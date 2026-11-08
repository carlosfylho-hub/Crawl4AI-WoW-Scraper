#!/usr/bin/env python3
"""
Servidor MCP (Model Context Protocol) do Crawl4AI / WoW Season 2 (Edição Aprimorada).

Expõe ferramentas avançadas de scraping no estilo Firecrawl / ScrapegraphAI:

- scrape_pagina: raspa qualquer página com Fit Markdown (sem ruídos de menu/header),
                 suporte a SPA/JS e controle de tags/ações (estilo Firecrawl scrape).
- map_site: descobre e mapeia links e rotas de um domínio/site (estilo Firecrawl map).
- scrape_estruturado: extrai entidades diretamente em JSON via esquema CSS
                      (estilo ScrapegraphAI / Firecrawl extract).
- scrape_wowhead_item: extrai um item do Wowhead em EN + PT-BR.
- scrape_wowhead_items: extrai uma lista de URLs de itens com filtros de craft/ilvl.
- listar_catalogo: consulta o catálogo consolidado salvo em data/.
- recomendar_encantamento_gema: recomendações por classe/especialidade.
- estado_dados: mostra quais arquivos/catálogos estão disponíveis.

Transporte padrão: stdio (recomendado para clientes locais).
"""

from __future__ import annotations

import asyncio
import html as html_lib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from mcp.server.fastmcp import FastMCP

from recomendacoes import gerar_recomendacoes
from runtime import configurar_event_loop_windows
from scraper_season2 import WowheadSeason2Scraper

# Playwright precisa de ProactorEventLoop no Windows (centralizado em runtime.py).
configurar_event_loop_windows()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ITENS_PATH = DATA_DIR / "wowhead_itens_season2.json"
CATALOGO_PATH = DATA_DIR / "wowhead_catalogo.json"

mcp = FastMCP(
    "crawl4ai-wow",
    instructions=(
        "Ferramentas avançadas de scraping com Crawl4AI (Playwright) com recursos "
        "estilo Firecrawl (Fit Markdown limpo e map_site) e ScrapegraphAI (scrape_estruturado "
        "com schemas JSON), além de extração bilíngue EN/PT-BR de itens de WoW."
    ),
)

def _gerar_js_completo(
    auto_clicar_abas: bool = True,
    seletor_abas: str = "",
    clicar_em: str = "",
    espera_ms: int = 800,
    max_abas: int = 15,
    extrair_tooltips: bool = True,
    max_tooltips: int = 40,
    espera_tooltip_ms: int = 200,
    scroll_ate_fim: bool = True,
    js_customizado: str = "",
) -> str:
    """Gera um único script assíncrono consolidado que executa abas, cliques e rolagem retornando metadados."""
    seletores_especificos = [s.strip() for s in clicar_em.split(",") if s.strip()] if clicar_em else []
    seletor_custom_tab = seletor_abas.strip()
    espera = max(200, int(espera_ms))
    limite_abas = max(2, int(max_abas))

    return f"""
return (async () => {{
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const dadosAbas = [];

  // 1. Processar Abas Automáticas
  if ({json.dumps(auto_clicar_abas)}) {{
    try {{
      const seletorCustom = {json.dumps(seletor_custom_tab)};
      let seletores = [];
      if (seletorCustom) {{
        seletores = [seletorCustom];
      }} else {{
        seletores = [
          '[role="tab"]',
          '[role="tablist"] button, [role="tablist"] a, [role="tablist"] li > button, [role="tablist"] li > a',
          '.nav-tabs button, .nav-tabs a, .nav-pills button, .nav-pills a',
          '.tabs button, .tabs a, ul.tabs li button, ul.tabs li a',
          'button[data-tab], a[data-tab]',
          'button[data-bs-toggle="tab"], button[data-toggle="tab"], a[data-bs-toggle="tab"], a[data-toggle="tab"]',
          '.tab-button, .tab-btn, .tab-item, [class*="tab-item"], [class*="tabButton"]',
          'button[aria-controls], a[aria-controls]'
        ];
      }}

      let abas = [];
      for (const sel of seletores) {{
        try {{
          const els = Array.from(document.querySelectorAll(sel));
          const validas = els.filter(el => {{
            const href = el.getAttribute('href') || '';
            if (href && !href.startsWith('#') && !href.startsWith('javascript:') && href !== '') {{
              try {{
                const u = new URL(href, window.location.href);
                if (u.pathname !== window.location.pathname) return false;
              }} catch(e) {{}}
            }}
            const st = window.getComputedStyle(el);
            return st.display !== 'none' && st.visibility !== 'hidden' && (el.offsetWidth > 0 || el.offsetHeight > 0 || (el.innerText || el.textContent || '').trim().length > 0);
          }});
          if (validas.length > 1) {{
            abas = validas.slice(0, {limite_abas});
            break;
          }}
        }} catch(e) {{}}
      }}

      if (abas.length > 1) {{
        let container = document.getElementById('crawl4ai-abas-consolidadas');
        if (!container) {{
          container = document.createElement('div');
          container.id = 'crawl4ai-abas-consolidadas';
          container.style.marginTop = '30px';
          container.style.padding = '15px';
          document.body.appendChild(container);
        }}

        const abaOriginal = abas.find(a => a.getAttribute('aria-selected') === 'true' || a.classList.contains('active')) || abas[0];

        for (let i = 0; i < abas.length; i++) {{
          const aba = abas[i];
          const nomeAba = (aba.innerText || aba.textContent || `Aba ${{i + 1}}`).trim();
          if (!nomeAba) continue;

          try {{
            aba.scrollIntoView({{ behavior: 'instant', block: 'center' }});
            aba.click();
            aba.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true }}));
            await sleep({espera});
          }} catch (e) {{}}

          let painel = null;
          const idAlvo = aba.getAttribute('aria-controls') || aba.getAttribute('data-target') || (aba.getAttribute('href') || '').replace('#', '');
          if (idAlvo) {{
            try {{ painel = document.getElementById(idAlvo); }} catch(e) {{}}
          }}
          if (!painel) {{
            const candidatosPainel = Array.from(document.querySelectorAll('[role="tabpanel"], .tab-pane, .tab-content > *, .active-tab-content'));
            painel = candidatosPainel.find(el => {{
              const st = window.getComputedStyle(el);
              return st.display !== 'none' && st.visibility !== 'hidden';
            }});
          }}
          if (!painel) {{
            painel = aba.closest('section, article, main, .tabs-container, .card') || document.body;
          }}

          const htmlConteudo = painel ? painel.innerHTML : '';
          dadosAbas.push({{
            indice: i + 1,
            nome: nomeAba
          }});

          const secao = document.createElement('section');
          secao.className = 'crawl4ai-secao-aba';
          secao.setAttribute('data-tab-title', nomeAba);
          secao.innerHTML = `
            <h2 class="crawl4ai-tab-title" style="margin-top:20px;">=== ABA: ${{nomeAba}} ===</h2>
            <div class="crawl4ai-tab-body">${{htmlConteudo}}</div>
          `;
          container.appendChild(secao);
        }}

        if (abaOriginal) {{
          try {{
            abaOriginal.click();
            await sleep(200);
          }} catch(e) {{}}
        }}
      }}
    }} catch (errAbas) {{
      console.warn('Erro ao processar abas:', errAbas);
    }}
  }}

// 2. Extração de Tooltips via Mouse Hover (Passar mouse em cima para ler atributos)
  if ({json.dumps(extrair_tooltips)}) {{
    try {{
      const escapeAttr = (str) => (str || '').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const seletoresTooltip = [
        'a[href*="item="]',
        'a[href*="spell="]',
        'a[href*="talent="]',
        'a[href*="affix="]',
        '[data-wowhead]',
        '[data-tooltip]',
        '[data-tippy-content]',
        '.has-tooltip',
        '[data-toggle="tooltip"]',
        '.item-link'
      ];

      const elementosTooltip = Array.from(document.querySelectorAll(seletoresTooltip.join(','))).slice(0, {max(5, int(max_tooltips))});

      let containerTooltips = document.getElementById('crawl4ai-tooltips-consolidadas');
      if (!containerTooltips && elementosTooltip.length > 0) {{
        containerTooltips = document.createElement('section');
        containerTooltips.id = 'crawl4ai-tooltips-consolidadas';
        containerTooltips.style.marginTop = '40px';
        containerTooltips.innerHTML = '<h2 class="crawl4ai-tooltip-header">=== ATRIBUTOS E DETALHES DE TOOLTIPS ===</h2><ul id="crawl4ai-lista-tooltips"></ul>';
        document.body.appendChild(containerTooltips);
      }}
      const listaTooltipsUl = document.getElementById('crawl4ai-lista-tooltips');

      for (let i = 0; i < elementosTooltip.length; i++) {{
        const el = elementosTooltip[i];
        const nomeItem = (el.innerText || el.textContent || '').trim();
        const href = el.getAttribute('href') || '';
        if (!nomeItem) continue;

        // Hover
        const rect = el.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;

        el.dispatchEvent(new MouseEvent('mouseenter', {{ bubbles: true, cancelable: true, clientX: cx, clientY: cy }}));
        el.dispatchEvent(new MouseEvent('mouseover', {{ bubbles: true, cancelable: true, clientX: cx, clientY: cy }}));
        el.dispatchEvent(new MouseEvent('mousemove', {{ bubbles: true, cancelable: true, clientX: cx, clientY: cy }}));

        await sleep({max(80, int(espera_tooltip_ms))});

        const seletoresCaixaTooltip = [
          '.wowhead-tooltip',
          '[role="tooltip"].visible, [role="tooltip"]:not([style*="display: none"]):not([hidden])',
          '.tippy-box',
          '.tooltip.show, .tooltip.visible, .tooltip:not([style*="display: none"]):not([hidden])',
          '.tooltip-box.visible',
          'div[id*="tooltip"].visible, div[id*="tooltip"]:not([style*="display: none"]):not([hidden])'
        ];

        let textoTooltip = "";
        for (const selT of seletoresCaixaTooltip) {{
          try {{
            const tEls = Array.from(document.querySelectorAll(selT));
            for (const tEl of tEls) {{
              const st = window.getComputedStyle(tEl);
              if (st.display !== 'none' && st.visibility !== 'hidden' && (st.opacity === '' || parseFloat(st.opacity) > 0)) {{
                const t = (tEl.innerText || tEl.textContent || '').trim();
                if (t) {{
                  textoTooltip = t;
                  break;
                }}
              }}
            }}
            if (textoTooltip) break;
          }} catch(e) {{}}
        }}

        if (!textoTooltip) {{
          textoTooltip = el.getAttribute('data-tooltip') || el.getAttribute('data-tippy-content') || el.getAttribute('title') || '';
        }}

        el.dispatchEvent(new MouseEvent('mouseout', {{ bubbles: true, cancelable: true }}));
        el.dispatchEvent(new MouseEvent('mouseleave', {{ bubbles: true, cancelable: true }}));

        if (textoTooltip) {{
          const textoLimpo = textoTooltip.split(String.fromCharCode(10)).map(s => s.trim()).filter(Boolean).join(' | ');
          const spanAnotacao = document.createElement('span');
          spanAnotacao.className = 'crawl4ai-tooltip-anotado';
          spanAnotacao.innerHTML = ' <em>(' + textoLimpo + ')</em>';
          el.appendChild(spanAnotacao);

          if (listaTooltipsUl) {{
            const li = document.createElement('li');
            li.className = 'crawl4ai-tooltip-item';
            li.setAttribute('data-item', escapeAttr(nomeItem));
            li.setAttribute('data-href', escapeAttr(href));
            li.setAttribute('data-atributos', escapeAttr(textoLimpo));
            li.innerHTML = '<strong>' + nomeItem + '</strong>: ' + textoLimpo;
            listaTooltipsUl.appendChild(li);
          }}
        }}
      }}
    }} catch (errTip) {{
      console.warn('Erro ao processar tooltips:', errTip);
    }}
  }}

  // 3. Cliques Manuais em Seletores Específicos
  const seletoresManuais = {json.dumps(seletores_especificos)};
  for (const sel of seletoresManuais) {{
    try {{
      const el = document.querySelector(sel);
      if (el) {{
        el.click();
        await sleep({espera});
      }}
    }} catch (e) {{
      console.warn('Falha ao clicar em: ' + sel, e);
    }}
  }}

  // 4. JS Customizado
  {js_customizado if js_customizado else ""}

  // 5. Scroll Dinâmico
  if ({json.dumps(scroll_ate_fim and not js_customizado)}) {{
    try {{
      for (let i = 0; i < 4; i++) {{
        window.scrollTo(0, document.body.scrollHeight);
        await sleep(400);
      }}
      window.scrollTo(0, 0);
      await sleep(200);
    }} catch (e) {{}}
  }}

  return {{
    abas: dadosAbas,
    total_abas: dadosAbas.length
  }};
}})();
"""
_JS_SCROLL = """
(async () => {
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  for (let i = 0; i < 5; i++) {
    window.scrollTo(0, document.body.scrollHeight);
    await sleep(600);
  }
  window.scrollTo(0, 0);
  await sleep(300);
  return true;
})();
"""


def _texto_markdown(result: Any, preferir_fit: bool = True) -> Dict[str, str]:
    """Extrai tanto o Fit Markdown (filtrado/limpo) quanto o Raw Markdown."""
    md = getattr(result, "markdown", None)
    fit_texto = ""
    raw_texto = ""

    if isinstance(md, str):
        fit_texto = md
        raw_texto = md
    elif md is not None:
        raw_texto = str(getattr(md, "raw_markdown", "") or "")
        fit_texto = str(getattr(md, "fit_markdown", "") or "")
        if not raw_texto and not fit_texto:
            fit_texto = str(md)
            raw_texto = str(md)

    if not fit_texto:
        fit_texto = raw_texto
    if not raw_texto:
        raw_texto = fit_texto

    principal = fit_texto if preferir_fit and fit_texto else raw_texto
    return {
        "principal": principal,
        "fit": fit_texto,
        "raw": raw_texto,
    }


def _imagens_media(result: Any, limite: int = 40) -> List[Dict[str, str]]:
    media = getattr(result, "media", None)
    if not isinstance(media, dict):
        return []
    imagens: List[Dict[str, str]] = []
    for imagem in media.get("images") or []:
        if isinstance(imagem, dict) and imagem.get("src"):
            imagens.append(
                {
                    "src": str(imagem["src"]),
                    "alt": str(imagem.get("alt") or ""),
                }
            )
        if len(imagens) >= limite:
            break
    return imagens


def _links(result: Any, limite: int = 50) -> Dict[str, List[str]]:
    links = getattr(result, "links", None)
    if not isinstance(links, dict):
        return {"internos": [], "externos": []}

    def _extrair(chave: str) -> List[str]:
        valores = []
        for link in links.get(chave) or []:
            if isinstance(link, dict) and link.get("href"):
                valores.append(str(link["href"]))
            elif isinstance(link, str):
                valores.append(link)
            if len(valores) >= limite:
                break
        return valores

    return {
        "internos": _extrair("internal"),
        "externos": _extrair("external"),
    }


def _base_config(headless: bool = True) -> BrowserConfig:
    try:
        return BrowserConfig(
            headless=headless,
            enable_stealth=True,
            verbose=False,
            browser_type="chromium",
            viewport_width=1920,
            viewport_height=1080,
        )
    except TypeError:
        return BrowserConfig(
            headless=headless,
            verbose=False,
            browser_type="chromium",
            viewport_width=1920,
            viewport_height=1080,
        )


async def scrape_pagina_impl(
    url: str,
    wait_for: str = "css:body",
    usar_js: bool = True,
    max_caracteres: int = 25000,
    incluir_html: bool = False,
    apenas_conteudo_principal: bool = True,
    scroll_ate_fim: bool = True,
    auto_clicar_abas: bool = True,
    seletor_abas: str = "",
    clicar_em: str = "",
    extrair_tooltips: bool = True,
    max_tooltips: int = 40,
    espera_tooltip_ms: int = 200,
    espera_apos_clique_ms: int = 800,
    js_customizado: str = "",
    remover_tags: Optional[List[str]] = None,
    capturar_screenshot: bool = False,
) -> Dict[str, Any]:
    """Implementação síncrona de scraping com suporte a Fit Markdown e clique automático em abas."""
    kwargs: Dict[str, Any] = {
        "cache_mode": CacheMode.BYPASS,
        "wait_for": wait_for or "css:body",
        "page_timeout": 60000,
        "verbose": False,
    }

    if capturar_screenshot:
        kwargs["screenshot"] = True

    if apenas_conteudo_principal:
        tags_excluidas = remover_tags or ["nav", "footer", "header", "aside", "form", "dialog"]
        kwargs["excluded_tags"] = tags_excluidas
        try:
            from crawl4ai.content_filter_strategy import PruningContentFilter
            from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

            md_gen = DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.48)
            )
            kwargs["markdown_generator"] = md_gen
        except Exception:
            pass

    if usar_js:
        kwargs["js_code"] = _gerar_js_completo(
            auto_clicar_abas=auto_clicar_abas,
            seletor_abas=seletor_abas,
            clicar_em=clicar_em,
            espera_ms=espera_apos_clique_ms,
            extrair_tooltips=extrair_tooltips,
            max_tooltips=max_tooltips,
            espera_tooltip_ms=espera_tooltip_ms,
            scroll_ate_fim=scroll_ate_fim,
            js_customizado=js_customizado,
        )

    try:
        run_config = CrawlerRunConfig(**kwargs)
    except TypeError:
        kwargs.pop("js_code", None)
        kwargs.pop("markdown_generator", None)
        kwargs.pop("excluded_tags", None)
        run_config = CrawlerRunConfig(**kwargs)

    try:
        async with AsyncWebCrawler(config=_base_config()) as crawler:
            result = await crawler.arun(url=url, config=run_config)
    except Exception as exc:  # noqa: BLE001
        return {"sucesso": False, "url": url, "erro": f"exceção: {exc}"}

    if not getattr(result, "success", False):
        return {
            "sucesso": False,
            "url": url,
            "erro": str(getattr(result, "error_message", "falha desconhecida")),
        }

    textos_md = _texto_markdown(result, preferir_fit=apenas_conteudo_principal)
    texto = textos_md["principal"] or (getattr(result, "html", "") or "")
    metadata = getattr(result, "metadata", None) or {}
    titulo = metadata.get("title", "") if isinstance(metadata, dict) else ""

    html_completo = getattr(result, "html", "") or ""
    abas_detectadas = re.findall(r'data-tab-title="([^"]+)"', html_completo)
    padrao_tooltips = r'<li class="crawl4ai-tooltip-item"[^>]*data-item="([^"]+)"[^>]*data-href="([^"]+)"[^>]*data-atributos="([^"]+)"'
    tooltips_detectadas = [
        {
            "item": html_lib.unescape(m[0]),
            "href": html_lib.unescape(m[1]),
            "atributos": html_lib.unescape(m[2]),
        }
        for m in re.findall(padrao_tooltips, html_completo)
    ]

    resposta: Dict[str, Any] = {
        "sucesso": True,
        "url": url,
        "titulo": titulo,
        "texto_markdown": texto[:max_caracteres],
        "fit_markdown": textos_md["fit"][:max_caracteres],
        "raw_markdown": textos_md["raw"][:max_caracteres],
        "truncado": len(texto) > max_caracteres,
        "imagens": _imagens_media(result),
        "links": _links(result),
    }
    if abas_detectadas:
        resposta["abas_detectadas"] = abas_detectadas
        resposta["total_abas_processadas"] = len(abas_detectadas)
    if tooltips_detectadas:
        resposta["tooltips_detectadas"] = tooltips_detectadas
        resposta["total_tooltips_processadas"] = len(tooltips_detectadas)
    if incluir_html:
        resposta["html"] = html_completo[:max_caracteres]
    if capturar_screenshot and getattr(result, "screenshot", None):
        resposta["screenshot_base64"] = result.screenshot

    return resposta


async def scrape_todas_as_abas_impl(
    url: str,
    seletor_abas: str = "",
    espera_por_aba_ms: int = 800,
    max_abas: int = 15,
    extrair_tooltips: bool = True,
    max_tooltips: int = 40,
    max_caracteres: int = 35000,
    wait_for: str = "css:body",
    apenas_conteudo_principal: bool = True,
    incluir_html: bool = False,
) -> Dict[str, Any]:
    """Varre e raspa automaticamente TODAS as abas dinamicas e tooltips de uma pagina SPA."""
    return await scrape_pagina_impl(
        url=url,
        wait_for=wait_for,
        usar_js=True,
        max_caracteres=max_caracteres,
        incluir_html=incluir_html,
        apenas_conteudo_principal=apenas_conteudo_principal,
        scroll_ate_fim=True,
        auto_clicar_abas=True,
        seletor_abas=seletor_abas,
        extrair_tooltips=extrair_tooltips,
        max_tooltips=max_tooltips,
        espera_apos_clique_ms=espera_por_aba_ms,
    )


async def map_site_impl(
    url: str,
    apenas_mesmo_dominio: bool = True,
    filtro_padrao: str = "",
    limite: int = 100,
    wait_for: str = "css:body",
) -> Dict[str, Any]:
    """Mapeia links e rotas descobertas a partir de uma URL (estilo Firecrawl map)."""
    parsed_base = urlparse(url)
    dominio_base = parsed_base.netloc.lower()

    kwargs: Dict[str, Any] = {
        "cache_mode": CacheMode.BYPASS,
        "wait_for": wait_for or "css:body",
        "page_timeout": 45000,
        "verbose": False,
    }
    try:
        run_config = CrawlerRunConfig(**kwargs)
        async with AsyncWebCrawler(config=_base_config()) as crawler:
            result = await crawler.arun(url=url, config=run_config)
    except Exception as exc:  # noqa: BLE001
        return {"sucesso": False, "url": url, "erro": f"exceção ao mapear: {exc}"}

    if not getattr(result, "success", False):
        return {
            "sucesso": False,
            "url": url,
            "erro": str(getattr(result, "error_message", "falha ao acessar página")),
        }

    links_dict = getattr(result, "links", {}) or {}
    todos_links: List[Dict[str, str]] = []
    vistos = set()

    for categoria in ("internal", "external"):
        lista = links_dict.get(categoria) or []
        for item in lista:
            href = ""
            texto = ""
            if isinstance(item, dict):
                href = str(item.get("href") or "").strip()
                texto = str(item.get("text") or "").strip()
            elif isinstance(item, str):
                href = item.strip()

            if not href or href in vistos:
                continue
            if href.startswith(("#", "javascript:", "mailto:", "tel:")):
                continue

            parsed = urlparse(href)
            if apenas_mesmo_dominio and parsed.netloc and parsed.netloc.lower() != dominio_base:
                continue

            if filtro_padrao:
                if (
                    filtro_padrao.lower() not in href.lower()
                    and filtro_padrao.lower() not in texto.lower()
                ):
                    continue

            vistos.add(href)
            todos_links.append({"url": href, "texto": texto})
            if len(todos_links) >= limite:
                break
        if len(todos_links) >= limite:
            break

    return {
        "sucesso": True,
        "url_base": url,
        "dominio": dominio_base,
        "total_encontrado": len(todos_links),
        "links": todos_links,
    }


async def scrape_estruturado_impl(
    url: str,
    schema_css: Optional[Dict[str, Any]] = None,
    campos: Optional[List[str]] = None,
    clicar_em: str = "",
    espera_apos_clique_ms: int = 1000,
    wait_for: str = "css:body",
    usar_js: bool = True,
) -> Dict[str, Any]:
    """Extrai entidades estruturadas em JSON usando CSS Schema com suporte a cliques em abas."""
    from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

    if not schema_css and not campos:
        return {
            "sucesso": False,
            "erro": "Forneça 'schema_css' (formato JsonCssExtractionStrategy) ou lista de 'campos'.",
        }

    if schema_css:
        estrategia = JsonCssExtractionStrategy(schema_css)
    else:
        fields = [
            {"name": c, "selector": f"[id*='{c}'], [class*='{c}'], h2, h3, p", "type": "text"}
            for c in (campos or [])
        ]
        auto_schema = {
            "name": "ExtracaoAutomatica",
            "baseSelector": "body",
            "fields": fields,
        }
        estrategia = JsonCssExtractionStrategy(auto_schema)

    kwargs: Dict[str, Any] = {
        "cache_mode": CacheMode.BYPASS,
        "wait_for": wait_for or "css:body",
        "page_timeout": 60000,
        "extraction_strategy": estrategia,
        "verbose": False,
    }
    if usar_js:
        js_blocos = []
        if auto_clicar_abas or seletor_abas:
            js_blocos.append(_gerar_js_auto_abas(seletor_customizado=seletor_abas, espera_ms=espera_apos_clique_ms).strip())

        if clicar_em:
            seletores = [s.strip() for s in clicar_em.split(",") if s.strip()]
            js_cliques = f"""
(async () => {{
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const seletores = {json.dumps(seletores)};
  for (const sel of seletores) {{
    try {{
      const el = document.querySelector(sel);
      if (el) {{
        el.click();
        await sleep({espera_apos_clique_ms});
      }}
    }} catch (e) {{
      console.warn("Falha ao clicar em: " + sel, e);
    }}
  }}
  return true;
}})();
"""
            js_blocos.append(js_cliques.strip())
        js_blocos.append(_JS_SCROLL.strip())
        kwargs["js_code"] = ";\n\n".join(b.strip() if b.strip().startswith(";") else f";{b.strip()}" for b in js_blocos)

    try:
        run_config = CrawlerRunConfig(**kwargs)
        async with AsyncWebCrawler(config=_base_config()) as crawler:
            result = await crawler.arun(url=url, config=run_config)
    except Exception as exc:  # noqa: BLE001
        return {"sucesso": False, "url": url, "erro": f"exceção na extração: {exc}"}

    if not getattr(result, "success", False):
        return {
            "sucesso": False,
            "url": url,
            "erro": str(getattr(result, "error_message", "falha na extração")),
        }

    conteudo_bruto = getattr(result, "extracted_content", "") or ""
    dados_parseados = None
    if isinstance(conteudo_bruto, str) and conteudo_bruto.strip():
        try:
            dados_parseados = json.loads(conteudo_bruto)
        except Exception:
            dados_parseados = conteudo_bruto
    else:
        dados_parseados = conteudo_bruto

    return {
        "sucesso": True,
        "url": url,
        "dados": dados_parseados,
    }


def _normalizar_item_url(item: str) -> Optional[str]:
    item = (item or "").strip()
    if not item:
        return None
    if "item=" in item:
        return item
    if item.isdigit():
        return f"https://www.wowhead.com/pt/item={item}"
    return None


async def scrape_wowhead_item_impl(
    item: str,
    buscar_ingles: bool = True,
    qualidade_craft_min: int = 5,
    exigir_craft: bool = False,
) -> Dict[str, Any]:
    """Implementação da extração de um item do Wowhead."""
    url = _normalizar_item_url(item)
    if not url:
        return {
            "sucesso": False,
            "erro": "Informe um ID numérico ou uma URL com item=...",
        }

    async with WowheadSeason2Scraper(
        ilvl_min=0,
        ilvl_max=400,
        qualidade_min=0,
        qualidade_craft_min=qualidade_craft_min,
        exigir_craft=exigir_craft,
        incluir_sem_ilvl=True,
        buscar_detalhes=True,
        buscar_ingles=buscar_ingles,
        gerar_markdown=False,
        max_itens=1,
        max_detalhes=1,
        wait_for="css:body",
    ) as scraper:
        resultado = await scraper.executar([url])

    itens = resultado.get("itens") or []
    metadata = dict(resultado.get("metadata") or {})
    metadata.setdefault("qualidade_craft_min", qualidade_craft_min)
    metadata.setdefault("exigir_craft", exigir_craft)
    if not itens:
        return {
            "sucesso": False,
            "erro": "Item não extraído; verifique a URL/ID.",
            "url": url,
            "metadata": metadata,
        }
    return {
        "sucesso": True,
        "item": itens[0],
        "metadata": metadata,
    }


async def scrape_wowhead_items_impl(
    urls: List[str],
    ilvl_min: int = 305,
    ilvl_max: int = 350,
    max_itens: int = 20,
    buscar_detalhes: bool = True,
    buscar_ingles: bool = True,
    salvar: bool = False,
    qualidade_craft_min: int = 5,
    exigir_craft: bool = False,
) -> Dict[str, Any]:
    """Implementação da extração de vários itens/listas do Wowhead."""
    urls = [url.strip() for url in (urls or []) if url and url.strip()]
    if not urls:
        return {"sucesso": False, "erro": "Lista de URLs vazia."}

    async with WowheadSeason2Scraper(
        ilvl_min=ilvl_min,
        ilvl_max=ilvl_max,
        qualidade_min=0,
        qualidade_craft_min=qualidade_craft_min,
        exigir_craft=exigir_craft,
        incluir_sem_ilvl=True,
        buscar_detalhes=buscar_detalhes,
        buscar_ingles=buscar_ingles,
        gerar_markdown=salvar,
        max_itens=max_itens,
        max_detalhes=max_itens if buscar_detalhes else 0,
        wait_for="css:a[href*='item=']",
    ) as scraper:
        resultado = await scraper.executar_por_categorias({"MCP": urls})
        if salvar:
            scraper.salvar_resultados(
                resultado,
                str(DATA_DIR / "wowhead_itens_season2.json"),
                str(DATA_DIR / "wowhead_season2.md"),
            )

    metadata = dict(resultado.get("metadata") or {})
    metadata.setdefault("qualidade_craft_min", qualidade_craft_min)
    metadata.setdefault("exigir_craft", exigir_craft)
    return {
        "sucesso": True,
        "metadata": metadata,
        "itens": resultado.get("itens") or [],
    }


def listar_catalogo_impl(tipo: str = "", limite: int = 50) -> Dict[str, Any]:
    """Implementação da consulta ao catálogo consolidado."""
    if not CATALOGO_PATH.exists():
        return {
            "sucesso": False,
            "erro": "Catálogo não encontrado.",
            "fonte": str(CATALOGO_PATH),
        }

    try:
        with open(CATALOGO_PATH, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except Exception as exc:  # noqa: BLE001
        return {
            "sucesso": False,
            "erro": f"Falha ao ler catálogo: {exc}",
            "fonte": str(CATALOGO_PATH),
        }

    itens = dados.get("itens") or []
    if tipo:
        itens = [i for i in itens if i.get("tipo_item") == tipo]
    return {
        "sucesso": True,
        "total": len(itens),
        "itens": itens[: max(1, int(limite))],
        "fonte": str(CATALOGO_PATH),
    }


def _carregar_itens(caminho: Path) -> List[Dict[str, Any]]:
    if not caminho.exists():
        return []
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if isinstance(dados, list):
            return dados
        return dados.get("itens") or []
    except Exception:
        return []


def recomendar_encantamento_gema_impl(
    classe: str,
    especialidade: str,
    prioridade: Optional[List[str]] = None,
    primario: str = "",
    item_id: Optional[int] = None,
    limite: int = 3,
) -> Dict[str, Any]:
    """Implementação das recomendações usando gear + catálogo salvos."""
    gear = _carregar_itens(ITENS_PATH)
    catalogo = _carregar_itens(CATALOGO_PATH)
    if not catalogo:
        return {
            "sucesso": False,
            "erro": "Catálogo indisponível.",
            "fonte": str(CATALOGO_PATH),
        }
    if not gear:
        return {
            "sucesso": False,
            "erro": "Itens de gear indisponíveis.",
            "fonte": str(ITENS_PATH),
        }

    rec = gerar_recomendacoes(
        gear + catalogo,
        classe,
        especialidade,
        prioridade or ["Aceleração", "Crítico", "Maestria"],
        primario_override=primario,
        limite=limite,
    )
    if item_id is not None:
        rec["itens"] = [i for i in rec["itens"] if i.get("id") == item_id]
    rec["sucesso"] = True
    rec["fontes"] = {"gear": str(ITENS_PATH), "catalogo": str(CATALOGO_PATH)}
    return rec


def estado_dados_impl() -> Dict[str, Any]:
    """Mostra arquivos e contagens disponíveis para o agente."""
    arquivos = {}
    for caminho in (
        ITENS_PATH,
        CATALOGO_PATH,
        DATA_DIR / "wowhead_gemas.json",
        DATA_DIR / "wowhead_encantamentos.json",
        DATA_DIR / "wowhead_missivas.json",
        DATA_DIR / "wowhead_season2.md",
        DATA_DIR / "wowhead_catalogo.md",
    ):
        arquivos[caminho.name] = {
            "existe": caminho.exists(),
            "bytes": caminho.stat().st_size if caminho.exists() else 0,
        }

    itens = _carregar_itens(ITENS_PATH)
    catalogo = _carregar_itens(CATALOGO_PATH)
    tipos: Dict[str, int] = {}
    for item in catalogo:
        tipo = item.get("tipo_item") or "outro"
        tipos[tipo] = tipos.get(tipo, 0) + 1

    legacy_dir = DATA_DIR / "_legacy"
    legados_json = (
        sorted(p.name for p in legacy_dir.glob("*.json"))
        if legacy_dir.exists()
        else []
    )

    return {
        "diretorio": str(BASE_DIR),
        "arquivos": arquivos,
        "gear_itens": len(itens),
        "catalogo_itens": len(catalogo),
        "catalogo_por_tipo": tipos,
        "legados_dir": str(legacy_dir),
        "legados_total": len(legados_json),
        "legados_json": legados_json,
    }


# =============================================================================
# Ferramentas MCP
# =============================================================================

@mcp.tool()
async def scrape_pagina(
    url: str,
    wait_for: str = "css:body",
    usar_js: bool = True,
    max_caracteres: int = 25000,
    incluir_html: bool = False,
    apenas_conteudo_principal: bool = True,
    scroll_ate_fim: bool = True,
    auto_clicar_abas: bool = True,
    seletor_abas: str = "",
    clicar_em: str = "",
    extrair_tooltips: bool = True,
    max_tooltips: int = 40,
    espera_tooltip_ms: int = 200,
    espera_apos_clique_ms: int = 800,
    js_customizado: str = "",
    capturar_screenshot: bool = False,
) -> Dict[str, Any]:
    """Raspa uma pagina web com remocao de ruido, deteccao automatica de abas e extracao de tooltips ao passar o mouse.

    Args:
        url: URL completa para raspagem.
        wait_for: Seletor CSS ou texto para esperar antes de extrair (ex: 'css:#content').
        usar_js: Habilita execucao de JavaScript/Playwright.
        max_caracteres: Limite de tamanho retornado para texto.
        incluir_html: Quando True, tambem retorna o codigo HTML.
        apenas_conteudo_principal: Quando True (padrao), remove menus, navbars e rodapes gerando Fit Markdown limpo.
        scroll_ate_fim: Quando True, rola a pagina para carregar conteudo dinamico.
        auto_clicar_abas: Quando True (padrao), detecta e clica automaticamente em todas as abas interativas.
        seletor_abas: Seletor CSS customizado de abas (opcional; se vazio com auto_clicar_abas=True, autodetecta).
        clicar_em: Seletor CSS especifico de botao ou link para clicar antes de raspar.
        extrair_tooltips: Quando True (padrao), passa o mouse (hover) sobre itens e links para revelar e extrair tooltips com atributos.
        max_tooltips: Quantidade maxima de elementos para passar o mouse e ler tooltips (padrao: 40).
        espera_tooltip_ms: Tempo em ms para a tooltip renderizar apos passar o mouse (padrao: 200ms).
        espera_apos_clique_ms: Tempo em ms para aguardar a atualizacao do conteudo apos o clique (padrao 800ms).
        js_customizado: Codigo JavaScript customizado para executar antes da raspagem.
        capturar_screenshot: Quando True, retorna captura de tela em base64.
    """
    return await scrape_pagina_impl(
        url=url,
        wait_for=wait_for,
        usar_js=usar_js,
        max_caracteres=max_caracteres,
        incluir_html=incluir_html,
        apenas_conteudo_principal=apenas_conteudo_principal,
        scroll_ate_fim=scroll_ate_fim,
        auto_clicar_abas=auto_clicar_abas,
        seletor_abas=seletor_abas,
        clicar_em=clicar_em,
        extrair_tooltips=extrair_tooltips,
        max_tooltips=max_tooltips,
        espera_tooltip_ms=espera_tooltip_ms,
        espera_apos_clique_ms=espera_apos_clique_ms,
        js_customizado=js_customizado,
        capturar_screenshot=capturar_screenshot,
    )


@mcp.tool()
async def scrape_todas_as_abas(
    url: str,
    seletor_abas: str = "",
    espera_por_aba_ms: int = 800,
    max_abas: int = 15,
    extrair_tooltips: bool = True,
    max_tooltips: int = 40,
    max_caracteres: int = 35000,
    wait_for: str = "css:body",
    apenas_conteudo_principal: bool = True,
    incluir_html: bool = False,
) -> Dict[str, Any]:
    """Varre e raspa automaticamente TODAS as abas dinamicas de uma pagina SPA.

    Identifica de forma inteligente componentes de abas (role='tab', .nav-tabs, buttons),
    clica em cada aba sequencialmente, aguarda a re-renderizacao e consolida todo o conteudo
    em Markdown organizado com cabecalhos claros para cada aba.

    Args:
        url: URL completa da pagina a ser raspada.
        seletor_abas: Seletor CSS customizado das abas (opcional; autodetecta se vazio).
        espera_por_aba_ms: Tempo em ms de espera para a aba renderizar apos o clique (padrao: 800ms).
        max_abas: Quantidade maxima de abas a varrer (padrao: 15).
        max_caracteres: Limite de caracteres retornados.
        wait_for: Seletor CSS inicial para aguardar antes do clique nas abas.
        apenas_conteudo_principal: Quando True, gera Fit Markdown filtrado sem menus e rodapes.
        incluir_html: Quando True, tambem retorna o HTML consolidado com todas as abas.
    """
    return await scrape_todas_as_abas_impl(
        url=url,
        seletor_abas=seletor_abas,
        espera_por_aba_ms=espera_por_aba_ms,
        max_abas=max_abas,
        extrair_tooltips=extrair_tooltips,
        max_tooltips=max_tooltips,
        max_caracteres=max_caracteres,
        wait_for=wait_for,
        apenas_conteudo_principal=apenas_conteudo_principal,
        incluir_html=incluir_html,
    )


@mcp.tool()
async def map_site(
    url: str,
    apenas_mesmo_dominio: bool = True,
    filtro_padrao: str = "",
    limite: int = 100,
    wait_for: str = "css:body",
) -> Dict[str, Any]:
    """Descobre e mapeia links internos e rotas de um site (estilo Firecrawl map).

    Args:
        url: URL inicial para mapeamento.
        apenas_mesmo_dominio: Quando True, ignora links externos.
        filtro_padrao: Substring ou filtro de rota desejada (ex: '/priest' ou '/m+').
        limite: Quantidade máxima de links retornados.
        wait_for: Seletor CSS para aguardar o carregamento dos links.
    """
    return await map_site_impl(
        url=url,
        apenas_mesmo_dominio=apenas_mesmo_dominio,
        filtro_padrao=filtro_padrao,
        limite=limite,
        wait_for=wait_for,
    )


@mcp.tool()
async def scrape_estruturado(
    url: str,
    schema_css: Optional[Dict[str, Any]] = None,
    campos: Optional[List[str]] = None,
    clicar_em: str = "",
    espera_apos_clique_ms: int = 1000,
    wait_for: str = "css:body",
    usar_js: bool = True,
) -> Dict[str, Any]:
    """Extrai entidades estruturadas em JSON usando CSS Schema com suporte a cliques em abas.

    Args:
        url: URL para extrair dados.
        schema_css: Esquema declarativo do Crawl4AI (baseSelector + fields).
        campos: Lista simplificada de nomes de campos para auto-esquema caso schema_css não seja fornecido.
        clicar_em: Seletor CSS de abas ou botões para clicar antes de extrair.
        espera_apos_clique_ms: Tempo em ms para aguardar a atualização do conteúdo após o clique.
        wait_for: Seletor CSS para esperar antes da extração.
        usar_js: Habilita execução de JavaScript.
    """
    return await scrape_estruturado_impl(
        url=url,
        schema_css=schema_css,
        campos=campos,
        clicar_em=clicar_em,
        espera_apos_clique_ms=espera_apos_clique_ms,
        wait_for=wait_for,
        usar_js=usar_js,
    )


@mcp.tool()
async def scrape_wowhead_item(
    item: str,
    buscar_ingles: bool = True,
    qualidade_craft_min: int = 5,
    exigir_craft: bool = False,
) -> Dict[str, Any]:
    """Extrai um item do Wowhead (ID ou URL) com nome EN/PT-BR e atributos."""
    return await scrape_wowhead_item_impl(
        item, buscar_ingles, qualidade_craft_min, exigir_craft
    )


@mcp.tool()
async def scrape_wowhead_items(
    urls: List[str],
    ilvl_min: int = 305,
    ilvl_max: int = 350,
    max_itens: int = 20,
    buscar_detalhes: bool = True,
    buscar_ingles: bool = True,
    salvar: bool = False,
    qualidade_craft_min: int = 5,
    exigir_craft: bool = False,
) -> Dict[str, Any]:
    """Extrai vários itens/listas do Wowhead e retorna JSON estruturado."""
    return await scrape_wowhead_items_impl(
        urls,
        ilvl_min,
        ilvl_max,
        max_itens,
        buscar_detalhes,
        buscar_ingles,
        salvar,
        qualidade_craft_min,
        exigir_craft,
    )


@mcp.tool()
def listar_catalogo(tipo: str = "", limite: int = 50) -> Dict[str, Any]:
    """Lista o catálogo consolidado, filtrando por tipo_item se informado."""
    return listar_catalogo_impl(tipo, limite)


@mcp.tool()
def recomendar_encantamento_gema(
    classe: str,
    especialidade: str,
    prioridade: Optional[List[str]] = None,
    primario: str = "",
    item_id: Optional[int] = None,
    limite: int = 3,
) -> Dict[str, Any]:
    """Recomenda encantamento/gema por classe, especialidade e prioridade."""
    return recomendar_encantamento_gema_impl(
        classe, especialidade, prioridade, primario, item_id, limite
    )


@mcp.tool()
def estado_dados() -> Dict[str, Any]:
    """Informa arquivos e catálogos disponíveis para o agente."""
    return estado_dados_impl()


def _selftest() -> None:
    print(
        json.dumps(
            {
                "servidor": "crawl4ai-wow",
                "versao": "2.0-aprimorada",
                "estado": estado_dados_impl(),
                "catalogo_amostra": listar_catalogo_impl(limite=3),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def _print_config(formato: str = "roo") -> None:
    servidor = {
        "command": sys.executable,
        "args": [str(BASE_DIR / "mcp_server.py")],
        "env": {
            "PYTHONIOENCODING": "utf-8",
            "PYTHONPATH": str(BASE_DIR),
            "MCP_TRANSPORT": os.getenv("MCP_TRANSPORT", "stdio"),
        },
    }

    if formato == "vscode":
        config = {
            "servers": {
                "crawl4ai-wow": {
                    "type": "stdio",
                    **servidor,
                    "cwd": str(BASE_DIR),
                }
            }
        }
    elif formato == "bloco":
        config = {**servidor, "cwd": str(BASE_DIR)}
    else:
        config = {
            "mcpServers": {
                "crawl4ai-wow": {
                    **servidor,
                    "alwaysAllow": ["estado_dados", "listar_catalogo", "map_site"],
                    "disabled": False,
                }
            }
        }

    print(json.dumps(config, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    _formato = "roo"
    for _arg in sys.argv:
        if _arg.startswith("--formato="):
            _formato = _arg.split("=", 1)[1].strip()

    if "--print-config" in sys.argv:
        _print_config(_formato)
    elif "--selftest" in sys.argv:
        _selftest()
    else:
        transporte = os.getenv("MCP_TRANSPORT", "stdio")
        mcp.run(transport=transporte)  # type: ignore[arg-type]
