#!/usr/bin/env python3
"""Utilitários de runtime compartilhados pelos entrypoints do projeto.

Por que este módulo existe
--------------------------
O Playwright (usado pelo Crawl4AI) precisa lançar subprocessos do navegador.
No Windows, o ``SelectorEventLoop`` padrão do Streamlit/Tornado não suporta
subprocessos e falha com::

    NotImplementedError

A solução é usar ``WindowsProactorEventLoopPolicy``. Este módulo centraliza
esse workaround para evitar duplicação em ``app_streamlit.py`` e
``mcp_server.py``. Em Linux/macOS nada muda: a função é um no-op (exceto
quando ``criar_loop=True``, caso em que apenas cria um event loop normal).
"""

from __future__ import annotations

import asyncio
import os
import sys
from typing import Optional


def configurar_saida_utf8() -> None:
    """Força ``stdout``/``stderr`` em UTF-8 no console do Windows (F-09).

    Por que existe
    --------------
    O console padrão do Windows abre o Python com a *code page* local
    (``cp1252``/``cp850``). Qualquer ``print`` com acento — comum nos
    relatórios em PT-BR — levanta ``UnicodeEncodeError`` e aborta o
    scraper. Reconfigurar os streams no topo do ``runtime`` garante que
    todo entrypoint que importe este módulo escreva UTF-8.

    Regras
    ------
    - ``PYTHONIOENCODING`` é respeitada quando já aponta para UTF-8
      (``utf-8``, ``utf8``, ``utf-8:replace``…): nesse caso nada é feito.
    - Quando a variável aponta para outra *code page*, o UTF-8 é forçado
      (o objetivo do F-09 é justamente evitar ``UnicodeEncodeError``).
    - Streams que não expõem ``reconfigure`` (ex.: ``io.StringIO`` em
      testes) são ignorados silenciosamente.
    """

    encoding_env = os.environ.get("PYTHONIOENCODING", "").strip().lower()
    if encoding_env.startswith(("utf-8", "utf8")):
        return

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8")
        except Exception:  # pragma: no cover - stream exótico
            pass


# Executa no import: todo entrypoint que importar `runtime` já sai em UTF-8.
configurar_saida_utf8()


def configurar_event_loop_windows(
    criar_loop: bool = False,
) -> Optional[asyncio.AbstractEventLoop]:
    """Configura o event loop adequado ao Playwright no Windows.

    Parâmetros
    ----------
    criar_loop:
        Quando ``True``, cria e registra um novo event loop *na thread atual*
        (necessário para o worker do Streamlit, que roda em thread separada e
        não herda o loop principal). Quando ``False`` (padrão), apenas define
        a policy global — comportamento adequado ao processo principal do MCP.

    Retorno
    -------
    ``asyncio.AbstractEventLoop`` quando ``criar_loop=True``; ``None`` caso
    contrário (ou sempre que a criação não for solicitada).

    Notas
    -----
    - Windows: usa ``WindowsProactorEventLoopPolicy`` (suporta subprocessos).
    - Linux/macOS: sem alteração de policy; com ``criar_loop=True`` apenas
      devolve ``asyncio.new_event_loop()`` como antes.
    """

    if sys.platform == "win32":
        policy = asyncio.WindowsProactorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)
        if criar_loop:
            loop = policy.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
        return None

    # Linux/macOS: mantém o comportamento original (sem policy especial).
    if criar_loop:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
    return None


__all__ = ["configurar_event_loop_windows", "configurar_saida_utf8"]
