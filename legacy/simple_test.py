#!/usr/bin/env python3
"""Teste simples do scraper sem caracteres Unicode."""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Desativar logging Unicode
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

async def simple_test():
    """Teste simples de conexão."""
    print("Testando conexao basica...")

    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig

        config = BrowserConfig(
            headless=True,
            enable_stealth=True,
            verbose=False,  # Desativar verbose para evitar Unicode
            browser_type="chromium"
        )

        async with AsyncWebCrawler(config=config) as crawler:
            # Testar URL simples
            url = "https://httpbin.org/html"
            print(f"Acessando {url}...")

            result = await crawler.arun(
                url=url,
                word_count_threshold=10
            )

            if result.success:
                print(f"Sucesso! Status: {result.status_code}")
                print(f"Titulo: {result.metadata.get('title', 'N/A')}")
                print(f"Conteudo extraido (primeiros 100 chars): {result.markdown[:100]}...")
            else:
                print(f"Falha: {result.error_message}")

    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())
