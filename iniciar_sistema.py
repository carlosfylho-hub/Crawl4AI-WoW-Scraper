#!/usr/bin/env python3
"""
Script de inicialização do sistema WoWhead Midnight Scraper.
Oferece menu interativo para escolher como executar o sistema.
"""

import os
import sys
import subprocess
import webbrowser
import time

def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Imprime o cabeçalho do sistema."""
    print("=" * 60)
    print("SISTEMA WOWHEAD MIDNIGHT SCRAPER")
    print("=" * 60)
    print()

def check_dependencies():
    """Verifica se as dependências estão instaladas."""
    print("[VERIFICACAO] Verificando dependencias...")

    # Verificar Python (já estamos executando em Python)
    print("  [OK] Python encontrado (versao: %s)" % sys.version.split()[0])

    # Verificar dependências principais
    dependencies = ['crawl4ai', 'litellm', 'streamlit', 'playwright']

    all_ok = True
    for dep in dependencies:
        try:
            if dep == 'playwright':
                # Verificar se playwright está instalado
                import playwright
                print(f"  [OK] {dep} encontrado")
            else:
                __import__(dep)
                print(f"  [OK] {dep} encontrado")
        except ImportError:
            print(f"  [AVISO] {dep} não encontrado")
            if dep == 'streamlit':
                print("     Execute: pip install streamlit")
            all_ok = False

    print()
    return all_ok

def run_streamlit():
    """Executa o aplicativo Streamlit."""
    print("\n[WEB] Iniciando interface web Streamlit...")
    print("   O sistema abrira automaticamente no seu navegador.")
    print("   URL: http://localhost:8501")
    print("\n   Aguarde alguns segundos...")

    # Abrir navegador após alguns segundos
    time.sleep(3)
    webbrowser.open("http://localhost:8501")

    # Executar Streamlit
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app_streamlit.py"],
                      check=True)
    except KeyboardInterrupt:
        print("\n\n[INTERRUPCAO] Streamlit interrompido pelo usuario.")
    except Exception as e:
        print(f"\n[ERRO] Erro ao executar Streamlit: {e}")
        print("   Tente executar manualmente: python -m streamlit run app_streamlit.py")

def run_scraper():
    """Executa o scraper completo."""
    print("\n[SCRAPER] Escolha o modo de scraping:")
    print("   1. Pipeline Season 2 (Recomendado) - nomes e ícones (EN/PT-BR)")
    print("   2. Sem LLM - parsers canônicos (não requer API)")

    choice = input("\nEscolha (1-2): ").strip()

    if choice == "1":
        print("\n[SCRAPER] Executando o pipeline Season 2...")
        print("   NOTA: O pipeline bilingue usa os parsers canônicos do projeto.")
        print("         Nenhuma chave de API é necessária.")
        print("\n   O processo pode levar varios minutos.")

        try:
            subprocess.run([sys.executable, "scraper_season2.py"], check=True)
        except KeyboardInterrupt:
            print("\n\n[INTERRUPCAO] Scraper interrompido pelo usuario.")
        except Exception as e:
            print(f"\n[ERRO] Erro ao executar scraper: {e}")

    elif choice == "2":
        print("\n[SCRAPER] Executando scraper SEM LLM...")
        print("   NOTA: Usa os parsers canônicos do projeto.")
        print("         Não requer API key.")
        print("\n   O processo pode levar alguns minutos.")

        try:
            subprocess.run([sys.executable, "scraper_sem_llm.py"], check=True)
        except KeyboardInterrupt:
            print("\n\n[INTERRUPCAO] Scraper interrompido pelo usuario.")
        except Exception as e:
            print(f"\n[ERRO] Erro ao executar scraper: {e}")
    else:
        print("\n[ERRO] Opcao invalida.")

def run_tests():
    """Executa os testes offline ativos (sem rede)."""
    print("\n[TESTES] Executando testes offline do sistema...")
    testes = [
        "test_season2.py",
        "tests/test_smoke_offline.py",
        "tests/test_imports.py",
        "tests/test_app_streamlit.py",
    ]
    falhas = 0
    for teste in testes:
        print(f"\n[TESTES] python {teste}")
        try:
            subprocess.run([sys.executable, teste], check=True)
        except Exception as e:
            falhas += 1
            print(f"[ERRO] {teste}: {e}")

    if falhas:
        print(f"\n[TESTES] {falhas} arquivo(s) com falha.")
    else:
        print("\n[TESTES] Todos os testes offline passaram.")
    print("Testes legados opcionais: python legacy/test_final.py")

def show_menu():
    """Exibe o menu principal."""
    while True:
        clear_screen()
        print_header()

        print("MENU PRINCIPAL")
        print("=" * 40)
        print("1. Interface Web (Streamlit) - Recomendado")
        print("2. Pipeline Season 2 (Terminal)")
        print("3. Scraper Sem LLM (Parsers Canônicos)")
        print("4. Testar Sistema")
        print("5. Ver Documentacao")
        print("6. Sair")
        print()

        choice = input("Escolha uma opcao (1-6): ").strip()

        if choice == "1":
            run_streamlit()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "2":
            run_scraper()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "3":
            # Executar scraper sem LLM diretamente
            print("\n[SCRAPER] Executando scraper SEM LLM...")
            print("   NOTA: Usa os parsers canônicos do projeto.")
            print("         Não requer API key.")
            print("\n   O processo pode levar alguns minutos.")

            try:
                subprocess.run([sys.executable, "scraper_sem_llm.py"], check=True)
            except KeyboardInterrupt:
                print("\n\n[INTERRUPCAO] Scraper interrompido pelo usuario.")
            except Exception as e:
                print(f"\n[ERRO] Erro ao executar scraper: {e}")

            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "4":
            run_tests()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "5":
            show_documentation()
            input("\nPressione ENTER para voltar ao menu...")
        elif choice == "6":
            print("\nSistema encerrado. Ate logo!")
            break
        else:
            print("\n[ERRO] Opcao invalida! Tente novamente.")
            time.sleep(1)

def show_documentation():
    """Mostra informações de documentação."""
    clear_screen()
    print_header()

    print("DOCUMENTACAO RAPIDA")
    print("=" * 40)
    print("\nESTRUTURA DO PROJETO (ativa):")
    print("  • app_streamlit.py      - Interface web")
    print("  • scraper_season2.py    - Pipeline Season 2 (nomes e icones)")
    print("  • scraper_sem_llm.py    - Fluxo sem LLM (parsers canonicos)")
    print("  • coleta.py             - Rede + parsers do fluxo Sem LLM")
    print("  • wow_season2.py        - Parsers/utilitarios testaveis")
    print("  • mcp_server.py         - Servidor MCP (stdio)")
    print("  • runtime.py            - Workaround de event loop no Windows")
    print("  • config.py             - URLs e configuracoes")
    print("  • data/                 - Saidas canonicas (ver data/README.md)")
    print("  • legacy/               - Scrapers/testes antigos (nao usados)")

    print("\nCONFIGURACAO NECESSARIA:")
    print("  1. Copie .env.example para .env (opcional; S2/Sem LLM nao exigem)")
    print("  2. Execute: pip install -r requirements.txt")
    print("  3. Execute: python -m playwright install chromium")

    print("\nEXECUCAO RAPIDA:")
    print("  • Interface web: python -m streamlit run app_streamlit.py")
    print("  • Pipeline Season 2: python scraper_season2.py")
    print("  • Sem LLM: python scraper_sem_llm.py")
    print("  • MCP selftest: python mcp_server.py --selftest")
    print("  • MCP config local: python mcp_server.py --print-config")
    print("  • Testes offline: python test_season2.py && python tests/test_imports.py")

    print("\nSUPORTE:")
    print("  • Consulte README.md para detalhes completos")
    print("  • Verifique se todas as dependencias estao instaladas")

def main():
    """Função principal."""
    try:
        # Verificar dependências
        if not check_dependencies():
            print("\n[AVISO] Algumas dependencias podem estar faltando.")
            print("   Consulte README.md para instrucoes de instalacao.")
            input("\nPressione ENTER para continuar...")

        # Mostrar menu
        show_menu()

    except KeyboardInterrupt:
        print("\n\n[INTERRUPCAO] Sistema interrompido pelo usuario.")
    except Exception as e:
        print(f"\n[ERRO] Erro inesperado: {e}")
        print("   Por favor, reporte este erro.")
        input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    main()
