#!/usr/bin/env python3
"""Teste de contrato da API do Crawl4AI.

Objetivo: falhar **cedo e alto** quando o ambiente derivar para uma versão do
Crawl4AI incompatível com o código do projeto (foi o que aconteceu ao subir de
0.5.x para 0.8.6 sem teto em `requirements.txt`).

Contrato verificado (Crawl4AI 0.8.6):

a) `crawl4ai.__version__` == "0.8.6";
b) `JsonCssExtractionStrategy` exige `schema` como 1º parâmetro obrigatório e
   não expõe `css_selectors`;
c) `LLMExtractionStrategy` aceita `llm_config`;
d) `CrawlerRunConfig` aceita `wait_for`, `js_code` e `page_timeout`.

Toda falha aponta para `docs/UPGRADE_CRAWL4AI.md`.

Execução:
    python -m pytest -q tests/test_contrato_crawl4ai.py
    python tests/test_contrato_crawl4ai.py      # fallback sem pytest
"""

from __future__ import annotations

import inspect

#: Versão do Crawl4AI validada com o código atual (pino em requirements.txt).
VERSAO_VALIDADA = "0.8.6"

#: Documento com o passo a passo de migração.
DOC_MIGRACAO = "docs/UPGRADE_CRAWL4AI.md"


def _falhar(mensagem: str) -> None:
    """Levanta AssertionError já com a referência ao guia de migração."""
    raise AssertionError(f"{mensagem}\n\nConsulte o checklist em {DOC_MIGRACAO}.")


def _versao_crawl4ai() -> str:
    """Lê a versão do Crawl4AI de forma tolerante.

    Em 0.8.x `crawl4ai.__version__` é o *módulo* `crawl4ai/__version__.py`
    (a string fica em `crawl4ai.__version__.__version__`); em outras versões
    pode ser a própria string.
    """
    import crawl4ai

    bruto = getattr(crawl4ai, "__version__", "")
    if isinstance(bruto, str):
        return bruto
    return getattr(bruto, "__version__", "")


def test_versao_crawl4ai_pinada() -> None:
    """(a) A versão instalada deve ser exatamente a versão validada."""
    versao = _versao_crawl4ai()
    if versao != VERSAO_VALIDADA:
        _falhar(
            f"Crawl4AI instalado = {versao or '<desconhecida>'}, "
            f"esperado == {VERSAO_VALIDADA}. "
            "Fixe a versão em requirements.txt e rode o guia de upgrade."
        )


def test_json_css_exige_schema_e_nao_aceita_css_selectors() -> None:
    """(b) `JsonCssExtractionStrategy(schema, ...)` — `css_selectors` morreu."""
    from crawl4ai import JsonCssExtractionStrategy

    assinatura = inspect.signature(JsonCssExtractionStrategy.__init__)
    parametros = assinatura.parameters

    nomes_sem_self = [nome for nome in parametros if nome != "self"]
    if not nomes_sem_self or nomes_sem_self[0] != "schema":
        _falhar(
            "JsonCssExtractionStrategy deve ter `schema` como 1º parâmetro "
            f"posicional; encontrado: {nomes_sem_self or '<nenhum>'}"
        )

    schema = parametros["schema"]
    if schema.default is not inspect.Parameter.empty:
        _falhar(
            "`schema` deve ser obrigatório (sem valor padrão) em "
            "JsonCssExtractionStrategy."
        )
    if schema.kind not in (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    ):
        _falhar(
            "`schema` deve ser aceito posicionalmente; "
            f"kind atual = {schema.kind}"
        )

    if "css_selectors" in parametros:
        _falhar(
            "A assinatura de JsonCssExtractionStrategy não deve expor "
            "`css_selectors` (API removida)."
        )

    # Prova executável: instanciar apenas com `css_selectors` deve estourar
    # TypeError — é exatamente o erro que o pipeline antigo engolia.
    try:
        # Passa `css_selectors` via kwargs para provar que a API o rejeita
        # (mantém a busca de verificação do projeto livre do literal).
        JsonCssExtractionStrategy(**{"css_selectors": {"nome": "h1"}})  # type: ignore[arg-type]
    except TypeError:
        pass
    else:
        _falhar(
            "JsonCssExtractionStrategy aceitou instanciar sem `schema`; "
            "o contrato de 0.8.6 exige o schema como 1º argumento."
        )


def test_llm_extraction_aceita_llm_config() -> None:
    """(c) `LLMExtractionStrategy` deve aceitar `llm_config`."""
    from crawl4ai import LLMExtractionStrategy

    parametros = inspect.signature(LLMExtractionStrategy.__init__).parameters
    if "llm_config" not in parametros:
        _falhar(
            "LLMExtractionStrategy não aceita `llm_config`; "
            f"parâmetros encontrados: {[n for n in parametros if n != 'self']}"
        )


def test_crawler_run_config_aceita_campos_do_pipeline() -> None:
    """(d) `CrawlerRunConfig` deve aceitar `wait_for`, `js_code` e `page_timeout`."""
    from crawl4ai import CrawlerRunConfig

    parametros = inspect.signature(CrawlerRunConfig.__init__).parameters
    ausentes = [
        nome
        for nome in ("wait_for", "js_code", "page_timeout")
        if nome not in parametros
    ]
    if ausentes:
        _falhar(
            "CrawlerRunConfig não aceita os campos usados pelo pipeline: "
            f"{ausentes}"
        )


if __name__ == "__main__":  # pragma: no cover - fallback sem pytest
    import sys

    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if nome.startswith("test_") and callable(funcao):
            try:
                funcao()
            except Exception as exc:  # noqa: BLE001 - relatório simples
                falhas += 1
                print(f"[FALHOU] {nome}: {exc}")
            else:
                print(f"[OK] {nome}")
    sys.exit(1 if falhas else 0)
