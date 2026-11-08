#!/usr/bin/env python3
"""
Teste final do projeto WoWhead Midnight Scraper.
Verifica se todos os componentes estão funcionando corretamente.
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Este arquivo foi movido para `legacy/`. Garante que a raiz do projeto
# continue no sys.path para importar `config` e `scraper_completo_final`.
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

def test_imports():
    """Testa se todas as importações necessárias funcionam."""
    print("[TESTE] Testando importações...")

    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig, LLMExtractionStrategy, LLMConfig
        print("  [OK] crawl4ai importado com sucesso")
    except ImportError as e:
        print(f"  [ERRO] Erro ao importar crawl4ai: {e}")
        return False

    try:
        import litellm
        print("  [OK] litellm importado com sucesso")
    except ImportError as e:
        print(f"  [ERRO] Erro ao importar litellm: {e}")
        return False

    try:
        import streamlit
        print("  [OK] streamlit importado com sucesso")
    except ImportError as e:
        print(f"  [ERRO] Erro ao importar streamlit: {e}")
        return False

    try:
        from config import PARTE1_URLS, PARTE2_URLS, PARTE3_URLS, PARTE4_URLS, PARTE5_URLS
        print("  [OK] config.py importado com sucesso")

        # Verificar URLs
        assert len(PARTE1_URLS) == 5, f"PARTE1_URLS deve ter 5 URLs, tem {len(PARTE1_URLS)}"
        assert len(PARTE2_URLS) == 5, f"PARTE2_URLS deve ter 5 URLs, tem {len(PARTE2_URLS)}"
        assert len(PARTE3_URLS) == 3, f"PARTE3_URLS deve ter 3 URLs, tem {len(PARTE3_URLS)}"
        assert len(PARTE4_URLS) == 6, f"PARTE4_URLS deve ter 6 URLs, tem {len(PARTE4_URLS)}"
        assert len(PARTE5_URLS) == 6, f"PARTE5_URLS deve ter 6 URLs, tem {len(PARTE5_URLS)}"

        print("  [OK] Todas as URLs configuradas corretamente")

    except Exception as e:
        print(f"  [ERRO] Erro ao verificar config.py: {e}")
        return False

    return True

def test_files_exist():
    """Verifica se todos os arquivos necessários existem."""
    print("[TESTE] Verificando arquivos...")

    required_files = [
        "requirements.txt",
        "config.py",
        "scraper.py",
        "scraper_completo_final.py",
        "app_streamlit.py",
        ".env.example",
        "README.md"
    ]

    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"  [OK] {file} existe")
        else:
            print(f"  [ERRO] {file} não encontrado")
            all_exist = False

    return all_exist

def test_data_directory():
    """Verifica se o diretório de dados existe e pode ser criado."""
    print("[TESTE] Verificando diretório de dados...")

    data_dir = Path("data")
    try:
        data_dir.mkdir(exist_ok=True)
        print(f"  [OK] Diretório 'data' criado/verificado")

        # Testar escrita
        test_file = data_dir / "test_write.json"
        with open(test_file, "w") as f:
            json.dump({"test": "success"}, f)

        if test_file.exists():
            test_file.unlink()
            print("  [OK] Permissão de escrita OK")
        else:
            print("  [ERRO] Não foi possível escrever no diretório")
            return False

    except Exception as e:
        print(f"  [ERRO] Erro com diretório 'data': {e}")
        return False

    return True

def test_scraper_class():
    """Testa se a classe do scraper pode ser instanciada."""
    print("[TESTE] Testando classe do scraper...")

    try:
        from scraper_completo_final import WowheadScraperCompleto

        # Testar instanciação
        scraper = WowheadScraperCompleto()
        print("  [OK] WowheadScraperCompleto instanciado com sucesso")

        # Testar métodos básicos
        test_url = "https://www.wowhead.com/pt/item=12345/test-item&bonus=123:456"

        item_id = scraper.extract_item_id_from_url(test_url)
        assert item_id == "12345", f"ID extraído incorreto: {item_id}"
        print("  [OK] extract_item_id_from_url funciona")

        bonus_ids = scraper.extract_bonus_ids_from_url(test_url)
        assert "123" in bonus_ids and "456" in bonus_ids, f"Bonus IDs incorretos: {bonus_ids}"
        print("  [OK] extract_bonus_ids_from_url funciona")

        profissao = scraper.get_profession_from_url("https://www.wowhead.com/pt/guide/midnight/professions/alchemy")
        assert profissao == "Alquimia", f"Profissão incorreta: {profissao}"
        print("  [OK] get_profession_from_url funciona")

        return True

    except Exception as e:
        print(f"  [ERRO] Erro ao testar classe do scraper: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_async_crawler():
    """Testa básico do crawler assíncrono (sem API key)."""
    print("[TESTE] Testando crawler assíncrono...")

    try:
        from crawl4ai import AsyncWebCrawler, BrowserConfig

        # Configuração básica com encoding para Windows
        config = BrowserConfig(
            headless=True,
            enable_stealth=False,  # Desativar para teste rápido
            verbose=False,
            browser_type="chromium",
            # Configurações adicionais para evitar problemas de Unicode
            extra_args=[
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
        )

        # Testar inicialização
        async with AsyncWebCrawler(config=config) as crawler:
            print("  [OK] AsyncWebCrawler inicializado com sucesso")

            # Testar navegação simples (página estática)
            test_url = "https://httpbin.org/html"

            # Configurar encoding para evitar problemas no Windows
            import sys
            import io
            # Salvar stdout original
            old_stdout = sys.stdout
            # Redirecionar para buffer com encoding UTF-8
            sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')

            try:
                result = await crawler.arun(url=test_url)

                # Restaurar stdout
                sys.stdout = old_stdout

                if result.success:
                    print("  [OK] Navegação básica funciona")
                    return True
                else:
                    print(f"  [ERRO] Navegação falhou: {result.error_message}")
                    return False
            except Exception as e:
                # Restaurar stdout em caso de erro
                sys.stdout = old_stdout
                print(f"  [ERRO] Erro durante navegação: {e}")
                return False

    except Exception as e:
        print(f"  [ERRO] Erro ao testar crawler: {e}")
        return False

def test_streamlit_app():
    """Testa se o aplicativo Streamlit pode ser importado."""
    print("[TESTE] Testando aplicativo Streamlit...")

    try:
        # Verificar se o arquivo existe e é válido
        with open("app_streamlit.py", "r", encoding="utf-8") as f:
            content = f.read()

        # Verificar imports básicos
        required_imports = ["streamlit", "asyncio", "json", "pandas"]
        for imp in required_imports:
            if f"import {imp}" in content or f"from {imp}" in content:
                print(f"  [OK] Import {imp} encontrado")
            else:
                print(f"  [AVISO] Import {imp} não encontrado (pode ser opcional)")

        # Verificar funções principais
        required_functions = ["gerar_markdown", "executar_scraping"]
        for func in required_functions:
            if f"def {func}" in content:
                print(f"  [OK] Função {func} encontrada")
            else:
                print(f"  [AVISO] Função {func} não encontrada")

        print("  [OK] Arquivo app_streamlit.py parece válido")
        return True

    except Exception as e:
        print(f"  [ERRO] Erro ao testar app Streamlit: {e}")
        return False

def main():
    """Função principal de teste."""
    print("=" * 60)
    print("TESTE FINAL DO PROJETO WOWHEAD MIDNIGHT SCRAPER")
    print("=" * 60)

    results = []

    # Testes síncronos
    results.append(("Importações", test_imports()))
    results.append(("Arquivos", test_files_exist()))
    results.append(("Diretório de dados", test_data_directory()))
    results.append(("Classe do scraper", test_scraper_class()))
    results.append(("App Streamlit", test_streamlit_app()))

    # Teste assíncrono
    print("\nExecutando teste assíncrono do crawler...")
    try:
        async_result = asyncio.run(test_async_crawler())
        results.append(("Crawler assíncrono", async_result))
    except Exception as e:
        print(f"  ERRO no teste assíncrono: {e}")
        results.append(("Crawler assíncrono", False))

    # Resumo
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "[OK] PASSOU" if success else "[ERRO] FALHOU"
        print(f"{status}: {test_name}")
        if success:
            passed += 1

    print(f"\nResultado: {passed}/{total} testes passaram")

    if passed == total:
        print("\nTODOS OS TESTES PASSARAM! O projeto está pronto para uso.")
        print("\nPróximos passos:")
        print("1. Configure sua chave API DeepSeek no arquivo .env")
        print("2. Execute o scraper completo: python scraper_completo_final.py")
        print("3. Ou execute a interface: streamlit run app_streamlit.py")
        return 0
    else:
        print(f"\n{total - passed} teste(s) falharam. Verifique os problemas acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
