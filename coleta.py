#!/usr/bin/env python3
"""Coleta de itens do Wowhead usando os parsers canônicos do projeto.

Este módulo é a **fronteira de rede** do fluxo "Sem LLM": ele baixa o HTML com
`AsyncWebCrawler` (Crawl4AI 0.8.x) e aplica os parsers de `wow_season2.py`
(`parse_links_itens`, `parse_item_unico`, `extrair_detalhes_item`,
`finalizar_item_bilingue`).

Decisão de arquitetura: NÃO criamos um schema JSON-CSS novo. O parâmetro
`css_selectors` de `JsonCssExtractionStrategy` foi removido na API 0.8.6 e é a
causa do `TypeError` que zerava o resultado. Aqui usamos apenas
`AsyncWebCrawler.arun(url=..., config=...)`, **sem** `extraction_strategy`.

PKG-3 (robustez de renderização JS / anti-bot):

- **JS-01**: `wait_for` usa condições `js:` (`.listview-row` ou `tr[data-id]`
  na listagem; `h1.heading-size-1` no detalhe) em vez de seletores CSS frágeis.
  O timeout da espera vem de `CRAWL4AI_WAIT_TIMEOUT` (default 15000 ms) e é
  aplicado no parâmetro `wait_for_timeout` de `CrawlerRunConfig` (0.8.6).
- **JS-02**: o script de lazy-load dispara `mouseover` nas 20 primeiras linhas
  para forçar os tooltips (protegido por `typeof document` + `try/catch`).
- **JS-03**: falha no primeiro crawl dispara um segundo passe com scroll
  forçado (`JS_RETRY_SCROLL`) registrado em `estatisticas_coleta()`.
- **F-04**: `user_agent`/`viewport` realistas (configuráveis por env).

Uso:
    from coleta import extrair_itens_de_url
    itens = await extrair_itens_de_url(url, categoria="ferramentas")
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

from wow_season2 import (
    extrair_detalhes_item,
    finalizar_item_bilingue,
    parse_item_unico,
    parse_links_itens,
)

logger = logging.getLogger("coleta")

# =============================================================================
# Defaults configuráveis por ambiente (sempre com fallback seguro/offline)
# =============================================================================

#: User-Agent de navegador real (sobrescrevível por `CRAWL4AI_USER_AGENT`).
USER_AGENT_PADRAO = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

VIEWPORT_LARGURA_PADRAO = 1920
VIEWPORT_ALTURA_PADRAO = 1080

#: Timeout da condição de `wait_for` (Crawl4AI: `wait_for_timeout`), em ms.
WAIT_TIMEOUT_PADRAO = 15000

#: Timeout total da página (Crawl4AI: `page_timeout`), em ms.
PAGE_TIMEOUT_PADRAO = 60000

#: Marcadores textuais da página de desafio anti-bot (Cloudflare/Wowhead).
_CHALLENGE_HTML_RE = re.compile(
    r"confirmar que voc[êe] é humano|verifying you are human|"
    r"checking your browser|just a moment\.\.\.|cf-challenge|challenge-platform",
    re.IGNORECASE,
)


def env_int(nome: str, padrao: int) -> int:
    """Lê um inteiro positivo do ambiente; qualquer valor inválido -> `padrao`."""
    bruto = os.getenv(nome)
    if bruto is None or not str(bruto).strip():
        return padrao
    try:
        valor = int(str(bruto).strip())
    except (TypeError, ValueError):
        logger.debug("env %s inválido (%r); usando default %s", nome, bruto, padrao)
        return padrao
    return valor if valor > 0 else padrao


def user_agent_configurado() -> str:
    """User-Agent efetivo (`CRAWL4AI_USER_AGENT` com fallback navegador real)."""
    valor = (os.getenv("CRAWL4AI_USER_AGENT") or "").strip()
    return valor or USER_AGENT_PADRAO


def pagina_de_desafio(html: str) -> bool:
    """Detecta a página de desafio anti-bot (não é conteúdo de item)."""
    return bool(_CHALLENGE_HTML_RE.search((html or "")[:30000]))


# =============================================================================
# JavaScript de pré-extração
# =============================================================================

#: Rolagem leve para forçar lazy-loading de tooltips/listas (best-effort).
#: JS-02: após o scroll, dispara `mouseover` nas 20 primeiras linhas para
#: forçar a criação dos tooltips. Todo o bloco é protegido por
#: `typeof document !== 'undefined'` e `try/catch` — nunca lança no browser.
_JS_LAZY_LOAD = """
(async () => {
  try {
    if (typeof document !== 'undefined') {
      const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
      for (let i = 0; i < 4; i++) {
        window.scrollTo(0, document.body.scrollHeight);
        await sleep(500);
      }
      window.scrollTo(0, 0);
      await sleep(300);
      var rows = document.querySelectorAll('.listview-row');
      for (var idx = 0; idx < Math.min(rows.length, 20); idx++) {
        rows[idx].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
      }
    }
    return true;
  } catch (erro) {
    return false;
  }
})();
"""

#: Segundo passe (JS-03): scroll forçado até o fim, espera e volta ao topo.
_JS_RETRY_SCROLL = """
(async () => {
  try {
    if (typeof document === 'undefined') { return false; }
    window.scrollTo(0, document.body.scrollHeight);
    await new Promise((r) => setTimeout(r, 2000));
    window.scrollTo(0, 0);
    return true;
  } catch (erro) {
    return false;
  }
})();
"""

#: Alias público (usado por `scraper_season2`).
JS_RETRY_SCROLL = _JS_RETRY_SCROLL

#: Alias público do lazy-load canônico (fonte única usada por
#: `scraper_season2`), garantindo o bloco `mouseover` (JS-02) em todo o fluxo.
JS_LAZY_LOAD = _JS_LAZY_LOAD

#: Condição de espera para listagens: `.listview-row` (layouts antigos) ou
#: `tr[data-id]` (DOM atual do Wowhead) — F-01.
_WAIT_LISTAGEM = (
    "js:() => (document.querySelectorAll('.listview-row').length > 0"
    " || document.querySelectorAll('tr[data-id]').length > 5)"
)

#: Condição de espera para páginas de item (detalhe).
_WAIT_DETALHE = "js:() => !!document.querySelector('h1.heading-size-1')"

#: Estatísticas do último/últimos crawls (alimenta `metadata` no scraper).
_ESTATISTICAS: Dict[str, Any] = {
    "tentativas_wait": 0,
    "retry_scroll_usado": False,
}


def resetar_estatisticas() -> None:
    """Zera os contadores de tentativas (útil entre execuções/testes)."""
    _ESTATISTICAS["tentativas_wait"] = 0
    _ESTATISTICAS["retry_scroll_usado"] = False


def estatisticas_coleta() -> Dict[str, Any]:
    """Cópia das estatísticas de `wait_for`/retry registradas até agora."""
    return dict(_ESTATISTICAS)


def eh_url_de_detalhe(url: str) -> bool:
    """`True` quando a URL aponta para um item individual (`item=123`)."""
    return bool(re.search(r"item=\d+", url or ""))


def wait_for_padrao(url: str = "") -> str:
    """Condição `js:` de `wait_for` adequada à URL (detalhe vs. listagem)."""
    return _WAIT_DETALHE if eh_url_de_detalhe(url) else _WAIT_LISTAGEM


# =============================================================================
# Configurações do Crawl4AI
# =============================================================================


def _browser_config() -> BrowserConfig:
    """BrowserConfig com UA/viewport realistas e tolerante a versões antigas."""
    largura = env_int("CRAWL4AI_VIEWPORT_WIDTH", VIEWPORT_LARGURA_PADRAO)
    altura = env_int("CRAWL4AI_VIEWPORT_HEIGHT", VIEWPORT_ALTURA_PADRAO)
    kwargs: Dict[str, Any] = {
        "headless": os.getenv("CRAWL4AI_BROWSER_HEADLESS", "true").lower()
        == "true",
        "enable_stealth": os.getenv("CRAWL4AI_MAGIC_MODE", "true").lower()
        == "true",
        "verbose": False,
        "browser_type": "chromium",
        "user_agent": user_agent_configurado(),
        # API 0.8.6: `viewport` (dict) sobrescreve viewport_width/height.
        "viewport": {"width": largura, "height": altura},
        "viewport_width": largura,
        "viewport_height": altura,
    }
    # Degradação progressiva para versões que não aceitam algum campo.
    for campo in ("enable_stealth", "viewport", "user_agent"):
        try:
            return BrowserConfig(**kwargs)
        except TypeError:
            kwargs.pop(campo, None)
    return BrowserConfig(**kwargs)


def _run_config(
    url: str = "",
    wait_for: str = "",
    js_code: Optional[str] = None,
) -> CrawlerRunConfig:
    """CrawlerRunConfig sem estratégia de extração (HTML cru).

    Args:
        url: endereço alvo; define a condição `js:` padrão de `wait_for`.
        wait_for: condição explícita (sobrescreve a derivada da URL).
        js_code: script extra executado junto do lazy-load (ex.: retry scroll).

    A API 0.8.6 expõe `wait_for_timeout` (timeout específico da condição de
    espera), usado aqui com `CRAWL4AI_WAIT_TIMEOUT`; `page_timeout` continua
    controlado por `CRAWL4AI_PAGE_TIMEOUT` (sem regressão).
    """
    condicao = wait_for or wait_for_padrao(url)
    kwargs: Dict[str, Any] = {
        "cache_mode": CacheMode.BYPASS,
        "wait_for": condicao,
        "wait_for_timeout": env_int(
            "CRAWL4AI_WAIT_TIMEOUT", WAIT_TIMEOUT_PADRAO
        ),
        "page_timeout": env_int("CRAWL4AI_PAGE_TIMEOUT", PAGE_TIMEOUT_PADRAO),
        "verbose": False,
        "user_agent": user_agent_configurado(),
    }

    scripts: List[str] = []
    if os.getenv("CRAWL4AI_JS_LAZY_LOAD", "true").lower() == "true":
        scripts.append(_JS_LAZY_LOAD)
    if js_code:
        scripts.append(js_code)
    if scripts:
        kwargs["js_code"] = scripts

    # Degradação progressiva para versões sem algum dos campos.
    for campo in ("wait_for_timeout", "js_code", "user_agent"):
        try:
            return CrawlerRunConfig(**kwargs)
        except TypeError:
            kwargs.pop(campo, None)
    return CrawlerRunConfig(**kwargs)


# =============================================================================
# Parsers (puro, sem rede)
# =============================================================================


def itens_de_html(
    url: str, html: str, categoria: str = ""
) -> List[Dict[str, Any]]:
    """Aplica os parsers canônicos a um HTML já baixado (puro, sem rede).

    - URL de item (`item=123`) -> `parse_item_unico` + `extrair_detalhes_item`.
    - Listagem/guia -> `parse_links_itens` (fallback: `parse_item_unico`).
    - Cada bruto é finalizado por `finalizar_item_bilingue`.
    """
    html = html or ""
    eh_item = eh_url_de_detalhe(url)

    brutos: List[Dict[str, Any]] = []
    if eh_item:
        unico = parse_item_unico(html, url)
        if unico:
            unico = extrair_detalhes_item(html, unico)
            brutos = [unico]
        else:
            brutos = parse_links_itens(html, url)
    else:
        brutos = parse_links_itens(html, url)
        if not brutos:
            unico = parse_item_unico(html, url)
            if unico:
                brutos = [unico]

    itens: List[Dict[str, Any]] = []
    for bruto in brutos:
        atual = dict(bruto)
        atual.setdefault("_categoria", categoria)
        atual["_pagina"] = url
        if not atual.get("url"):
            atual["url"] = url
        itens.append(finalizar_item_bilingue(atual))
    return itens


# =============================================================================
# Rede
# =============================================================================


async def _coletar_com_crawler(
    crawler: Any, url: str, categoria: str
) -> List[Dict[str, Any]]:
    """Baixa `url` (com segundo passe + scroll forçado) e devolve os itens."""
    resultado: Any = None
    erro: Optional[str] = None

    # JS-03: primeiro passe normal; segundo passe com scroll forçado.
    for tentativa in range(2):
        _ESTATISTICAS["tentativas_wait"] = (
            int(_ESTATISTICAS.get("tentativas_wait") or 0) + 1
        )
        if tentativa == 0:
            config = _run_config(url)
        else:
            _ESTATISTICAS["retry_scroll_usado"] = True
            logger.debug("retry com scroll forçado para %s", url)
            config = _run_config(url, js_code=_JS_RETRY_SCROLL)

        try:
            resultado = await crawler.arun(url=url, config=config)
        except Exception as exc:  # noqa: BLE001 - retry cobre falha de rede
            resultado = None
            erro = f"exceção: {exc}"
            logger.debug("crawl falhou (tentativa %s): %s", tentativa + 1, exc)
            continue

        if getattr(resultado, "success", False):
            erro = None
            break
        erro = getattr(resultado, "error_message", "") or "falha desconhecida"

    if resultado is None or not getattr(resultado, "success", False):
        raise RuntimeError(f"crawl falhou para {url}: {erro or 'falha desconhecida'}")

    html = getattr(resultado, "html", "") or ""
    return itens_de_html(url, html, categoria)


async def extrair_itens_de_url(
    url: str,
    categoria: str = "",
    crawler: Any = None,
) -> List[Dict[str, Any]]:
    """Extrai itens de uma URL do Wowhead usando os parsers canônicos.

    Args:
        url: listagem/guia ou página individual (`/item=123`).
        categoria: rótulo repassado ao parser (ex.: "ferramentas", "missivas").
        crawler: `AsyncWebCrawler` já aberto (reuso pelo adapter). Se `None`,
            abre um contexto próprio e fecha ao final.

    Returns:
        Lista de dicionários finalizados por `finalizar_item_bilingue`.
    """
    if crawler is not None:
        return await _coletar_com_crawler(crawler, url, categoria)

    async with AsyncWebCrawler(config=_browser_config()) as proprio:
        return await _coletar_com_crawler(proprio, url, categoria)
