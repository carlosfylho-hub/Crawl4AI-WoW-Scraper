#!/usr/bin/env python3
"""Testes offline das condições de `wait_for` e da config de browser (PKG-3).

Cobrem, sem qualquer chamada de rede:

a) `_run_config` para URL de listagem -> `wait_for` com `.listview-row` **e**
   `tr[data-id]` (JS-01/F-01);
b) `_run_config` para URL de item (`item=123`) -> `wait_for` com
   `h1.heading-size-1` (JS-01);
c) `_JS_LAZY_LOAD` contém `mouseover`, é protegido por `typeof document` +
   `try/catch` e não carrega `</script>` acidental (JS-02);
d) `_browser_config` inclui `user_agent`/viewport com os defaults e respeita
   as env vars (F-04);
e) `CRAWL4AI_WAIT_TIMEOUT` inválido cai no default sem exceção.

Execução:
    python -m pytest -q tests/test_coleta_wait_for.py
    python tests/test_coleta_wait_for.py      # fallback sem pytest
"""

from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, Optional

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

import coleta  # noqa: E402

URL_LISTAGEM = "https://www.wowhead.com/pt/items/armor/min-ilvl:305/max-ilvl:350"
URL_LISTAGEM_BONUS = (
    "https://www.wowhead.com/pt/items"
    "?bonus=12846:12854:12856:13440&min-ilvl=305&max-ilvl=350&quality=4"
)
URL_DETALHE = "https://www.wowhead.com/pt/item=123"

#: Env vars que os testes manipulam (restauradas ao final de cada caso).
_ENV_RELEVANTES = (
    "CRAWL4AI_WAIT_TIMEOUT",
    "CRAWL4AI_PAGE_TIMEOUT",
    "CRAWL4AI_USER_AGENT",
    "CRAWL4AI_VIEWPORT_WIDTH",
    "CRAWL4AI_VIEWPORT_HEIGHT",
    "CRAWL4AI_JS_LAZY_LOAD",
)


@contextmanager
def ambiente(**valores: Optional[str]) -> Iterator[None]:
    """Aplica env vars temporárias (None remove) e restaura ao final."""
    anteriores: Dict[str, Optional[str]] = {
        chave: os.environ.get(chave) for chave in _ENV_RELEVANTES
    }
    try:
        for chave in _ENV_RELEVANTES:
            os.environ.pop(chave, None)
        for chave, valor in valores.items():
            if valor is None:
                os.environ.pop(chave, None)
            else:
                os.environ[chave] = valor
        yield
    finally:
        for chave, valor in anteriores.items():
            if valor is None:
                os.environ.pop(chave, None)
            else:
                os.environ[chave] = valor


# ---------------------------------------------------------------------------
# (a) listagem
# ---------------------------------------------------------------------------


def test_wait_for_listagem_aceita_listview_e_tr_data_id() -> None:
    """Listagem deve esperar `.listview-row` OU `tr[data-id]` (F-01/JS-01)."""
    with ambiente():
        for url in (URL_LISTAGEM, URL_LISTAGEM_BONUS):
            config = coleta._run_config(url=url)
            assert ".listview-row" in config.wait_for, config.wait_for
            assert "tr[data-id]" in config.wait_for, config.wait_for
            assert config.wait_for.startswith("js:"), config.wait_for


def test_wait_for_explicito_tem_precedencia() -> None:
    """`wait_for` explícito não deve ser sobrescrito pela URL."""
    with ambiente():
        config = coleta._run_config(url=URL_DETALHE, wait_for="css:body")
        assert config.wait_for == "css:body"


# ---------------------------------------------------------------------------
# (b) detalhe
# ---------------------------------------------------------------------------


def test_wait_for_detalhe_usa_h1_heading_size_1() -> None:
    """Página de item deve esperar o `h1.heading-size-1` (JS-01)."""
    with ambiente():
        config = coleta._run_config(url=URL_DETALHE)
        assert "h1.heading-size-1" in config.wait_for, config.wait_for
        assert ".listview-row" not in config.wait_for, config.wait_for


# ---------------------------------------------------------------------------
# (c) JS de lazy-load (JS-02)
# ---------------------------------------------------------------------------


def test_js_lazy_load_forca_tooltips_com_mouseover() -> None:
    """O script precisa disparar `mouseover` nas linhas e ser seguro."""
    script = coleta._JS_LAZY_LOAD
    assert "mouseover" in script
    assert "MouseEvent" in script
    assert "listview-row" in script
    assert "typeof document" in script, "falta o guard de ambiente"
    assert "try" in script and "catch" in script, "falta try/catch"
    assert "</script" not in script.lower(), "script não pode fechar a tag"
    # Balanceamento mínimo de parênteses/chaves (sanity sintática).
    assert script.count("(") == script.count(")")
    assert script.count("{") == script.count("}")


def test_js_retry_scroll_existe_e_e_seguro() -> None:
    """JS-03: segundo passe de scroll forçado disponível e seguro."""
    script = coleta.JS_RETRY_SCROLL
    assert "scrollHeight" in script
    assert "2000" in script
    assert "typeof document" in script
    assert "try" in script and "catch" in script
    assert "</script" not in script.lower()


# ---------------------------------------------------------------------------
# (d) BrowserConfig (F-04)
# ---------------------------------------------------------------------------


def test_browser_config_defaults_de_user_agent_e_viewport() -> None:
    """Sem env: UA Chrome 124 e viewport 1920x1080."""
    with ambiente():
        config = coleta._browser_config()
        assert config.user_agent == coleta.USER_AGENT_PADRAO, config.user_agent
        assert "Chrome/124.0.0.0" in config.user_agent
        assert config.viewport_width == 1920, config.viewport_width
        assert config.viewport_height == 1080, config.viewport_height
        assert config.viewport == {"width": 1920, "height": 1080}


def test_browser_config_respeita_env_vars() -> None:
    """Env vars sobrescrevem UA e viewport."""
    with ambiente(
        CRAWL4AI_USER_AGENT="TestAgent/1.0",
        CRAWL4AI_VIEWPORT_WIDTH="1280",
        CRAWL4AI_VIEWPORT_HEIGHT="720",
    ):
        config = coleta._browser_config()
        assert config.user_agent == "TestAgent/1.0", config.user_agent
        assert config.viewport_width == 1280, config.viewport_width
        assert config.viewport_height == 720, config.viewport_height


def test_run_config_usa_user_agent_configurado() -> None:
    """O `user_agent` do run config acompanha `CRAWL4AI_USER_AGENT`."""
    with ambiente(CRAWL4AI_USER_AGENT="TestAgent/2.0"):
        assert coleta._run_config(url=URL_LISTAGEM).user_agent == "TestAgent/2.0"


# ---------------------------------------------------------------------------
# (e) CRAWL4AI_WAIT_TIMEOUT
# ---------------------------------------------------------------------------


def test_wait_timeout_default_e_page_timeout_preservado() -> None:
    """Default 15000 ms para `wait_for_timeout` e 60000 ms de `page_timeout`."""
    with ambiente():
        config = coleta._run_config(url=URL_LISTAGEM)
        assert config.wait_for_timeout == 15000, config.wait_for_timeout
        assert config.page_timeout == 60000, config.page_timeout


def test_wait_timeout_invalido_cai_no_default() -> None:
    """`CRAWL4AI_WAIT_TIMEOUT=abc` não pode levantar exceção."""
    with ambiente(CRAWL4AI_WAIT_TIMEOUT="abc"):
        config = coleta._run_config(url=URL_LISTAGEM)
        assert config.wait_for_timeout == 15000, config.wait_for_timeout


def test_wait_timeout_valido_e_aplicado() -> None:
    """`CRAWL4AI_WAIT_TIMEOUT=2500` reflete em `wait_for_timeout`."""
    with ambiente(CRAWL4AI_WAIT_TIMEOUT="2500", CRAWL4AI_PAGE_TIMEOUT="45000"):
        config = coleta._run_config(url=URL_LISTAGEM)
        assert config.wait_for_timeout == 2500, config.wait_for_timeout
        assert config.page_timeout == 45000, config.page_timeout


def test_js_lazy_load_respeita_gate_por_env() -> None:
    """`CRAWL4AI_JS_LAZY_LOAD=false` remove o `js_code` de lazy-load."""
    with ambiente(CRAWL4AI_JS_LAZY_LOAD="false"):
        config = coleta._run_config(url=URL_LISTAGEM)
        assert not config.js_code, config.js_code


if __name__ == "__main__":  # pragma: no cover - fallback sem pytest
    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if not (nome.startswith("test_") and callable(funcao)):
            continue
        try:
            funcao()
        except Exception as exc:  # noqa: BLE001 - relatório simples
            falhas += 1
            print(f"[FAIL] {nome}: {exc}")
        else:
            print(f"[OK] {nome}")
    print(f"\n{'FALHAS' if falhas else 'SUCESSO'}: {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
