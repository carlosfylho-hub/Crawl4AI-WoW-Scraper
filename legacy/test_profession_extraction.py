#!/usr/bin/env python3
"""Teste da extração de ferramentas de profissão."""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler, BrowserConfig, LLMExtractionStrategy, LLMConfig

# Movido para `legacy/`: mantém a raiz do projeto no sys.path para `config`.
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

try:
    from config import LLM_PROVIDER
except ImportError:  # fallback para execução isolada
    LLM_PROVIDER = "deepseek/deepseek-chat"

load_dotenv()

async def test_profession_extraction():
    """Testa a extração de uma página de ferramentas de profissão."""
    print("Testando extração de ferramentas de profissão...")

    # Configuração do navegador
    config = BrowserConfig(
        headless=True,
        enable_stealth=True,
        verbose=False,
        browser_type="chromium"
    )

    # Configuração do LLM
    llm_config = LLMConfig(
        provider=LLM_PROVIDER,
        api_token=os.getenv("DEEPSEEK_API_KEY"),
        temperature=0.1,
        max_tokens=2000
    )

    # Schema de extração
    extraction_schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "ID do item"},
                "nome_ptbr": {"type": "string", "description": "Nome do item em português"},
                "profissao": {"type": "string", "description": "Profissão (mineração, skinning, tailoring, etc.)"},
                "atributos_secundarios": {
                    "type": "object",
                    "description": "Atributos secundários e valores",
                    "additionalProperties": {"type": "string"}
                }
            },
            "required": ["id", "nome_ptbr", "profissao"]
        }
    }

    # URL de teste (uma das URLs fornecidas)
    test_url = "https://www.wowhead.com/pt/guide/midnight/professions/mining-overview-trainer-locations-ores-tools#accessories-tools"

    print(f"Acessando: {test_url}")

    async with AsyncWebCrawler(config=config) as crawler:
        # Primeiro, tentar extrair com seletor CSS para economizar tokens
        print("Tentando extração com seletor CSS...")

        result = await crawler.arun(
            url=test_url,
            extraction_strategy=LLMExtractionStrategy(
                llm_config=llm_config,
                instruction="""Extraia todos os itens da tabela 'Accessories & Tools'.
Para cada item, capture:
1. ID do item (do link href, ex: /item=12345)
2. Nome em português (texto do link)
3. Profissão (mineração, skinning, tailoring, etc.)
4. Atributos secundários e seus valores (se houver)

Retorne como uma lista de objetos JSON com campos: id, nome_ptbr, profissao, atributos_secundarios.

Exemplo:
[
  {
    "id": "12345",
    "nome_ptbr": "Picareta Avançada",
    "profissao": "mineração",
    "atributos_secundarios": {
      "Crítico": "+50",
      "Versatilidade": "+30"
    }
  }
]""",
                schema=extraction_schema
            )
        )

        if result.success:
            print(f"Sucesso! Status: {result.status_code}")
            print(f"Conteúdo extraído:")

            if result.extracted_content:
                import json
                try:
                    data = json.loads(result.extracted_content)
                    print(f"Total de itens extraídos: {len(data) if isinstance(data, list) else 'N/A'}")

                    # Mostrar alguns itens
                    if isinstance(data, list) and len(data) > 0:
                        print("\nPrimeiros 3 itens:")
                        for i, item in enumerate(data[:3]):
                            print(f"\nItem {i+1}:")
                            print(f"  ID: {item.get('id', 'N/A')}")
                            print(f"  Nome: {item.get('nome_ptbr', 'N/A')}")
                            print(f"  Profissão: {item.get('profissao', 'N/A')}")
                            atributos = item.get('atributos_secundarios', {})
                            if atributos:
                                print(f"  Atributos: {atributos}")
                except json.JSONDecodeError as e:
                    print(f"Erro ao decodificar JSON: {e}")
                    print(f"Conteúdo bruto: {result.extracted_content[:500]}...")
            else:
                print("Nenhum conteúdo extraído.")
        else:
            print(f"Falha: {result.error_message}")

    print("\nTeste concluído.")

async def main():
    """Função principal."""
    print("=== Teste de Extração de Ferramentas de Profissão ===")

    # Verificar chave de API
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("AVISO: DEEPSEEK_API_KEY não configurada.")
        print("O teste funcionará, mas a extração com LLM pode falhar.")
        print("Configure a chave no arquivo .env")

    await test_profession_extraction()

if __name__ == "__main__":
    asyncio.run(main())
