"""Diagnóstico: extrai IDs de itens das tabelas do catálogo M+.

Movido de ``data/_diagnostico/`` (F-11). Gera apenas saída em stdout.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

import runtime  # noqa: E402,F401  (F-09: console UTF-8)

ARQUIVOS = (
    RAIZ / "base_conhecimento_ai_studio" / "armaduras_drop_mplus.md",
    RAIZ / "base_conhecimento_ai_studio" / "armas_drop_mplus.md",
)

ids = []
for arquivo in ARQUIVOS:
    with open(arquivo, encoding="utf-8") as f:
        texto = f.read()
    for m in re.findall(r"\|\s*(\d{6})\s*\|", texto):
        if m not in ids:
            ids.append(m)

print(len(ids), file=sys.stderr)
print(" ".join(ids))
