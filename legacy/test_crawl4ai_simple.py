#!/usr/bin/env python3
"""Teste simples do Crawl4AI sem Playwright."""

import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig

async def test_crawler():
    """Testa o crawler básico."""
    print("Testando Crawl4AI...")

    try:
        # Configuração simples
        config = BrowserConfig(
            headless=True,
            enable_stealth=True,
            verbose=False,
            browser_type="chromium"
        )

        async with AsyncWebCrawler(config=config) as crawler:
            print("✅ Crawler inicializado com sucesso")

            # Testar uma URL simples
            result = await crawler.arun("https://httpbin.org/html")

            if result.success:
                print(f"✅ Scraping bem-sucedido")
                print(f"   Título: {result.metadata.get('title', 'N/A')}")
                print(f"   Conteúdo: {len(result.markdown or '')} caracteres")
            else:
                print(f"❌ Scraping falhou: {result.error_message}")

    except Exception as e:
        print(f"❌ Erro ao testar crawler: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_crawler())
