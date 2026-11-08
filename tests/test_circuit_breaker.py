#!/usr/bin/env python3
"""Testes offline do circuit breaker anti-bot (PKG-3 / F-04).

Cobrem, sem rede:

a) 5 falhas 403 consecutivas abrem o breaker; a 6ª chamada **não** executa
   crawl, aplica a pausa (60s por default) e registra pausa/motivo;
b) um sucesso reseta o contador e fecha o breaker;
c) a categoria abortada aparece em `metadata.falhas`.

Execução:
    python -m pytest -q tests/test_circuit_breaker.py
    python tests/test_circuit_breaker.py      # fallback sem pytest
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any, List

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from scraper_season2 import (  # noqa: E402
    CircuitBreakerAntiBot,
    WowheadSeason2Scraper,
)

URL_LISTA = "https://www.wowhead.com/pt/items?min-ilvl=305&max-ilvl=350"
ITEM_FALSO = {
    "id": "250001",
    "nome": "Lâmina de Teste",
    "bonus_ids": ["12838"],
    "_categoria": "gear",
}


class Resultado403:
    """Imita o `arun` do Crawl4AI com resposta 403."""

    success = False
    status_code = 403
    error_message = "crawl falhou: 403 Forbidden"
    html = "<html><body>403 Forbidden</body></html>"
    media: dict = {}


class ResultadoDesafio:
    """Imita a página de desafio anti-bot (Cloudflare)."""

    success = True
    status_code = 200
    error_message = ""
    html = (
        "<html><head><title>Just a moment...</title></head>"
        "<body>checking your browser</body></html>"
    )
    media: dict = {}


class CrawlerFalso:
    """Conta as chamadas a `arun` e devolve sempre o resultado configurado."""

    def __init__(self, resultado: Any = None, resultados: Any = None):
        self.chamadas = 0
        self.urls: List[str] = []
        self._resultado = resultado or Resultado403()
        self._resultados = list(resultados or [])

    async def arun(self, url: str = "", config: Any = None) -> Any:
        self.chamadas += 1
        self.urls.append(url)
        if self._resultados:
            return self._resultados.pop(0)
        return self._resultado


async def _sem_espera(_segundos: float) -> None:
    """Substitui `asyncio.sleep` nos testes (pausa instantânea)."""
    return None


def _scraper(crawler: Any, **kwargs: Any) -> WowheadSeason2Scraper:
    """Instancia o scraper com sleeps/esperas desativados e crawler falso."""
    parametros = {
        "buscar_detalhes": False,
        "tentativas_crawl": 1,
        "esperas_retry": (0.0,),
        "limite_falhas_consecutivas": 5,
        "pausa_circuit_breaker": 60.0,
        "sleep": _sem_espera,
    }
    parametros.update(kwargs)
    scraper = WowheadSeason2Scraper(**parametros)  # type: ignore[arg-type]
    scraper.crawler = crawler  # type: ignore[assignment]
    return scraper


# ---------------------------------------------------------------------------
# (a) 5 falhas 403 -> 6ª chamada bloqueada
# ---------------------------------------------------------------------------


def test_seis_falhas_403_acionam_circuit_breaker() -> None:
    crawler = CrawlerFalso(Resultado403())
    scraper = _scraper(crawler)

    for _ in range(5):
        url, html, media = asyncio.run(scraper._crawl_locale(ITEM_FALSO, "ptbr"))
        assert (html, media) == ("", [])

    assert crawler.chamadas == 5, crawler.chamadas
    assert scraper.circuito.deve_bloquear()
    assert scraper.circuito.falhas_consecutivas == 5
    assert scraper.circuito.pausa_realizada is False

    # 6ª chamada: NÃO executa crawl; aplica a pausa e registra o motivo.
    url, html, media = asyncio.run(scraper._crawl_locale(ITEM_FALSO, "ptbr"))
    assert crawler.chamadas == 5, "a 6ª chamada não deve executar crawl"
    assert html == "" and media == []
    assert scraper.circuito.pausa_realizada is True
    assert scraper.circuito.pausas == 1
    assert scraper.circuito.motivo
    assert "403" in scraper.circuito.motivo

    erros = " ".join(f.get("erro", "") for f in scraper._falhas_circuito)
    assert "circuit breaker" in erros, scraper._falhas_circuito


def test_desafio_antibot_tambem_conta_como_falha() -> None:
    """Página de desafio (HTTP 200) também abre o breaker após 5 tentativas."""
    crawler = CrawlerFalso(ResultadoDesafio())
    scraper = _scraper(crawler)

    for _ in range(5):
        asyncio.run(scraper._crawl_locale(ITEM_FALSO, "ptbr"))

    assert scraper.circuito.deve_bloquear()
    assert crawler.chamadas == 5


# ---------------------------------------------------------------------------
# (b) sucesso reseta o contador
# ---------------------------------------------------------------------------


def test_sucesso_reseta_contador_do_breaker() -> None:
    breaker = CircuitBreakerAntiBot()
    for _ in range(4):
        assert breaker.registrar_falha() == "continuar"
    assert breaker.falhas_consecutivas == 4

    breaker.registrar_sucesso()
    assert breaker.falhas_consecutivas == 0
    assert breaker.deve_bloquear() is False

    assert breaker.registrar_falha() == "continuar"
    assert breaker.falhas_consecutivas == 1

    # 5ª falha abre o breaker.
    for _ in range(4):
        breaker.registrar_falha()
    assert breaker.deve_bloquear() is True
    assert breaker.limite_falhas == 5
    assert breaker.pausa_segundos == 60.0
    assert breaker.resumo()["abortado"] is True


def test_sucesso_no_crawl_reduz_falhas_consecutivas() -> None:
    """Um crawl bem-sucedido no meio da sequência zera o contador."""
    crawler = CrawlerFalso(
        resultados=[
            Resultado403(),
            Resultado403(),
            type(
                "ResultadoOk",
                (),
                {
                    "success": True,
                    "status_code": 200,
                    "error_message": "",
                    "html": "<html><h1 class='heading-size-1'>Item</h1></html>",
                    "media": {},
                },
            )(),
        ]
    )
    scraper = _scraper(crawler)

    asyncio.run(scraper._crawl_locale(ITEM_FALSO, "ptbr"))
    asyncio.run(scraper._crawl_locale(ITEM_FALSO, "ptbr"))
    assert scraper.circuito.falhas_consecutivas == 2

    url, html, media = asyncio.run(scraper._crawl_locale(ITEM_FALSO, "ptbr"))
    assert html, "o terceiro crawl deveria retornar HTML"
    assert scraper.circuito.falhas_consecutivas == 0
    assert scraper.circuito.deve_bloquear() is False


# ---------------------------------------------------------------------------
# (c) metadata
# ---------------------------------------------------------------------------


def test_categoria_abortada_entra_em_metadata_falhas() -> None:
    crawler = CrawlerFalso(Resultado403())
    scraper = _scraper(crawler)

    async def coletar_falso(url: str, categoria: str = ""):
        for _ in range(5):
            scraper.circuito.registrar_falha()
        return [], None

    scraper.coletar_url = coletar_falso  # type: ignore[assignment]

    resultado = asyncio.run(
        scraper.executar_por_categorias({"Gear": [URL_LISTA, URL_LISTA + "2"]})
    )
    metadata = resultado["metadata"]
    erros = " ".join(f.get("erro", "") for f in metadata["falhas"])
    assert "circuit breaker" in erros, metadata["falhas"]
    assert metadata["circuit_breaker"]["abortado"] is True
    assert metadata["circuit_breaker"]["limite"] == 5
    assert "tentativas_wait" in metadata
    assert "retry_scroll_usado" in metadata


if __name__ == "__main__":  # pragma: no cover - fallback sem pytest
    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if not (nome.startswith("test_") and callable(funcao)):
            continue
        try:
            funcao()
        except Exception as exc:  # noqa: BLE001 - relatório simples
            falhas += 1
            print(f"[FAIL] {nome}: {exc}")
        else:
            print(f"[OK] {nome}")
    print(f"\n{'FALHAS' if falhas else 'SUCESSO'}: {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
