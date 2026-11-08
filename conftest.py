"""Configuração raiz do pytest para o projeto Crawl4AI / WoWhead Season 2.

Garante que a raiz do repositório esteja no `sys.path`, de modo que os testes
em `tests/` importem os módulos de produção (`config`, `wow_season2`, ...) sem
`PYTHONPATH` manual. Os runners de fallback (`python tests/<arquivo>.py`)
continuam funcionando sem pytest.
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))
