#!/usr/bin/env python3
"""Teste básico do AsyncWebCrawler com BrowserConfig."""

import asyncio
import os
from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler, BrowserConfig

load_dotenv()

async def test_crawler():
    """Testa a configuração básica do crawler."""
    print("Testando AsyncWebCrawler com BrowserConfig...")

    # Configuração do navegador
    config = BrowserConfig(
        headless=True,
        enable_stealth=True,
        verbose=True,
        browser_type="chromium",
        viewport_width=1920,
        viewport_height=1080,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    # Criar crawler
    crawler = AsyncWebCrawler(config=config)

    try:
        await crawler.__aenter__()
        print("Crawler iniciado com sucesso!")

        # Testar uma URL simples
        url = "https://httpbin.org/html"
        print(f"Acessando {url}...")

        result = await crawler.arun(
            url=url,
            word_count_threshold=10
        )

        if result.success:
            print(f"Sucesso! Status: {result.status_code}")
            print(f"Título: {result.metadata.get('title', 'N/A')}")
            print(f"Conteúdo extraído (primeiros 200 chars): {result.markdown[:200]}...")
        else:
            print(f"Falha: {result.error_message}")

    except Exception as e:
        print(f"Erro durante o teste: {e}")
    finally:
        await crawler.__aexit__(None, None, None)
        print("Crawler finalizado.")

if __name__ == "__main__":
    asyncio.run(test_crawler())
