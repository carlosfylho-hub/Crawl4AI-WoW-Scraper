#!/usr/bin/env python3
"""Diagnóstico: o filtro min-ilvl chegou ao HTML da listagem?

Lê ``data/_diagnostico/_listagem.html`` (gerado por
``valida_anchors_bonus.py``).

Movido de ``data/_diagnostico/`` (F-11). Executar da raiz do projeto::

    python tools/diagnostico/valida_html_filtro.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

import runtime  # noqa: E402,F401  (F-09: console UTF-8)

ARQUIVO_HTML = RAIZ / "data" / "_diagnostico" / "_listagem.html"

html = ARQUIVO_HTML.read_text(encoding="utf-8", errors="replace")

print("len(html)          =", len(html))
print("count('min-ilvl')  =", html.count("min-ilvl"))
print("count('max-ilvl')  =", html.count("max-ilvl"))
print("item=19019 (clássico) =", "item=19019" in html)
print("item=49812 (clássico) =", "item=49812" in html)
print("count('#items')    =", html.count("#items"))

achados = re.findall(r"min-ilvl.{0,20}", html)[:6]
for a in achados:
    print("amostra:", repr(a))
