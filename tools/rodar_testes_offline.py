#!/usr/bin/env python3
"""Roda cada arquivo de `tests/` em subprocesso com timeout (diagnóstico).

Motivo: alguns testes importam `crawl4ai`/Playwright e podem demorar. Este
runner identifica o arquivo culpado sem deixar o terminal preso em um comando
aparentemente infinito.

Uso::

    python tools/rodar_testes_offline.py
    python tools/rodar_testes_offline.py --timeout 60
    python tools/rodar_testes_offline.py --incluir-app
"""

from __future__ import annotations

import argparse
import glob
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Runner com timeout por arquivo.")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument(
        "--incluir-app",
        action="store_true",
        help="Inclui tests/test_app_streamlit.py (AppTest costuma ser lento).",
    )
    args = parser.parse_args()

    arquivos = sorted(glob.glob(str(RAIZ / "tests" / "test_*.py")))
    if not args.incluir_app:
        arquivos = [a for a in arquivos if "test_app_streamlit" not in a]

    falhas = 0
    timeouts = 0
    for caminho in arquivos:
        nome = Path(caminho).name
        inicio = time.time()
        try:
            resultado = subprocess.run(
                [sys.executable, caminho],
                cwd=str(RAIZ),
                capture_output=True,
                text=True,
                timeout=args.timeout,
            )
            if resultado.returncode == 0:
                status = "OK"
            else:
                status = "FAIL"
                falhas += 1
                print(f"[FAIL] {nome}")
                print((resultado.stdout or "")[-1500:])
                print((resultado.stderr or "")[-1500:])
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
            timeouts += 1
        print(f"[{status}] {nome} ({time.time() - inicio:.1f}s)", flush=True)

    print(
        f"\nResumo: {len(arquivos)} arquivos, {falhas} falha(s), "
        f"{timeouts} timeout(s)"
    )
    return 1 if (falhas or timeouts) else 0


if __name__ == "__main__":
    sys.exit(main())
