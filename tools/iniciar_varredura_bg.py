#!/usr/bin/env python3
"""Inicia a varredura de craft R5 em background, com log em arquivo.

Motivo: neste Windows, o `python.exe` do WindowsApps não funciona via
`Start-Process`/`start /b`. Este launcher usa `sys.executable` (o mesmo que roda
os testes) e `DETACHED_PROCESS`, então o processo continua após o comando
retornar.

Uso::

    python tools/iniciar_varredura_bg.py
    python tools/iniciar_varredura_bg.py --max-itens 30 --max-detalhes 30
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DIAG = RAIZ / "data" / "_diagnostico"


def main() -> int:
    parser = argparse.ArgumentParser(description="Varredura em background.")
    parser.add_argument("--max-itens", type=int, default=120)
    parser.add_argument("--max-detalhes", type=int, default=100)
    args = parser.parse_args()

    DIAG.mkdir(parents=True, exist_ok=True)
    saida = DIAG / "varredura_craft.out"
    erros = DIAG / "varredura_craft.err"

    # IMPORTANTE: `DETACHED_PROCESS` faz o `python.exe` do WindowsApps morrer
    # silenciosamente neste ambiente. `CREATE_NEW_PROCESS_GROUP` basta: no
    # Windows o filho continua após o pai terminar.
    flags = 0
    if os.name == "nt":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP

    ambiente = dict(os.environ)
    ambiente["PYTHONIOENCODING"] = "utf-8"

    with open(saida, "w", encoding="utf-8") as out, open(
        erros, "w", encoding="utf-8"
    ) as err:
        processo = subprocess.Popen(
            [
                sys.executable,
                "scraper_season2.py",
                "--max-itens",
                str(args.max_itens),
                "--max-detalhes",
                str(args.max_detalhes),
                "--qualidade-craft",
                "5",
                "--exigir-craft",
            ],
            cwd=str(RAIZ),
            stdin=subprocess.DEVNULL,
            stdout=out,
            stderr=err,
            creationflags=flags,
            close_fds=True,
            env=ambiente,
        )

    time.sleep(2)
    vivo = processo.poll() is None
    print(f"PID={processo.pid}")
    print(f"ALIVE={vivo}")
    print(f"stdout={saida}")
    print(f"stderr={erros}")
    if not vivo:
        print("O processo terminou imediatamente; veja o stderr acima.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
