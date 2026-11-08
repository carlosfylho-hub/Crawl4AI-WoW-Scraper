#!/usr/bin/env python3
"""Teste da lógica de navegação para WoWhead."""

import re
from urllib.parse import urlparse, parse_qs

def extract_item_id_from_url(url: str) -> str:
    """Extrai o ID do item da URL do WoWhead."""
    # Padrões de URL do WoWhead: /item=12345 ou /item=12345&bonus=...
    match = re.search(r'item=(\d+)', url)
    if match:
        return match.group(1)
    return ""

def extract_bonus_ids_from_url(url: str) -> list:
    """Extrai todos os bonus IDs da URL."""
    bonus_ids = []

    # Extrair parâmetros do caminho (WoWhead usa formato /item=12345&bonus=... no caminho)
    # Encontrar tudo após 'item=' até o final ou próximo '#'
    match = re.search(r'item=\d+(.*?)(?:#|$)', url)
    if match:
        params_str = match.group(1)
        # Extrair parâmetros como &bonus=... &gems=... &ench=...
        param_pattern = r'&(bonus|gems|ench)=([^&]+)'
        for param_match in re.finditer(param_pattern, params_str):
            param_name = param_match.group(1)
            param_value = param_match.group(2)

            # Separar valores por : ou ,
            for id_val in re.split(r'[:,]', param_value):
                if id_val and id_val.isdigit():
                    bonus_ids.append(id_val)

    return bonus_ids

def test_url_parsing():
    """Testa a extração de IDs de URLs do WoWhead."""
    test_cases = [
        {
            "url": "https://www.wowhead.com/pt/item=12345",
            "expected_id": "12345",
            "expected_bonus": []
        },
        {
            "url": "https://www.wowhead.com/pt/item=12345&bonus=6789",
            "expected_id": "12345",
            "expected_bonus": ["6789"]
        },
        {
            "url": "https://www.wowhead.com/pt/item=12345&bonus=6789:1234",
            "expected_id": "12345",
            "expected_bonus": ["6789", "1234"]
        },
        {
            "url": "https://www.wowhead.com/pt/item=12345&gems=9876&ench=5432",
            "expected_id": "12345",
            "expected_bonus": ["9876", "5432"]
        },
        {
            "url": "https://www.wowhead.com/pt/item=12345&bonus=6789,1234,5678",
            "expected_id": "12345",
            "expected_bonus": ["6789", "1234", "5678"]
        }
    ]

    print("Testando extração de IDs do WoWhead...")
    print("=" * 60)

    all_passed = True
    for i, test in enumerate(test_cases, 1):
        url = test["url"]
        expected_id = test["expected_id"]
        expected_bonus = test["expected_bonus"]

        item_id = extract_item_id_from_url(url)
        bonus_ids = extract_bonus_ids_from_url(url)

        id_passed = item_id == expected_id
        bonus_passed = bonus_ids == expected_bonus

        print(f"Teste {i}: {url}")
        print(f"  ID extraído: {item_id} (esperado: {expected_id}) {'[OK]' if id_passed else '[ERRO]'}")
        print(f"  Bonus IDs: {bonus_ids} (esperado: {expected_bonus}) {'[OK]' if bonus_passed else '[ERRO]'}")

        if not (id_passed and bonus_passed):
            all_passed = False

        print()

    print("=" * 60)
    if all_passed:
        print("[OK] Todos os testes passaram!")
    else:
        print("[ERRO] Alguns testes falharam.")

    return all_passed

def test_quality_filters():
    """Testa os filtros de qualidade."""
    print("\nTestando filtros de qualidade...")
    print("=" * 60)

    # Configurações
    quality_rank = 5
    rare_item_level = 232
    epic_item_level_min = 250

    test_items = [
        {"qualidade": 5, "item_level": 200, "tipo": "raro", "deve_passar": True},
        {"qualidade": 5, "item_level": 232, "tipo": "raro", "deve_passar": True},
        {"qualidade": 5, "item_level": 250, "tipo": "épico", "deve_passar": True},
        {"qualidade": 5, "item_level": 255, "tipo": "épico", "deve_passar": True},
        {"qualidade": 4, "item_level": 255, "tipo": "épico", "deve_passar": False},  # Qualidade errada
        {"qualidade": 5, "item_level": 230, "tipo": "raro", "deve_passar": False},  # ILvl baixo para raro
        {"qualidade": 5, "item_level": 245, "tipo": "épico", "deve_passar": False},  # ILvl baixo para épico
    ]

    for item in test_items:
        passes = True

        # Verificar qualidade
        if item["qualidade"] != quality_rank:
            passes = False

        # Verificar item level baseado no tipo
        if item["tipo"] == "raro" and item["item_level"] != rare_item_level:
            passes = False
        elif item["tipo"] == "épico" and item["item_level"] < epic_item_level_min:
            passes = False

        expected = item["deve_passar"]
        status = "[OK]" if passes == expected else "[ERRO]"

        print(f"Item: Qualidade {item['qualidade']}, ILvl {item['item_level']}, Tipo {item['tipo']}")
        print(f"  Passa filtro: {passes} (esperado: {expected}) {status}")

    print("=" * 60)

def main():
    """Função principal."""
    print("=== Teste da Lógica de Navegação WoWhead ===")

    # Testar parsing de URLs
    url_tests_passed = test_url_parsing()

    # Testar filtros de qualidade
    test_quality_filters()

    # Demonstrar variações
    print("\nDemonstração de variações de atributos:")
    print("=" * 60)

    base_urls = [
        "https://www.wowhead.com/pt/item=12345",
        "https://www.wowhead.com/pt/item=12345&bonus=6789",
        "https://www.wowhead.com/pt/item=12345&bonus=6789:1234:5678",
    ]

    for url in base_urls:
        item_id = extract_item_id_from_url(url)
        bonus_ids = extract_bonus_ids_from_url(url)

        print(f"URL: {url}")
        print(f"  ID do item: {item_id}")
        print(f"  IDs de bônus: {bonus_ids}")
        print(f"  Total de variações: {max(1, len(bonus_ids))}")
        print()

    print("=" * 60)
    print("\nConclusão:")
    print("A lógica de navegação está implementada para:")
    print("1. Extrair IDs de itens das URLs")
    print("2. Identificar variações através de parâmetros de bônus")
    print("3. Gerar entradas separadas para cada variação")

    if url_tests_passed:
        print("\n[OK] Pronto para implementar no scraper principal.")
    else:
        print("\n[ERRO] Necessário corrigir a lógica de parsing.")

if __name__ == "__main__":
    main()
