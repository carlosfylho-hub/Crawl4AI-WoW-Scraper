#!/usr/bin/env python3
"""
Script de execução do scraper WoWhead Midnight.

Redirecionado para o **pipeline Season 2** (`scraper_season2.py`), que extrai
nomes e ícones (EN/PT-BR) com os parsers canônicos do projeto. Os scrapers
LLM antigos foram movidos para `legacy/` e não são mais usados por este
entrypoint.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

from runtime import configurar_event_loop_windows

# Configurar encoding para Windows
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001 - best-effort no terminal
        pass

load_dotenv()


async def main():
    """Executa o pipeline Season 2 e salva JSON + Markdown."""
    print("=== Scraper WoWhead Midnight — Pipeline Season 2 ===")
    print()

    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from scraper_season2 import WowheadSeason2Scraper
    except ImportError as e:
        print(f"ERRO ao importar o pipeline Season 2: {e}")
        print("Certifique-se de que as dependências estão instaladas.")
        return

    json_path = os.getenv(
        "SEASON2_JSON", os.path.join("data", "wowhead_itens_season2.json")
    )
    md_path = os.getenv(
        "SEASON2_MD", os.path.join("data", "wowhead_season2.md")
    )
    os.makedirs(os.path.dirname(json_path) or "data", exist_ok=True)

    print(f"JSON de saída: {json_path}")
    print(f"Markdown de saída: {md_path}")
    print()

    async with WowheadSeason2Scraper() as scraper:
        resultado = await scraper.executar()
        caminho_json = scraper.salvar_resultados(resultado, json_path, md_path)

    metadata = resultado.get("metadata", {}) if isinstance(resultado, dict) else {}
    print()
    print("=== EXECUÇÃO CONCLUÍDA ===")
    print(f"Total de itens: {metadata.get('total_itens', 0)}")
    print(f"JSON salvo: {caminho_json}")


if __name__ == "__main__":
    # Playwright/AsyncWebCrawler precisa de ProactorEventLoop no Windows.
    configurar_event_loop_windows()
    asyncio.run(main())
