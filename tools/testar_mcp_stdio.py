#!/usr/bin/env python3
"""Testa o servidor MCP por stdio (initialize, list_tools e uma chamada).

Não abre browser nem rede: as tools chamadas são as que leem `data/`.

Uso::

    python tools/testar_mcp_stdio.py
    python tools/testar_mcp_stdio.py --tool estado
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


async def _executar(tool: str, args_json: str) -> int:
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as exc:
        print(f"[FAIL] SDK do MCP não instalado: {exc}")
        return 1

    ambiente = dict(os.environ)
    ambiente["PYTHONIOENCODING"] = "utf-8"
    ambiente["PYTHONPATH"] = str(RAIZ)
    ambiente["MCP_TRANSPORT"] = "stdio"

    parametros = StdioServerParameters(
        command=sys.executable,
        args=[str(RAIZ / "mcp_server.py")],
        env=ambiente,
        cwd=str(RAIZ),
    )

    async with stdio_client(parametros) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()
            ferramentas = await sessao.list_tools()
            nomes = sorted(t.name for t in ferramentas.tools)
            print(f"[OK] initialize; tools={len(nomes)}")
            print("     " + ", ".join(nomes))

            if tool not in nomes:
                print(f"[FAIL] tool {tool!r} não exposta")
                return 1

            resultado = await sessao.call_tool(tool, _json_args(args_json))
            conteudo = getattr(resultado, "content", []) or []
            texto = "\n".join(
                str(getattr(bloco, "text", bloco)) for bloco in conteudo
            )
            print(f"[OK] call_tool({tool}) -> {len(texto)} chars")
            print(texto[:800])
    return 0


def _json_args(bruto: str) -> dict:
    if not bruto:
        return {}
    import json

    dados = json.loads(bruto)
    if not isinstance(dados, dict):
        raise SystemExit("--args precisa ser um objeto JSON")
    return dados


def main() -> int:
    parser = argparse.ArgumentParser(description="Teste stdio do MCP.")
    parser.add_argument("--tool", default="estado_dados")
    parser.add_argument("--args", default="")
    args = parser.parse_args()
    return asyncio.run(_executar(args.tool, args.args))


if __name__ == "__main__":
    sys.exit(main())
