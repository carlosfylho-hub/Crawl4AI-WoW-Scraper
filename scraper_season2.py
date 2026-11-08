#!/usr/bin/env python3
"""
Pipeline Crawl4AI da Season 2 (Midnight).

- Usa `AsyncWebCrawler` com execução de JavaScript pré-extração (`js_code`)
  para lazy-loading de tooltips / rolagem infinita.
- Configura `wait_for` explícito para os seletores das listas de itens.
- Associa `result.media["images"]` às linhas de itens (ícones).
- Enriquece cada item em página individual (atributos, efeitos, slot, ícone).
"""

from __future__ import annotations

import asyncio
import glob
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# F-09: garante stdout/stderr em UTF-8 no console do Windows antes dos
# imports pesados (crawl4ai/playwright).
import runtime as _runtime  # noqa: F401

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig

from coleta import (
    JS_LAZY_LOAD,
    JS_RETRY_SCROLL,
    USER_AGENT_PADRAO,
    VIEWPORT_ALTURA_PADRAO,
    VIEWPORT_LARGURA_PADRAO,
    WAIT_TIMEOUT_PADRAO,
    env_int,
    pagina_de_desafio,
    user_agent_configurado,
    wait_for_padrao,
)
from markdown_season2 import salvar_markdown
from tooltip_client import consultar_tooltip
from wow_season2 import (
    ILVL_ABSOLUTO_MIN,
    ILVL_PISO_PADRAO,
    ILVL_TETO_PADRAO,
    QUALIDADE_MINIMA_PADRAO,
    associar_icones_media,
    chave_variacao,
    extrair_detalhes_item,
    extrair_slot,
    extrair_subtipo,
    extrair_tipo_armadura,
    finalizar_item_bilingue,
    parse_item_unico,
    parse_links_itens,
    profissao_por_receita,
)

try:
    from config import (
        QUALIDADE_MINIMA_GEAR_PADRAO,
        SEASON2_ITEM_URLS,
        TRACKS_SEASON2,
        normalizar_url_gear,
        urls_craft_canonicas,
        urls_gear_canonicas,
    )
except ImportError:  # pragma: no cover - fallback quando rodando isolado
    SEASON2_ITEM_URLS = [
        "https://www.wowhead.com/pt/items/min-ilvl:305/max-ilvl:350"
    ]
    # F-01: espelho do `config.TRACKS_SEASON2` (fonte única: config.py).
    TRACKS_SEASON2 = (12846, 12854, 12856, 13440)
    QUALIDADE_MINIMA_GEAR_PADRAO = 4

    def normalizar_url_gear(url: str) -> List[str]:
        return [url]

    def urls_gear_canonicas(
        limite: Optional[int] = None, bonus: str = "12856"
    ) -> List[str]:
        return []

    def urls_craft_canonicas(
        limite: Optional[int] = None, bonus: str = "12856"
    ) -> List[str]:
        return []


logger = logging.getLogger("scraper_season2")


# =============================================================================
# Retenção de artefatos timestamped (F-11)
# =============================================================================

#: Quantidade padrão de artefatos timestamped mantidos por padrão de glob.
ARTEFATOS_MANTER_PADRAO = 5

#: Arquivos canônicos: nunca são removidos pela rotação, mesmo que casem
#: com um padrão de glob por acidente.
ARQUIVOS_CANONICOS = frozenset(
    {
        "wowhead_itens_season2.json",
        "wowhead_catalogo.json",
        "wowhead_catalogo.md",
        "wowhead_gemas.json",
        "wowhead_encantamentos.json",
        "wowhead_missivas.json",
        "wowhead_season2.md",
    }
)


def _rotacionar_artefatos(padrao: str, manter: int = ARTEFATOS_MANTER_PADRAO) -> List[str]:
    """Remove artefatos timestamped antigos, mantendo os ``manter`` mais novos.

    Parâmetros
    ----------
    padrao:
        Glob relativo (ex.: ``"*_sem_llm_*.json"``) — resolvido dentro de
        ``data/`` — ou glob completo com diretório/absoluto.
    manter:
        Quantidade de arquivos mais recentes preservados. Valores negativos
        são tratados como ``0`` (remove todos os que casarem com o padrão).

    Regras
    ------
    - Só remove arquivos que casem com o padrão **e** excedam ``manter``.
    - Nunca remove arquivos canônicos (ver :data:`ARQUIVOS_CANONICOS`).
    - Falhas de remoção (arquivo em uso/permissão) são ignoradas para não
      derrubar a execução do scraper.

    Retorno
    -------
    Lista dos caminhos efetivamente removidos (ordem: do mais antigo para o
    mais novo), útil para log e testes.
    """

    manter = max(0, int(manter))
    tem_diretorio = os.path.dirname(padrao) != ""
    caminho_padrao = padrao if tem_diretorio else os.path.join("data", padrao)

    arquivos = [
        caminho
        for caminho in glob.glob(caminho_padrao)
        if os.path.isfile(caminho)
        and os.path.basename(caminho) not in ARQUIVOS_CANONICOS
    ]
    arquivos.sort(key=os.path.getmtime, reverse=True)

    removidos: List[str] = []
    for antigo in reversed(arquivos[manter:]):
        try:
            os.remove(antigo)
            removidos.append(antigo)
        except OSError:
            continue
    return removidos


#: Alias público para reutilização por outros módulos (ex.: `scraper_sem_llm`).
rotacionar_artefatos = _rotacionar_artefatos


# =============================================================================
# JS de pré-extração (lazy-load / infinite scroll)
# =============================================================================
# JS-02: fonte única é `coleta._JS_LAZY_LOAD` (exportada como `JS_LAZY_LOAD`),
# que inclui o disparo de `mouseover` nas 20 primeiras linhas, o guard
# `typeof document` e `try/catch`. Não duplicar o script aqui.


def _pagina_desafio(html: str) -> bool:
    """Detecta a página de desafio anti-bot (não é conteúdo de item)."""
    return pagina_de_desafio(html)


# =============================================================================
# Circuit breaker anti-bot (F-04)
# =============================================================================


class CircuitBreakerAntiBot:
    """Contador de falhas 403/desafio consecutivas com pausa e aborto.

    Regras (PKG-3 / F-04):

    - cada falha 403/desafio incrementa `falhas_consecutivas`;
    - ao atingir `limite_falhas` (default 5) o breaker **abre** (`abortado`):
      a próxima chamada NÃO executa crawl, aplica a pausa de
      `pausa_segundos` (default 60s) uma única vez e registra o motivo;
    - um sucesso (`registrar_sucesso`) zera o contador e fecha o breaker.
    """

    LIMITE_FALHAS_PADRAO = 5
    PAUSA_SEGUNDOS_PADRAO = 60.0

    def __init__(
        self,
        limite_falhas: int = LIMITE_FALHAS_PADRAO,
        pausa_segundos: float = PAUSA_SEGUNDOS_PADRAO,
    ):
        self.limite_falhas = max(1, int(limite_falhas or 1))
        self.pausa_segundos = float(pausa_segundos or 0.0)
        self.falhas_consecutivas = 0
        self.abortado = False
        self.pausa_realizada = False
        self.pausas = 0
        self.motivo = ""

    def registrar_sucesso(self) -> None:
        """Zera falhas consecutivas e fecha o breaker."""
        self.falhas_consecutivas = 0
        self.abortado = False
        self.pausa_realizada = False
        self.motivo = ""

    def registrar_falha(self) -> str:
        """Contabiliza falha 403/desafio; devolve `continuar` ou `abortar`."""
        self.falhas_consecutivas += 1
        if self.falhas_consecutivas >= self.limite_falhas:
            self.abortado = True
            self.motivo = (
                f"{self.falhas_consecutivas} falhas consecutivas de "
                "403/desafio anti-bot"
            )
            return "abortar"
        return "continuar"

    def deve_bloquear(self) -> bool:
        """`True` quando o breaker está aberto (crawl deve ser pulado)."""
        return self.abortado

    def marcar_pausa(self) -> None:
        """Registra que a pausa de `pausa_segundos` foi aplicada."""
        self.pausa_realizada = True
        self.pausas += 1

    def resumo(self) -> Dict[str, Any]:
        """Resumo serializável para `metadata`."""
        return {
            "falhas_consecutivas": self.falhas_consecutivas,
            "limite": self.limite_falhas,
            "pausa_segundos": self.pausa_segundos,
            "pausas": self.pausas,
            "pausa_realizada": self.pausa_realizada,
            "abortado": self.abortado,
            "motivo": self.motivo,
        }


# =============================================================================
# Mapeamento de profissão a partir da URL
# =============================================================================

_PROFISSAO_POR_CHAVE = {
    "alchemy": "Alquimia",
    "blacksmithing": "Ferraria",
    "cooking": "Culinária",
    "enchanting": "Encantamento",
    "engineering": "Engenharia",
    "fishing": "Pesca",
    "herbalism": "Herborismo",
    "inscription": "Escrivania",
    "jewelcrafting": "Joalheria",
    "leatherworking": "Couraria",
    "mining": "Mineração",
    "skinning": "Esfolamento",
    "tailoring": "Alfaiataria",
}


def profissao_de_url(url: str) -> str:
    """Descobre a profissão de uma URL de guia do Wowhead (ou vazio)."""
    alvo = (url or "").lower()
    for chave, valor in _PROFISSAO_POR_CHAVE.items():
        if chave in alvo:
            return valor
    return ""


class WowheadSeason2Scraper:
    """Scraper da Season 2 com extração completa (texto + atributos + ícones)."""

    def __init__(
        self,
        ilvl_min: int = ILVL_PISO_PADRAO,
        ilvl_max: int = ILVL_TETO_PADRAO,
        qualidade_min: int = QUALIDADE_MINIMA_GEAR_PADRAO,
        qualidade_craft_min: int = 5,
        exigir_craft: bool = False,
        buscar_detalhes: bool = True,
        buscar_ingles: bool = True,
        gerar_markdown: bool = True,
        caminho_md: str = "",
        max_itens: int = 200,
        max_detalhes: Optional[int] = None,
        incluir_sem_ilvl: bool = False,
        slots_permitidos: Optional[List[str]] = None,
        profissoes_permitidas: Optional[List[str]] = None,
        wait_for: str = "",
        headless: bool = True,
        magic_mode: bool = True,
        js_lazy_load: bool = True,
        delay_before_html: float = 1.0,
        page_timeout: int = 60000,
        wait_for_timeout: int = WAIT_TIMEOUT_PADRAO,
        tentativas_crawl: int = 3,
        esperas_retry: Tuple[float, ...] = (2.0, 4.0, 8.0),
        limite_falhas_consecutivas: int = 5,
        pausa_circuit_breaker: float = 60.0,
        sleep: Any = None,
        progress_callback: Any = None,
    ):
        self.ilvl_min = ILVL_ABSOLUTO_MIN if ilvl_min is None else int(ilvl_min)
        self.ilvl_max = ILVL_TETO_PADRAO if ilvl_max is None else int(ilvl_max)
        self.qualidade_min = int(qualidade_min or 0)
        self.qualidade_craft_min = int(qualidade_craft_min or 0)
        # P-13: quando ligado, só aceita itens craftados no rank pedido
        # (R5 por padrão). `qualidade_craft=0` (não craftado) é descartado.
        self.exigir_craft = bool(exigir_craft)
        self.buscar_detalhes = bool(buscar_detalhes)
        self.buscar_ingles = bool(buscar_ingles)
        self.gerar_markdown = bool(gerar_markdown)
        self.caminho_md = caminho_md or os.path.join("data", "wowhead_season2.md")
        self.max_itens = max(1, int(max_itens or 200))
        # Semântica: None = todos; 0 = nenhum; N > 0 = N primeiros.
        self.max_detalhes = (
            None if max_detalhes is None else max(0, int(max_detalhes))
        )
        self.incluir_sem_ilvl = bool(incluir_sem_ilvl)
        self.slots_permitidos = [s for s in (slots_permitidos or []) if s]
        self.profissoes_permitidas = [p for p in (profissoes_permitidas or []) if p]
        # Vazio => condição derivada da URL (detalhe vs. listagem), ver
        # `wait_for_padrao()` em `coleta.py` (JS-01).
        self.wait_for = wait_for or ""
        self.js_lazy_load = bool(js_lazy_load)
        self.delay_before_html = float(delay_before_html or 0.0)
        self.page_timeout = int(page_timeout or 60000)
        self.wait_for_timeout = int(wait_for_timeout or WAIT_TIMEOUT_PADRAO)
        self.tentativas_crawl = max(1, int(tentativas_crawl or 1))
        self.esperas_retry: Tuple[float, ...] = tuple(
            float(v) for v in (esperas_retry or ())
        ) or (2.0, 4.0, 8.0)
        self._sleep = sleep or asyncio.sleep
        self.circuito = CircuitBreakerAntiBot(
            limite_falhas=limite_falhas_consecutivas,
            pausa_segundos=pausa_circuit_breaker,
        )
        # Estatísticas de retry/circuit breaker expostas em `metadata`.
        self._tentativas_wait = 0
        self._retry_scroll_usado = False
        self._falhas_circuito: List[Dict[str, str]] = []
        self._circuito_registrado: set = set()
        self.progress_callback = progress_callback
        self.base_url = os.getenv("WOWHEAD_BASE_URL", "https://www.wowhead.com")

        largura = env_int("CRAWL4AI_VIEWPORT_WIDTH", VIEWPORT_LARGURA_PADRAO)
        altura = env_int("CRAWL4AI_VIEWPORT_HEIGHT", VIEWPORT_ALTURA_PADRAO)
        kwargs_browser: Dict[str, Any] = {
            "headless": headless,
            "enable_stealth": magic_mode,
            "verbose": False,
            "browser_type": "chromium",
            "user_agent": user_agent_configurado(),
            # API 0.8.6: `viewport` (dict) sobrescreve viewport_width/height.
            "viewport": {"width": largura, "height": altura},
            "viewport_width": largura,
            "viewport_height": altura,
        }
        for campo in ("enable_stealth", "viewport", "user_agent"):
            try:
                self.browser_config = BrowserConfig(**kwargs_browser)
                break
            except TypeError:  # versões sem algum dos campos
                kwargs_browser.pop(campo, None)
        else:
            self.browser_config = BrowserConfig(**kwargs_browser)

        self.crawler = AsyncWebCrawler(config=self.browser_config)

    # ------------------------------------------------------------------ utils
    def _update_progress(
        self, message: str, current: Optional[int] = None, total: Optional[int] = None
    ) -> None:
        if self.progress_callback:
            try:
                self.progress_callback(message, current, total)
            except TypeError:
                self.progress_callback(message)

    async def __aenter__(self) -> "WowheadSeason2Scraper":
        await self.crawler.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.crawler.__aexit__(exc_type, exc_val, exc_tb)

    def _run_config(
        self,
        wait_for: Optional[str] = None,
        url: str = "",
        js_code: Optional[str] = None,
    ) -> CrawlerRunConfig:
        """CrawlerRunConfig com `wait_for` JS por tipo de página (JS-01).

        `wait_for` explícito tem precedência; caso contrário a condição é
        derivada da URL (`h1.heading-size-1` no detalhe, `.listview-row` /
        `tr[data-id]` na listagem). O timeout da condição vem de
        `CRAWL4AI_WAIT_TIMEOUT` (Crawl4AI 0.8.6: `wait_for_timeout`).
        """
        condicao = wait_for or self.wait_for or wait_for_padrao(url)
        kwargs: Dict[str, Any] = {
            "cache_mode": CacheMode.BYPASS,
            "wait_for": condicao,
            "wait_for_timeout": self.wait_for_timeout,
            "delay_before_return_html": self.delay_before_html,
            "page_timeout": self.page_timeout,
            "verbose": False,
            "user_agent": user_agent_configurado(),
        }

        scripts: List[str] = []
        if self.js_lazy_load:
            scripts.append(JS_LAZY_LOAD)
        if js_code:
            scripts.append(js_code)
        if scripts:
            kwargs["js_code"] = scripts

        for campo in (
            "wait_for_timeout",
            "delay_before_return_html",
            "js_code",
            "user_agent",
        ):
            try:
                return CrawlerRunConfig(**kwargs)
            except TypeError:
                kwargs.pop(campo, None)
        return CrawlerRunConfig(**kwargs)

    @staticmethod
    def _media_images(result: Any) -> List[Dict[str, Any]]:
        media = getattr(result, "media", None)
        if isinstance(media, dict):
            imagens = media.get("images") or []
            return [i for i in imagens if isinstance(i, dict)]
        return []

    @staticmethod
    def _tem_indicio_craft(item: Dict[str, Any]) -> bool:
        """Heurística de craft **antes** de visitar a página.

        Emite `crafting-quality` apenas quando há indício de craft:
        categoria/profissão de craft, `profissao_craft` já resolvida,
        `craft_indicio` de etapa anterior ou ID conhecido no mapa
        receita→profissão. Gear de drop (M+/raid) fica sem a marca, evitando
        `motivo_qualidade_craft = "ignorado:sem_profissao (url:crafting-quality)"`
        em massa.
        """
        if item.get("_profissao_url") or item.get("profissao_craft"):
            return True
        if item.get("_profissao_craft") or item.get("craft_indicio"):
            return True

        categoria = str(item.get("_categoria") or "").lower()
        if any(chave in categoria for chave in ("profiss", "craft")):
            return True

        return bool(profissao_por_receita(item.get("id")))

    def _url_detalhe(self, item: Dict[str, Any], locale: str = "ptbr") -> str:
        """Monta a URL da página individual no locale pedido (ptbr/en)."""
        ident = item.get("id")
        prefixo = "/pt" if locale == "ptbr" else ""
        url = f"{self.base_url}{prefixo}/item={ident}"

        params: List[str] = []
        # O ilvl NÃO é emitido: a URL canônica deriva o ilvl do bônus.
        bonus = item.get("bonus_ids") or []
        if bonus:
            params.append("bonus=" + ":".join(str(b) for b in bonus))
        categoria = str(item.get("_categoria") or "").lower()
        is_catalogo = any(
            chave in categoria
            for chave in ("gema", "encantamento", "missiva", "consum", "reagente")
        )
        if (
            self.qualidade_craft_min
            and not is_catalogo
            and self._tem_indicio_craft(item)
        ):
            params.append(f"crafting-quality={self.qualidade_craft_min}")
        if params:
            url += "?" + "&".join(params)
        return url

    def _base_locale(self, item: Dict[str, Any], locale: str) -> Dict[str, Any]:
        """
        Prepara o bruto para o locale. Se a listagem veio no outro idioma,
        limpa nome/contexto para não misturar localizações.
        """
        base = dict(item)
        pagina = str(item.get("_pagina") or item.get("url") or "")
        listagem_ptbr = "/pt/" in pagina
        if listagem_ptbr != (locale == "ptbr"):
            base["_contexto"] = ""
            base["nome"] = ""
        return base

    @staticmethod
    def _classificar_falha(result: Any) -> str:
        """Classifica a falha de um `arun`: `403`, `desafio`, `excecao`, `falha`."""
        if result is None:
            return "excecao"
        codigo = getattr(result, "status_code", 0) or 0
        erro = str(getattr(result, "error_message", "") or "")
        if codigo == 403 or "403" in erro or "forbidden" in erro.lower():
            return "403"
        if _pagina_desafio(getattr(result, "html", "") or ""):
            return "desafio"
        return "falha"

    def _registrar_falha_circuito(self, url: str, motivo: str) -> None:
        """Registra (uma única vez) a URL abortada pelo circuit breaker."""
        chave = f"{url}|{motivo}"
        if chave in self._circuito_registrado:
            return
        self._circuito_registrado.add(chave)
        self._falhas_circuito.append(
            {"url": url, "erro": f"circuit breaker anti-bot: {motivo}"}
        )

    async def _crawl_locale(
        self, item: Dict[str, Any], locale: str
    ) -> Tuple[str, str, List[Dict[str, Any]]]:
        """Baixa a página do item no locale pedido, com retry anti-bot.

        Backoff exponencial (default 2s/4s/8s) e circuit breaker: após 5
        falhas 403/desafio consecutivas a próxima chamada **não** executa
        crawl, aplica a pausa de 60s (uma vez) e registra o motivo.
        """
        url = self._url_detalhe(item, locale)
        breaker = self.circuito

        if breaker.deve_bloquear():
            if not breaker.pausa_realizada:
                logger.warning(
                    "circuit breaker: pausando %.1fs antes de prosseguir — %s",
                    breaker.pausa_segundos,
                    breaker.motivo,
                )
                await self._sleep(breaker.pausa_segundos)
                breaker.marcar_pausa()
            self._registrar_falha_circuito(url, breaker.motivo)
            return url, "", []

        for tentativa in range(self.tentativas_crawl):
            js_extra: Optional[str] = None
            if tentativa:
                espera = self.esperas_retry[
                    min(tentativa - 1, len(self.esperas_retry) - 1)
                ]
                logger.info(
                    "retry %s/%s em %.1fs para %s",
                    tentativa + 1,
                    self.tentativas_crawl,
                    espera,
                    url,
                )
                await self._sleep(espera)
                # JS-03: segundo passe com scroll forçado.
                js_extra = JS_RETRY_SCROLL
                self._retry_scroll_usado = True

            self._tentativas_wait += 1
            try:
                result = await self.crawler.arun(
                    url=url, config=self._run_config(url=url, js_code=js_extra)
                )
            except Exception as exc:  # noqa: BLE001 - retry cobre a exceção
                logger.debug("crawl de detalhe falhou (%s): %s", url, exc)
                result = None

            if result is not None and getattr(result, "success", False):
                html = getattr(result, "html", "") or ""
                if not _pagina_desafio(html):
                    breaker.registrar_sucesso()
                    return (url, html, self._media_images(result))

            tipo = self._classificar_falha(result)
            logger.debug("falha anti-bot (%s) em %s", tipo, url)
            if breaker.registrar_falha() == "abortar":
                logger.warning(
                    "circuit breaker aberto após %s falhas consecutivas",
                    breaker.falhas_consecutivas,
                )
                self._registrar_falha_circuito(url, breaker.motivo)
                return url, "", []

        return url, "", []

    # ------------------------------------------------------------- collection
    async def coletar_url(
        self, url: str, categoria: str = ""
    ) -> Tuple[List[Dict[str, Any]], Optional[Dict[str, str]]]:
        """Coleta os itens brutos de uma URL de listagem/guia/item."""
        breaker = self.circuito
        if breaker.deve_bloquear():
            if not breaker.pausa_realizada:
                logger.warning(
                    "circuit breaker: pausando %.1fs antes de prosseguir — %s",
                    breaker.pausa_segundos,
                    breaker.motivo,
                )
                await self._sleep(breaker.pausa_segundos)
                breaker.marcar_pausa()
            self._registrar_falha_circuito(url, breaker.motivo)
            return [], {
                "url": url,
                "erro": f"circuit breaker anti-bot: {breaker.motivo}",
            }

        self._tentativas_wait += 1
        try:
            result = await self.crawler.arun(
                url=url, config=self._run_config(url=url)
            )
        except Exception as exc:  # pragma: no cover - depende de rede
            breaker.registrar_falha()
            return [], {"url": url, "erro": f"exceção: {exc}"}

        if not getattr(result, "success", False):
            erro = getattr(result, "error_message", "") or "falha desconhecida"
            breaker.registrar_falha()
            return [], {"url": url, "erro": str(erro)}

        html = getattr(result, "html", "") or ""

        # Desafio anti-bot (Cloudflare): segundo passe com scroll forçado
        # (JS-03) e, se persistir, registra falha em vez de capturar nomes
        # falsos (nunca trava indefinidamente).
        if _pagina_desafio(html):
            logger.info("desafio anti-bot em %s; repetindo com scroll", url)
            await self._sleep(self.esperas_retry[0])
            self._retry_scroll_usado = True
            self._tentativas_wait += 1
            try:
                result = await self.crawler.arun(
                    url=url,
                    config=self._run_config(url=url, js_code=JS_RETRY_SCROLL),
                )
            except Exception as exc:  # pragma: no cover
                breaker.registrar_falha()
                return [], {"url": url, "erro": f"desafio anti-bot: {exc}"}
            if not getattr(result, "success", False) or _pagina_desafio(
                getattr(result, "html", "") or ""
            ):
                breaker.registrar_falha()
                return [], {"url": url, "erro": "desafio anti-bot (Cloudflare)"}
            html = getattr(result, "html", "") or ""

        breaker.registrar_sucesso()

        if re.search(r"item=\d+", url or ""):
            # Página individual de item: evita capturar "itens relacionados"
            unico = parse_item_unico(html, url)
            itens = [unico] if unico else parse_links_itens(html, url)
        else:
            itens = parse_links_itens(html, url)
            if not itens:
                unico = parse_item_unico(html, url)
                if unico:
                    itens = [unico]

        associar_icones_media(itens, self._media_images(result))

        for item in itens:
            item["_categoria"] = categoria
            item["_profissao_url"] = profissao_de_url(url)
            item["_pagina"] = url

        return itens, None

    def _consolidar_brutos(
        self, brutos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Deduplica itens brutos por (id, ilvl, Bonus IDs, stage), mantendo o
        melhor registro. Variações com Bonus IDs diferentes NÃO são colapsadas.
        """
        consolidados: Dict[str, Dict[str, Any]] = {}
        for item in brutos:
            ident = str(item.get("id") or "").strip()
            if not ident:
                continue
            ilvl = int(item.get("item_level") or 0)
            chave = chave_variacao(
                ident, ilvl, item.get("bonus_ids"), item.get("track_stage") or ""
            )
            atual = consolidados.get(chave)
            if atual is None:
                consolidados[chave] = item
                continue

            if len(item.get("_contexto") or "") > len(atual.get("_contexto") or ""):
                atual["_contexto"] = item["_contexto"]
            for campo in (
                "nome",
                "icone_url",
                "url",
                "_categoria",
                "_profissao_url",
                "_profissao_craft",
                "variante_fonte",
            ):
                if not atual.get(campo) and item.get(campo):
                    atual[campo] = item[campo]
            if item.get("qualidade") and not atual.get("qualidade"):
                atual["qualidade"] = item["qualidade"]
            if item.get("bonus_ids") and not atual.get("bonus_ids"):
                atual["bonus_ids"] = item["bonus_ids"]

        # Não filtrar qualidade aqui: itens de catálogo (missivas/gemas)
        # podem ter qualidade baixa e ainda são válidos. O filtro por tipo
        # é aplicado em _finalizar().
        return list(consolidados.values())

    # ------------------------------------------- seleção de variantes (F-01)
    @staticmethod
    def _selecao_variante_vazia() -> Dict[str, int]:
        """Contadores zerados de :meth:`_selecionar_melhores_variantes`."""
        return {"track_temporada": 0, "maior_ilvl": 0, "unica_sem_ilvl": 0}

    @staticmethod
    def _bonus_como_ints(item: Dict[str, Any]) -> List[int]:
        """Converte `bonus_ids` (str/int) em lista de ints, ignorando lixo."""
        numeros: List[int] = []
        for bruto in item.get("bonus_ids") or []:
            try:
                numeros.append(int(bruto))
            except (TypeError, ValueError):
                continue
        return numeros

    @classmethod
    def _tem_track(cls, item: Dict[str, Any], tracks: set) -> bool:
        """`True` quando algum `bonus_id` da variante é track da temporada."""
        if not tracks:
            return False
        return bool(set(cls._bonus_como_ints(item)) & tracks)

    @staticmethod
    def _melhor_por_ilvl(
        variantes: List[Tuple[int, Dict[str, Any]]]
    ) -> Tuple[int, Dict[str, Any]]:
        """Variante de maior `item_level` (empate: a primeira da listagem)."""
        melhor: Optional[Tuple[int, Dict[str, Any]]] = None
        for indice, item in variantes:
            if melhor is None or int(item.get("item_level") or 0) > int(
                melhor[1].get("item_level") or 0
            ):
                melhor = (indice, item)
        assert melhor is not None
        return melhor

    def _selecionar_melhores_variantes(
        self, itens: List[Dict[str, Any]], tracks: set
    ) -> List[Dict[str, Any]]:
        """Mantém **uma** variante por `item_id` antes do truncamento.

        A listagem do Wowhead devolve várias variantes do mesmo item (mesmo
        `item_id`, `bonus_ids`/`item_level` diferentes). Truncar por
        `max_itens` antes disso gastava as vagas nas variantes de track baixo
        do primeiro item (F-01).

        Prioridade dentro de cada grupo de `item_id`:
        1. variante cujo `bonus_ids` **intersecta** `tracks` (temporada);
        2. nenhuma com track -> variante de **maior** `item_level` conhecido;
        3. todas sem ilvl -> **apenas a primeira** (evita inflar o funil).

        A ordem original da listagem é preservada. As variantes com track
        descartadas ficam em ``item["_variantes_alternativas"]`` para o
        fallback de :meth:`_arbitrar_ilvl` (uma tentativa extra por item).
        """
        tracks_int = set()
        for track in tracks or ():
            try:
                tracks_int.add(int(track))
            except (TypeError, ValueError):
                continue

        grupos: Dict[str, List[Tuple[int, Dict[str, Any]]]] = {}
        ordem: List[str] = []
        for indice, item in enumerate(itens or []):
            chave = str(item.get("id") or "").strip()
            if not chave:
                continue
            if chave not in grupos:
                grupos[chave] = []
                ordem.append(chave)
            grupos[chave].append((indice, item))

        contagem = self._selecao_variante_vazia()
        escolhidos: List[Tuple[int, Dict[str, Any]]] = []
        for chave in ordem:
            variantes = grupos[chave]
            com_track = [
                (i, v) for i, v in variantes if self._tem_track(v, tracks_int)
            ]
            com_ilvl = [
                (i, v) for i, v in variantes if int(v.get("item_level") or 0) > 0
            ]
            if com_track:
                escolhido = self._melhor_por_ilvl(com_track)
                contagem["track_temporada"] += 1
            elif com_ilvl:
                escolhido = self._melhor_por_ilvl(com_ilvl)
                contagem["maior_ilvl"] += 1
            else:
                escolhido = variantes[0]
                contagem["unica_sem_ilvl"] += 1

            item_escolhido = escolhido[1]
            atuais = [str(b) for b in (item_escolhido.get("bonus_ids") or [])]
            alternativas: List[List[str]] = []
            vistos_alt = set()
            for _, variante in com_track:
                bonus = [str(b) for b in (variante.get("bonus_ids") or [])]
                chave_bonus = tuple(bonus)
                if not bonus or bonus == atuais or chave_bonus in vistos_alt:
                    continue
                vistos_alt.add(chave_bonus)
                alternativas.append(bonus)
            item_escolhido["_variantes_alternativas"] = alternativas
            # Ordem = primeira aparição do `item_id` na listagem original.
            escolhidos.append((variantes[0][0], item_escolhido))

        # Preserva a ordem original da listagem dos itens escolhidos.
        escolhidos.sort(key=lambda par: par[0])
        self._selecao_variante_contagem = contagem
        return [item for _, item in escolhidos]

    def _registrar_origem_ilvl(self, origem: str) -> None:
        contagem = getattr(self, "_ilvl_origem_contagem", None)
        if not isinstance(contagem, dict):
            contagem = {}
            self._ilvl_origem_contagem = contagem
        contagem[origem] = contagem.get(origem, 0) + 1

    def _ilvl_na_faixa(self, ilvl: int) -> bool:
        """`True` quando `ilvl` está dentro de `[ilvl_min, ilvl_max]`."""
        if not ilvl:
            return False
        if self.ilvl_min and ilvl < self.ilvl_min:
            return False
        if self.ilvl_max and ilvl > self.ilvl_max:
            return False
        return True

    def _tentar_variante_alternativa(
        self, item: Dict[str, Any]
    ) -> Optional[int]:
        """Uma única tentativa de tooltip em variante com track da temporada.

        As alternativas são gravadas por :meth:`_selecionar_melhores_variantes`
        em ``item["_variantes_alternativas"]``. Só a **primeira** é consultada
        (limite de 1 requisição extra por item). Devolve o ilvl encontrado ou
        `None`; nunca levanta exceção.
        """
        if item.get("_variante_alternativa_usada"):
            return None
        alternativas = item.get("_variantes_alternativas") or []
        if not alternativas:
            return None

        bonus = alternativas[0]
        try:
            tooltip = consultar_tooltip(item.get("id"), bonus)
        except Exception as exc:  # noqa: BLE001 - tooltip nunca derruba o item
            logger.debug("tooltip de variante alternativa falhou: %s", exc)
            return None
        if not tooltip:
            return None

        ilvl_alt = int(tooltip.get("item_level") or 0)
        if not self._ilvl_na_faixa(ilvl_alt):
            return None

        item["bonus_ids"] = [str(b) for b in bonus]
        item["variante_alternativa_usada"] = True
        item["_variante_alternativa_usada"] = True
        return ilvl_alt

    def _arbitrar_ilvl(
        self,
        item: Dict[str, Any],
        pt_bruto: Dict[str, Any],
        en_bruto: Dict[str, Any],
    ) -> str:
        """
        Arbitra o item level: tooltip > página > listagem.

        O tooltip só é consultado quando há conflito listagem×página ou
        quando o ilvl da página está fora de `[ilvl_min, ilvl_max]`.
        """
        ilvl_listagem = int(item.get("item_level") or 0)
        ilvl_pagina = int((pt_bruto or {}).get("item_level") or 0)
        if not ilvl_pagina:
            ilvl_pagina = int((en_bruto or {}).get("item_level") or 0)

        ilvl_final = ilvl_pagina or ilvl_listagem
        if ilvl_pagina:
            origem = "pagina"
        elif ilvl_listagem:
            origem = "listagem"
        else:
            origem = ""

        conflito = bool(
            ilvl_listagem and ilvl_pagina and ilvl_listagem != ilvl_pagina
        )
        fora_faixa = bool(
            ilvl_pagina
            and (
                (self.ilvl_min and ilvl_pagina < self.ilvl_min)
                or (self.ilvl_max and ilvl_pagina > self.ilvl_max)
            )
        )

        if conflito or fora_faixa:
            tooltip = consultar_tooltip(item.get("id"), item.get("bonus_ids"))
            if tooltip:
                ilvl_tooltip = int(tooltip.get("item_level") or 0)
                if ilvl_tooltip:
                    if ilvl_listagem and ilvl_tooltip != ilvl_listagem:
                        conflito = True
                    ilvl_final = ilvl_tooltip
                    origem = "tooltip"

        # F-01 (B): se o ilvl final ainda está fora da faixa, tenta UMA
        # variante alternativa do mesmo item com track da temporada antes de
        # deixar o item ser descartado em `_finalizar`.
        if ilvl_final and not self._ilvl_na_faixa(ilvl_final):
            ilvl_alt = self._tentar_variante_alternativa(item)
            if ilvl_alt:
                conflito = True
                ilvl_final = ilvl_alt
                origem = "tooltip"

        if ilvl_final:
            item["item_level"] = ilvl_final
            if isinstance(pt_bruto, dict):
                pt_bruto["item_level"] = ilvl_final
            if isinstance(en_bruto, dict):
                en_bruto["item_level"] = ilvl_final

        item["_ilvl_listagem"] = ilvl_listagem
        item["_ilvl_pagina"] = ilvl_pagina
        item["_ilvl_origem"] = origem
        item["_ilvl_conflito"] = conflito
        if origem:
            self._registrar_origem_ilvl(origem)
        return origem

    def enriquecer_por_tooltip(
        self, itens: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Enriquece itens usando o tooltip HTTP (F-05/P-03).

        Usado apenas quando não há detalhamento (`max_detalhes == 0` ou
        `buscar_detalhes=False`). Preenche **somente campos ausentes** e nunca
        levanta exceção: falhas são contabilizadas em ``self._tooltip_falhas``.

        Fonte declarada: ``nome_*_fonte``/``icone_fonte``/``atributos_fonte``
        recebem ``"tooltip_http"`` (escala em `FONTES_*`).
        """
        aplicados = 0
        falhas = 0

        for item in itens:
            ident = item.get("id")
            try:
                tooltip = consultar_tooltip(ident, item.get("bonus_ids") or [])
            except Exception as exc:  # noqa: BLE001 - nunca derruba o run
                logger.debug(
                    "tooltip de enriquecimento falhou item=%s: %s", ident, exc
                )
                tooltip = None

            if not tooltip:
                falhas += 1
                continue

            aplicados += 1
            texto = str(tooltip.get("tooltip_texto") or "")
            nome = str(
                tooltip.get("nome_ptbr") or tooltip.get("nome_en") or ""
            ).strip()

            if nome:
                if not str(item.get("nome") or "").strip():
                    item["nome"] = nome
                if not item.get("nome_ptbr"):
                    item["nome_ptbr"] = nome
                    item["_nome_ptbr_fonte"] = "tooltip_http"

            ilvl = int(tooltip.get("item_level") or 0)
            if ilvl and not int(item.get("item_level") or 0):
                item["item_level"] = ilvl
                item["_ilvl_origem"] = "tooltip"

            qualidade = int(tooltip.get("qualidade") or 0)
            if qualidade and not item.get("qualidade"):
                item["qualidade"] = qualidade

            icone = str(tooltip.get("icone_url") or "")
            if icone and not item.get("icone_url"):
                item["icone_url"] = icone
                item["_icone_fonte"] = "tooltip_http"

            primarios = tooltip.get("atributos_primarios") or {}
            secundarios = tooltip.get("atributos_secundarios") or {}
            if primarios and not item.get("atributos_primarios"):
                item["atributos_primarios"] = dict(primarios)
            if secundarios and not item.get("atributos_secundarios"):
                item["atributos_secundarios"] = dict(secundarios)
            if (primarios or secundarios) and not item.get("_atributos_fonte"):
                item["_atributos_fonte"] = "tooltip_http"

            if tooltip.get("track_rotulo") and not item.get("track"):
                item["track"] = tooltip["track_rotulo"]

            if texto:
                if not item.get("_contexto"):
                    item["_contexto"] = texto
                if not item.get("slot") or item.get("slot") == "N/A":
                    slot = extrair_slot(texto)
                    if slot and slot != "N/A":
                        item["slot"] = slot
                if (
                    not item.get("tipo_armadura")
                    or item.get("tipo_armadura") == "N/A"
                ):
                    tipo_armadura = extrair_tipo_armadura(texto)
                    if tipo_armadura and tipo_armadura != "N/A":
                        item["tipo_armadura"] = tipo_armadura
                if not item.get("subtipo"):
                    item["subtipo"] = extrair_subtipo(texto)

        self._tooltip_enriquecidos = aplicados
        self._tooltip_falhas = falhas
        logger.info(
            "enriquecimento por tooltip: %s aplicados, %s falhas",
            aplicados,
            falhas,
        )
        return itens

    async def detalhar_itens(
        self, itens: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Visita as páginas PT-BR e EN de cada item, extraindo nomes e atributos
        fiéis de cada localização (sem tradução automática).

        Depois do detalhamento, arbitra o item level (tooltip > página >
        listagem) e propaga a origem da variante para o dict final.
        """
        if not self.buscar_detalhes or not itens:
            for item in itens:
                item.setdefault(
                    "_variante_fonte", item.get("variante_fonte") or ""
                )
            return itens

        limite = (
            len(itens)
            if self.max_detalhes is None
            else min(len(itens), self.max_detalhes)
        )
        locais = ["ptbr"] + (["en"] if self.buscar_ingles else [])
        total = limite * len(locais)
        feitos = 0

        for i in range(limite):
            item = itens[i]
            rotulo = (item.get("nome") or str(item.get("id") or ""))[:50]

            url_pt, html_pt, media_pt = await self._crawl_locale(item, "ptbr")
            feitos += 1
            self._update_progress(
                f"Detalhando PT-BR {feitos}/{total}: {rotulo}", feitos, total
            )
            base_pt = self._base_locale(item, "ptbr")
            pt_bruto = (
                extrair_detalhes_item(html_pt, base_pt) if html_pt else base_pt
            )
            associar_icones_media([pt_bruto], media_pt)

            url_en = ""
            en_bruto: Dict[str, Any] = {}
            if self.buscar_ingles:
                url_en, html_en, media_en = await self._crawl_locale(item, "en")
                feitos += 1
                self._update_progress(
                    f"Detalhando EN {feitos}/{total}: {rotulo}", feitos, total
                )
                base_en = self._base_locale(item, "en")
                en_bruto = (
                    extrair_detalhes_item(html_en, base_en)
                    if html_en
                    else base_en
                )
                associar_icones_media([en_bruto], media_en)

            self._arbitrar_ilvl(item, pt_bruto, en_bruto)

            item["_pt"] = pt_bruto
            item["_en"] = en_bruto
            item["_variante_fonte"] = item.get("variante_fonte") or ""
            item["url"] = url_pt
            item["url_en"] = url_en
            itens[i] = item

        return itens

    # ------------------------------------------------------ pré-filtro ilvl
    @staticmethod
    def _descartes_vazios() -> Dict[str, int]:
        return {
            "ilvl_fora": 0,
            "ilvl_adiado": 0,
            "sem_ilvl": 0,
            "qualidade": 0,
            "slot": 0,
            "profissao": 0,
            "tipo": 0,
            "qualidade_craft": 0,
            "sem_craft": 0,
        }

    def _iniciar_descartes(self) -> None:
        self.descartes = self._descartes_vazios()
        self._ilvl_origem_contagem = {}
        # P-03: contadores do enriquecimento leve por tooltip HTTP.
        self._tooltip_enriquecidos = 0
        self._tooltip_falhas = 0

    def _prefiltrar(self, brutos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Descarte conservador por ilvl ANTES do detalhamento.

        Só descarta quando a variante é confiável: `variante_fonte ==
        "listagem"` E `bonus_ids` não vazio. Caso contrário, adia a decisão
        para depois do detalhamento (`descartes["ilvl_adiado"]`).
        """
        if not isinstance(getattr(self, "descartes", None), dict):
            self.descartes = self._descartes_vazios()

        mantidos: List[Dict[str, Any]] = []
        for item in brutos:
            ilvl = int(item.get("item_level") or 0)
            categoria = str(item.get("_categoria") or "").lower()
            is_catalogo = any(
                chave in categoria
                for chave in (
                    "gema",
                    "encantamento",
                    "missiva",
                    "consum",
                    "reagente",
                )
            )
            # Exceção de catálogo e itens sem ilvl: não decidir aqui.
            if is_catalogo or not ilvl:
                mantidos.append(item)
                continue

            confiavel = (
                str(item.get("variante_fonte") or "") == "listagem"
                and bool(item.get("bonus_ids"))
            )
            if not confiavel:
                self.descartes["ilvl_adiado"] += 1
                mantidos.append(item)
                continue

            if (self.ilvl_min and ilvl < self.ilvl_min) or (
                self.ilvl_max and ilvl > self.ilvl_max
            ):
                self.descartes["ilvl_fora"] += 1
                continue
            mantidos.append(item)
        return mantidos

    # ---------------------------------------------------------------- finalize
    def _finalizar(self, brutos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        vistos: Dict[str, Dict[str, Any]] = {}
        if not isinstance(getattr(self, "descartes", None), dict):
            self.descartes = self._descartes_vazios()
        for chave, valor in self._descartes_vazios().items():
            self.descartes.setdefault(chave, valor)

        for bruto in brutos:
            item = finalizar_item_bilingue(
                bruto,
                bruto.get("_pt"),
                bruto.get("_en"),
                bruto.get("url") or "",
                bruto.get("url_en") or "",
            )
            item["categoria"] = bruto.get("_categoria", "")
            item["profissao"] = bruto.get("_profissao_url", "")
            item["variante_fonte"] = (
                bruto.get("_variante_fonte")
                or bruto.get("variante_fonte")
                or ""
            )
            item["_variante_fonte"] = item["variante_fonte"]
            item["ilvl_origem"] = bruto.get("_ilvl_origem") or ""
            item["ilvl_conflito"] = bool(bruto.get("_ilvl_conflito"))
            item["variante_alternativa_usada"] = bool(
                bruto.get("_variante_alternativa_usada")
            )

            tipos_catalogo = {"encantamento", "gema", "missiva", "consumivel"}
            ilvl = int(item.get("item_level") or 0)
            if ilvl and item.get("tipo_item") not in tipos_catalogo:
                if (self.ilvl_min and ilvl < self.ilvl_min) or (
                    self.ilvl_max and ilvl > self.ilvl_max
                ):
                    self.descartes["ilvl_fora"] += 1
                    continue
            elif (
                not ilvl
                and not self.incluir_sem_ilvl
                and item.get("tipo_item") not in tipos_catalogo
            ):
                self.descartes["sem_ilvl"] += 1
                continue

            if (
                self.qualidade_min
                and item.get("tipo_item")
                in ("gear", "embelezamento", "ferramenta")
                and item.get("qualidade")
                and int(item["qualidade"]) < self.qualidade_min
            ):
                self.descartes["qualidade"] += 1
                continue

            if self.slots_permitidos and item.get("tipo_item") in (
                "gear",
                "embelezamento",
                "ferramenta",
            ):
                slot = item.get("slot") or ""
                # Slot desconhecido não é descartado; só filtra quando conhecido
                if slot not in ("", "N/A") and slot not in self.slots_permitidos:
                    self.descartes["slot"] += 1
                    continue

            qc = int(item.get("qualidade_craft") or 0)
            aplica_craft = item.get("tipo_item") in (
                "gear",
                "embelezamento",
                "ferramenta",
            )
            if self.qualidade_craft_min and aplica_craft:
                if self.exigir_craft:
                    # Requisito do produto: só itens craftados no rank pedido.
                    if qc != int(self.qualidade_craft_min):
                        self.descartes["sem_craft"] += 1
                        continue
                elif qc and qc < self.qualidade_craft_min:
                    self.descartes["qualidade_craft"] += 1
                    continue

            if item.get("tipo_item") == "outro":
                self.descartes["tipo"] += 1
                continue

            if (
                self.profissoes_permitidas
                and item.get("tipo_item") == "ferramenta"
                and item.get("profissao") not in self.profissoes_permitidas
            ):
                self.descartes["profissao"] += 1
                continue

            chave = chave_variacao(
                item.get("id"),
                ilvl,
                item.get("bonus_ids"),
                item.get("track_stage") or "",
            )
            existente = vistos.get(chave)
            if existente is None:
                vistos[chave] = item
                continue

            # Prefere o registro mais completo
            def _pontos(registro: Dict[str, Any]) -> int:
                return (
                    len(registro.get("atributos_primarios") or {})
                    + len(registro.get("atributos_secundarios") or {})
                    + len(registro.get("atributos_primarios_en") or {})
                    + len(registro.get("atributos_secundarios_en") or {})
                    + len(registro.get("nome_en") or "")
                    + len(registro.get("nome_ptbr") or "")
                    + len(registro.get("efeito_equip_uso") or "")
                    + (1 if registro.get("icone_url") else 0)
                )

            if _pontos(item) > _pontos(existente):
                vistos[chave] = item

        finais = list(vistos.values())
        finais.sort(
            key=lambda x: (
                int(x.get("item_level") or 0),
                str(x.get("track") or ""),
                str(x.get("nome_ptbr") or x.get("nome_en") or ""),
            )
        )
        return finais

    # ------------------------------------------------------------------- main
    async def executar_por_categorias(
        self, categorias: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Executa a extração apenas das categorias/URLs informadas."""
        categorias_limpas = {}
        for nome, urls in (categorias or {}).items():
            expandidas: List[str] = []
            for url in urls:
                if not url or not url.strip():
                    continue
                expandidas.extend(normalizar_url_gear(url.strip()))
            categorias_limpas[nome] = expandidas
        total_urls = sum(len(v) for v in categorias_limpas.values())
        if total_urls == 0:
            raise ValueError("Nenhuma URL para extrair nas categorias selecionadas.")

        brutos: List[Dict[str, Any]] = []
        falhas: List[Dict[str, str]] = []
        processadas = 0

        for categoria, urls in categorias_limpas.items():
            for url in urls:
                # Circuit breaker aberto: aborta a categoria (não trava
                # indefinidamente) e registra o motivo em `metadata.falhas`.
                if self.circuito.deve_bloquear():
                    motivo = (
                        "circuit breaker anti-bot abortou a categoria: "
                        f"{self.circuito.motivo}"
                    )
                    falhas.append({"url": url, "erro": motivo})
                    self._registrar_falha_circuito(url, self.circuito.motivo)
                    break
                processadas += 1
                self._update_progress(
                    f"[{categoria}] Lista {processadas}/{total_urls}: {url[:70]}",
                    processadas,
                    total_urls,
                )
                itens, falha = await self.coletar_url(url, categoria)
                if falha:
                    falhas.append(falha)
                    if self.circuito.deve_bloquear():
                        falhas.append(
                            {
                                "url": url,
                                "erro": "circuit breaker anti-bot abortou a "
                                f"categoria: {self.circuito.motivo}",
                            }
                        )
                        break
                    continue
                brutos.extend(itens)

        # Ordem obrigatória: dedupe -> seleção de variantes -> pré-filtro ->
        # truncar -> detalhar (F-01). A seleção vem ANTES do truncamento para
        # que as vagas de `max_itens` não sejam gastas em variantes do MESMO
        # item (a listagem devolve várias variantes por `item_id`).
        total_brutos_antes_dedupe = len(brutos)
        self._iniciar_descartes()
        brutos = self._consolidar_brutos(brutos)
        variantes_antes_selecao = len(brutos)
        itens_distintos = len({str(b.get("id") or "") for b in brutos})
        brutos = self._selecionar_melhores_variantes(
            brutos, set(TRACKS_SEASON2)
        )
        variantes_depois_selecao = len(brutos)
        brutos = self._prefiltrar(brutos)
        if len(brutos) > self.max_itens:
            brutos = brutos[: self.max_itens]

        # P-03/F-05: sem detalhamento (browser), enriquece via tooltip HTTP
        # antes de finalizar — é o que evita o descarte em massa por `sem_ilvl`.
        if not self.buscar_detalhes or self.max_detalhes == 0:
            brutos = self.enriquecer_por_tooltip(brutos)

        brutos = await self.detalhar_itens(brutos)
        detalhados = sum(1 for b in brutos if b.get("_pt") is not None)
        itens = self._finalizar(brutos)
        avisos = _validar_categorias(itens, categorias_limpas)

        # Falhas do circuit breaker (detalhamento) entram em `metadata.falhas`.
        falhas.extend(self._falhas_circuito)

        self._update_progress("Extração concluída", 1, 1)

        return {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "versao_scraper": "2.1.0-season2",
                "ilvl_min": self.ilvl_min,
                "ilvl_max": self.ilvl_max,
                "qualidade_min": self.qualidade_min,
                "qualidade_craft_min": self.qualidade_craft_min,
                "total_itens": len(itens),
                "total_brutos": len(brutos),
                "total_brutos_antes_dedupe": total_brutos_antes_dedupe,
                "variantes_antes_selecao": variantes_antes_selecao,
                "variantes_depois_selecao": variantes_depois_selecao,
                "itens_distintos": itens_distintos,
                "selecao_variante": dict(
                    getattr(
                        self,
                        "_selecao_variante_contagem",
                        self._selecao_variante_vazia(),
                    )
                ),
                "detalhados": detalhados,
                "max_detalhes": self.max_detalhes,
                "enriquecidos_tooltip": getattr(
                    self, "_tooltip_enriquecidos", 0
                ),
                "tooltip_falhas": getattr(self, "_tooltip_falhas", 0),
                "ilvl_origem": dict(
                    getattr(self, "_ilvl_origem_contagem", {})
                ),
                "descartes": getattr(self, "descartes", {}),
                "categorias": _resumo_categorias(categorias_limpas),
                "filtros": {
                    "slots": self.slots_permitidos,
                    "profissoes": self.profissoes_permitidas,
                    "buscar_detalhes": self.buscar_detalhes,
                    "buscar_ingles": self.buscar_ingles,
                    "exigir_craft": self.exigir_craft,
                },
                "avisos_catalogo": avisos,
                "arquivo_markdown": self.caminho_md if self.gerar_markdown else "",
                # JS-03/F-04: rastreio de retries e do circuit breaker.
                "tentativas_wait": self._tentativas_wait,
                "retry_scroll_usado": self._retry_scroll_usado,
                "circuit_breaker": self.circuito.resumo(),
                "falhas": falhas,
            },
            "itens": itens,
        }

    async def executar(self, urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """Conveniência: executa uma lista simples de URLs (categoria 'Geral').

        Sem `urls`, usa a lista canônica de IDs da temporada (F-01/P-01b).
        A listagem genérica (`SEASON2_ITEM_URLS`) fica só como fallback, pois
        o Wowhead não filtra `ilvl`/`bonus` server-side.
        """
        if urls is not None:
            lista = urls
        elif self.exigir_craft:
            lista = urls_craft_canonicas(self.max_itens) or urls_gear_canonicas(
                self.max_itens
            )
        else:
            lista = urls_gear_canonicas(self.max_itens) or SEASON2_ITEM_URLS
        return await self.executar_por_categorias({"Geral": list(lista)})

    def salvar_resultados(
        self,
        resultado: Dict[str, Any],
        caminho: str = os.path.join("data", "wowhead_itens_season2.json"),
        caminho_md: Optional[str] = None,
    ) -> str:
        """Salva o JSON e (opcionalmente) o documento Markdown final."""
        diretorio = os.path.dirname(caminho)
        if diretorio:
            os.makedirs(diretorio, exist_ok=True)

        if self.gerar_markdown:
            md_path = caminho_md or self.caminho_md
            try:
                salvo = salvar_markdown(
                    resultado.get("itens") or [],
                    caminho=md_path,
                    metadata=resultado.get("metadata") or {},
                )
                resultado.setdefault("metadata", {})["arquivo_markdown"] = salvo
            except Exception as exc:  # pragma: no cover
                resultado.setdefault("metadata", {})[
                    "erro_markdown"
                ] = str(exc)

        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)

        # F-11: se o artefato gravado for timestamped (`*_sem_llm_*`), aplica
        # a política de retenção para não acumular duplicados em `data/`.
        nome = os.path.basename(caminho)
        if "_sem_llm_" in nome:
            _rotacionar_artefatos(f"*{nome[nome.index('_sem_llm_'):]}")
        return caminho


def _resumo_categorias(categorias: Dict[str, List[str]]) -> Dict[str, int]:
    return {nome: len(urls) for nome, urls in categorias.items()}


TIPOS_ESPERADOS_CATEGORIA = {
    "Encantamentos": "encantamento",
    "Gemas": "gema",
    "Missivas (tipos)": "missiva",
    "Consumíveis": "consumivel",
}


def _validar_categorias(
    itens: List[Dict[str, Any]], categorias: Dict[str, List[str]]
) -> List[Dict[str, Any]]:
    """Detecta categorias vazias ou que retornaram catálogo genérico."""
    avisos: List[Dict[str, Any]] = []
    for categoria, urls in (categorias or {}).items():
        esperado = TIPOS_ESPERADOS_CATEGORIA.get(categoria)
        if not esperado:
            continue
        da_categoria = [i for i in itens if i.get("categoria") == categoria]
        correspondentes = [
            i for i in da_categoria if i.get("tipo_item") == esperado
        ]
        if not correspondentes:
            avisos.append(
                {
                    "categoria": categoria,
                    "esperado": esperado,
                    "encontrados": len(da_categoria),
                    "aviso": "Nenhum item do tipo esperado nesta categoria. "
                    "A URL pode ter retornado catálogo genérico ou "
                    "redirecionado.",
                    "urls": urls,
                }
            )
    return avisos


def _parse_args():  # pragma: no cover - CLI
    import argparse

    parser = argparse.ArgumentParser(
        description="Scraper bilíngue (EN/PT-BR) de itens da Season 2 do Wowhead"
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        default=None,
        help="URLs de listas/guias/itens (padrão: SEASON2_ITEM_URLS do config.py)",
    )
    parser.add_argument(
        "--ilvl-min",
        type=int,
        default=ILVL_PISO_PADRAO,
        help=f"Piso de item level aceito (padrão: {ILVL_PISO_PADRAO}).",
    )
    parser.add_argument(
        "--ilvl-max",
        type=int,
        default=ILVL_TETO_PADRAO,
        help=f"Teto de item level aceito (padrão: {ILVL_TETO_PADRAO}).",
    )
    parser.add_argument(
        "--qualidade-min",
        type=int,
        default=QUALIDADE_MINIMA_GEAR_PADRAO,
        help=(
            "Raridade mínima do item: 3=Raro, 4=Épico, 5=Lendário "
            f"(padrão: {QUALIDADE_MINIMA_GEAR_PADRAO}). NÃO é o craft (R)."
        ),
    )
    parser.add_argument(
        "--max-itens",
        type=int,
        default=200,
        help="Limite de itens retornados (padrão: 200).",
    )
    parser.add_argument(
        "--max-detalhes",
        type=int,
        default=None,
        help=(
            "Máximo de itens a detalhar: None=todos; 0=nenhum "
            "(mesmo efeito de --sem-detalhes); N=N primeiros após "
            "dedupe e pré-filtro."
        ),
    )
    parser.add_argument(
        "--qualidade-craft",
        type=int,
        default=5,
        help=(
            "Qualidade de craft mínima (R1–R5) usada na URL de detalhe. "
            "Itens craftados abaixo do rank são descartados; 0 desativa o "
            "filtro (padrão: 5). Separada de --qualidade-min."
        ),
    )
    parser.add_argument(
        "--exigir-craft",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Aceitar somente itens craftados no rank de --qualidade-craft "
            "(padrão: ligado). Use --no-exigir-craft para manter itens não "
            "craftados (qualidade_craft=0)."
        ),
    )
    parser.add_argument(
        "--incluir-sem-ilvl", action="store_true", help="Manter itens sem ilvl"
    )
    parser.add_argument(
        "--sem-detalhes",
        action="store_true",
        help=(
            "Não visitar páginas individuais. Equivale a --max-detalhes 0 "
            "(sem atributos/nomes bilíngues)."
        ),
    )
    parser.add_argument(
        "--sem-ingles",
        action="store_true",
        help="Não visitar a versão EN (perde o nome em inglês)",
    )
    parser.add_argument(
        "--sem-markdown", action="store_true", help="Não gerar o .md final"
    )
    parser.add_argument(
        "--json", default=os.path.join("data", "wowhead_itens_season2.json")
    )
    parser.add_argument("--md", default=os.path.join("data", "wowhead_season2.md"))
    return parser.parse_args()


async def main() -> None:  # pragma: no cover - execução manual
    args = _parse_args()
    print("=== Scraper WoWhead Season 2 (Midnight) — EN/PT-BR ===")

    # --sem-detalhes e --max-detalhes 0 têm o mesmo efeito (nenhum detalhe).
    max_detalhes = 0 if args.sem_detalhes else args.max_detalhes

    scraper = WowheadSeason2Scraper(
        ilvl_min=args.ilvl_min,
        ilvl_max=args.ilvl_max,
        qualidade_min=args.qualidade_min,
        qualidade_craft_min=args.qualidade_craft,
        exigir_craft=args.exigir_craft,
        buscar_detalhes=(not args.sem_detalhes) and max_detalhes != 0,
        buscar_ingles=not args.sem_ingles,
        gerar_markdown=not args.sem_markdown,
        caminho_md=args.md,
        max_itens=args.max_itens,
        max_detalhes=max_detalhes,
        incluir_sem_ilvl=args.incluir_sem_ilvl,
    )

    # F-01/P-01b: a fonte primária de gear é a lista canônica de IDs da
    # temporada (o Wowhead não filtra `ilvl`/`bonus` server-side). A listagem
    # genérica só entra como fallback quando o artefato de IDs não existe.
    urls_efetivas = (
        args.urls
        or (
            urls_craft_canonicas(args.max_itens)
            if args.exigir_craft
            else urls_gear_canonicas(args.max_itens)
        )
        or SEASON2_ITEM_URLS
    )

    async with scraper:
        resultado = await scraper.executar(urls_efetivas)
        caminho_json = scraper.salvar_resultados(resultado, args.json, args.md)

    meta = resultado.get("metadata", {}) or {}
    itens = resultado.get("itens", []) or []
    no_intervalo = sum(
        1
        for item in itens
        if args.ilvl_min
        <= int(item.get("item_level") or 0)
        <= args.ilvl_max
    )

    print("\nURL(s) de listagem efetiva(s):")
    for url in urls_efetivas:
        print(f"  {url}")

    print(f"\nTotal de itens: {meta.get('total_itens')}")
    print(f"total_brutos: {meta.get('total_brutos')}")
    print(f"total_brutos_antes_dedupe: {meta.get('total_brutos_antes_dedupe')}")
    print(f"variantes_antes_selecao: {meta.get('variantes_antes_selecao')}")
    print(f"variantes_depois_selecao: {meta.get('variantes_depois_selecao')}")
    print(f"itens_distintos: {meta.get('itens_distintos')}")
    print(f"selecao_variante: {meta.get('selecao_variante')}")
    print(f"detalhados: {meta.get('detalhados')}")
    print(f"max_detalhes: {meta.get('max_detalhes')}")
    print(f"descartes: {meta.get('descartes')}")
    print(f"ilvl_origem: {meta.get('ilvl_origem')}")
    print(f"tentativas_wait: {meta.get('tentativas_wait')}")
    print(f"retry_scroll_usado: {meta.get('retry_scroll_usado')}")
    print(f"circuit_breaker: {meta.get('circuit_breaker')}")
    print(f"falhas ({len(meta.get('falhas') or [])}): {meta.get('falhas')}")
    print(
        f"itens com item_level entre {args.ilvl_min} e {args.ilvl_max}: "
        f"{no_intervalo}"
    )
    print(f"JSON salvo: {caminho_json}")
    print(f"Markdown salvo: {meta.get('arquivo_markdown', '(não gerado)')}")


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(main())
