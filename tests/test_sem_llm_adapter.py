#!/usr/bin/env python3
"""Testes offline do adapter "Sem LLM" (PACOTE 3 / RC-2).

Prova que o fluxo:
- usa os parsers canônicos (`parse_links_itens`/`finalizar_item_bilingue`);
- NÃO instancia `JsonCssExtractionStrategy` (nem passa `css_selectors`);
- mantém a contagem de erros por parte quando o crawl falha.

Toda a rede é simulada por um `FakeCrawler` com HTML inline.

Execução:
    python -m pytest -q tests/test_sem_llm_adapter.py
    python tests/test_sem_llm_adapter.py        # fallback sem pytest
"""

from __future__ import annotations

import asyncio
import inspect
import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


#: Fixture de listagem/guia com uma variação (item + bonus + ilvl).
HTML_LISTAGEM = """
<html><body>
  <div class="listview">
    <a href="/pt/item=244025/encantamento-da-engenhosidade-rendorei-ferramenta"
       class="listview-cleartext q4"
       data-wowhead="item=244025&bonus=123&ilvl=320">
      Encantamento da Engenhosidade Rendorei
    </a>
  </div>
</body></html>
"""

#: Fixture de página individual de missiva.
HTML_ITEM = """
<html><body>
  <h1 class="heading-size-1 q3">Missiva Talassiana da Engenhosidade</h1>
</body></html>
"""

URL_LISTAGEM = (
    "https://www.wowhead.com/pt/guide/midnight/professions/"
    "engineering-overview-trainer-locations-recipes-tools"
)
URL_ITEM = (
    "https://www.wowhead.com/pt/item=245815/"
    "missiva-talassiana-da-engenhosidade"
)


class FakeResult:
    """Resultado mínimo de `crawler.arun`."""

    def __init__(self, html: str, success: bool, error_message: str = ""):
        self.html = html
        self.success = success
        self.error_message = error_message


class FakeCrawler:
    """Substitui `AsyncWebCrawler` devolvendo HTML inline (sem rede)."""

    html: str = ""
    success: bool = True
    error_message: str = ""
    chamadas: int = 0

    def __init__(self, config=None):
        self.config = config

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return False

    async def arun(self, url: str, config=None):
        FakeCrawler.chamadas += 1
        return FakeResult(
            FakeCrawler.html, FakeCrawler.success, FakeCrawler.error_message
        )


def _com_crawler_fake(fake_cls, funcao):
    """Executa `funcao` com `scraper_sem_llm.AsyncWebCrawler` patcheado."""
    import scraper_sem_llm as ssl

    original = ssl.AsyncWebCrawler
    ssl.AsyncWebCrawler = fake_cls
    try:
        return funcao(ssl)
    finally:
        ssl.AsyncWebCrawler = original


def _coletar_parte1(ssl):
    async def _run():
        scraper = ssl.WowheadScraperSemLLM()
        itens = await scraper.extrair_ferramentas_parte([URL_LISTAGEM], 1)
        return itens, scraper

    return asyncio.run(_run())


# ---------------------------------------------------------------------------
# 1) Parsers canônicos + conversão para dataclass
# ---------------------------------------------------------------------------

def test_extrai_ferramenta_usando_parsers_canonicos() -> None:
    FakeCrawler.html = HTML_LISTAGEM
    FakeCrawler.success = True
    FakeCrawler.error_message = ""

    itens, _ = _com_crawler_fake(FakeCrawler, _coletar_parte1)

    assert len(itens) == 1, f"esperava 1 ferramenta, veio: {itens}"
    item = itens[0]
    assert "Engenhosidade" in item.nome_ptbr, item.nome_ptbr
    assert "item=244025" in item.id_item_completo, item.id_item_completo
    assert item.item_level == 320, item.item_level
    assert item.bonus_ids == ["123"], item.bonus_ids
    assert item.profissao == "Engenharia", item.profissao


# ---------------------------------------------------------------------------
# 2) Nenhuma instanciação de JsonCssExtractionStrategy
# ---------------------------------------------------------------------------

def test_fluxo_nao_instancia_json_css_extraction() -> None:
    import crawl4ai
    import scraper_sem_llm as ssl

    original = crawl4ai.JsonCssExtractionStrategy

    class SpyStrategy:
        chamadas = 0

        def __init__(self, *args, **kwargs):
            SpyStrategy.chamadas += 1

    FakeCrawler.html = HTML_LISTAGEM
    FakeCrawler.success = True
    FakeCrawler.error_message = ""
    crawl4ai.JsonCssExtractionStrategy = SpyStrategy
    try:
        _com_crawler_fake(FakeCrawler, _coletar_parte1)
    finally:
        crawl4ai.JsonCssExtractionStrategy = original

    assert SpyStrategy.chamadas == 0, (
        "JsonCssExtractionStrategy foi instanciada no fluxo Sem LLM"
    )
    fonte = inspect.getsource(ssl)
    literal_proibido = "css_selectors" + "="
    assert literal_proibido not in fonte, (
        "scraper_sem_llm ainda contém o literal " + literal_proibido
    )


# ---------------------------------------------------------------------------
# 3) Falha de crawl é registrada por parte (sem except silencioso)
# ---------------------------------------------------------------------------

def test_falha_de_crawl_registra_erro_por_parte() -> None:
    FakeCrawler.html = ""
    FakeCrawler.success = False
    FakeCrawler.error_message = "403 Forbidden (anti-bot)"

    itens, scraper = _com_crawler_fake(FakeCrawler, _coletar_parte1)

    assert itens == [], itens
    assert scraper.erros.get("parte1"), scraper.erros
    erro = scraper.erros["parte1"][0]
    assert erro["tipo"] == "RuntimeError", erro
    assert "403" in erro["mensagem"], erro


# ---------------------------------------------------------------------------
# 4) Página individual (missiva) via parser canônico puro
# ---------------------------------------------------------------------------

def test_item_unico_missiva_via_coleta() -> None:
    from coleta import itens_de_html
    from scraper_sem_llm import dict_para_missiva

    itens = itens_de_html(URL_ITEM, HTML_ITEM, categoria="missivas")
    assert len(itens) == 1, itens

    missiva = dict_para_missiva(itens[0], url=URL_ITEM)
    assert "Missiva" in missiva.nome_ptbr, missiva.nome_ptbr
    assert missiva.profissao == "Engenharia", missiva.profissao
    assert "item=245815" in missiva.id_item_completo, missiva.id_item_completo


if __name__ == "__main__":  # pragma: no cover - fallback sem pytest
    import traceback

    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if not (nome.startswith("test_") and callable(funcao)):
            continue
        try:
            funcao()
        except Exception:  # noqa: BLE001 - relatório simples
            falhas += 1
            print(f"[FALHOU] {nome}")
            traceback.print_exc()
        else:
            print(f"[OK] {nome}")
    print(f"\n{'FALHAS' if falhas else 'SUCESSO'}: {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
