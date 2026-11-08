#!/usr/bin/env python3
"""Verificar estratégias de extração disponíveis no Crawl4AI."""

import crawl4ai

print("Classes disponíveis no módulo crawl4ai:")
for name in dir(crawl4ai):
    if 'Strategy' in name:
        cls = getattr(crawl4ai, name)
        print(f"  - {name}: {cls}")

# Verificar também as estratégias de extração
print("\n\nVerificando estratégias de extração específicas:")
try:
    from crawl4ai import LLMExtractionStrategy
    print("✓ LLMExtractionStrategy disponível")
except ImportError as e:
    print(f"✗ LLMExtractionStrategy não disponível: {e}")

try:
    from crawl4ai import CSSExtractionStrategy
    print("✓ CSSExtractionStrategy disponível")
except ImportError as e:
    print(f"✗ CSSExtractionStrategy não disponível: {e}")

try:
    from crawl4ai import RegexExtractionStrategy
    print("✓ RegexExtractionStrategy disponível")
except ImportError as e:
    print(f"✗ RegexExtractionStrategy não disponível: {e}")

# Verificar a classe base
try:
    from crawl4ai import ExtractionStrategy
    print(f"✓ ExtractionStrategy (classe base) disponível")
except ImportError as e:
    print(f"✗ ExtractionStrategy não disponível: {e}")
