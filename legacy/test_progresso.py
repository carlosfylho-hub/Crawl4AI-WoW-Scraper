#!/usr/bin/env python3
"""Teste do sistema de progresso."""

import asyncio
import sys
import time
from pathlib import Path

# Movido para `legacy/`: mantém a raiz do projeto no sys.path.
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from scraper_sem_llm import WowheadScraperSemLLM

def progress_callback(message: str, current: int = None, total: int = None):
    """Callback de progresso para teste."""
    if current is not None and total is not None:
        percent = (current / total) * 100
        print(f"[PROGRESSO] {message} - {current}/{total} ({percent:.1f}%)")
    else:
        print(f"[PROGRESSO] {message}")

async def test_progresso():
    """Testa o sistema de progresso."""
    print("Testando sistema de progresso...")

    # Criar scraper com callback de progresso
    scraper = WowheadScraperSemLLM(progress_callback=progress_callback)

    # Testar callback diretamente
    print("\n1. Testando callback direto:")
    scraper._update_progress("Teste 1", 10, 100)
    scraper._update_progress("Teste 2", 50, 100)
    scraper._update_progress("Teste 3", 100, 100)

    # Testar extração de uma URL (simulada)
    print("\n2. Testando extração simulada:")

    # Simular progresso
    urls = ["url1", "url2", "url3"]
    for i, url in enumerate(urls, 1):
        scraper._update_progress(f"Processando URL {i}/{len(urls)}", i, len(urls))
        time.sleep(0.5)  # Simular trabalho

    print("\n✅ Teste de progresso concluído!")

if __name__ == "__main__":
    asyncio.run(test_progresso())
