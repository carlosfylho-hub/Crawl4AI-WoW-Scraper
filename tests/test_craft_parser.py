#!/usr/bin/env python3
"""Testes offline do parser de **profissão/qualidade de craft** (Pacote 4).

Cobre as pendências 1/9/10:

a) item craftado com `?crafting-quality=5` na URL → `qualidade_craft=5`,
   `qualidade_craft_fonte="url:crafting-quality"`;
b) item craftado com `Rank 5` no texto → `qualidade_craft=5` e fonte de texto;
c) item **não** craftado com a palavra "qualidade" → `qualidade_craft=0`;
d) `profissao_craft` detectada por link de profissão, por texto
   ("Feito por/Crafted by") e pelo fallback de receita (base local);
e) quando nada é detectado, `craft_indicio` registra a evidência observada
   em vez de zerar silenciosamente.

Execução:
    python -m pytest -q tests/test_craft_parser.py
    python tests/test_craft_parser.py        # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from wow_season2 import (  # noqa: E402
    extrair_detalhes_item,
    extrair_qualidade_craft,
    extrair_qualidade_craft_detalhado,
    finalizar_item_bilingue,
    profissao_por_receita,
)


# ---------------------------------------------------------------------------
# Fixtures HTML inline
# ---------------------------------------------------------------------------

HTML_CRAFT_POR_LINK = """
<html><body>
  <h1 class="heading-size-1 q4">Lâmina de Teste</h1>
  <div class="wowhead-tooltip">
    <div>Nível do Item: 341</div>
    <div>Qualidade de criação: 5</div>
    <a href="/pt/professions/blacksmithing">Ferraria</a>
  </div>
</body></html>
"""

HTML_CRAFT_POR_TEXTO = """
<html><body>
  <h1 class="heading-size-1 q4">Lâmina de Teste</h1>
  <div class="wowhead-tooltip">
    <div>Nível do Item: 341</div>
    <div>Crafted by Ferraria — Rank 5</div>
  </div>
</body></html>
"""

HTML_NAO_CRAFTADO = """
<html><body>
  <h1 class="heading-size-1 q4">Anel da Sorte</h1>
  <div class="wowhead-tooltip">
    <div>Nível do Item: 341</div>
    <div>Item de qualidade superior, sem indicação de rank de craft.</div>
  </div>
</body></html>
"""

HTML_SEM_PROFISSAO_COM_QUALIDADE_URL = """
<html><body>
  <h1 class="heading-size-1 q4">Elo Misterioso</h1>
  <div class="wowhead-tooltip">
    <div>Nível do Item: 341</div>
  </div>
</body></html>
"""

HTML_FALLBACK_RECEITA = """
<html><body>
  <h1 class="heading-size-1 q4">Repreensão do Quebra-feitiço</h1>
  <div class="wowhead-tooltip">
    <div>Nível do Item: 246</div>
  </div>
</body></html>
"""


def _montar_item(
    html: str,
    url: str,
    item_id: Any,
    nome: str = "Item de Teste",
    item_level: int = 341,
    bonus_ids: list | None = None,
) -> Dict[str, Any]:
    """Roda o pipeline real (detalhes PT-BR + consolidação bilíngue)."""
    bruto = {
        "id": item_id,
        "nome": nome,
        "item_level": item_level,
        "qualidade": 4,
        "bonus_ids": bonus_ids or [],
        "url": url,
        "_pagina": url,
    }
    pt = extrair_detalhes_item(html, bruto)
    return finalizar_item_bilingue(bruto, pt, {}, url, "")


# ---------------------------------------------------------------------------
# (a) R5 pela URL
# ---------------------------------------------------------------------------

def test_craftado_com_crafting_quality_na_url() -> None:
    item = _montar_item(
        HTML_CRAFT_POR_LINK,
        "https://www.wowhead.com/pt/item=250001?crafting-quality=5",
        "250001",
        nome="Lâmina de Teste",
    )

    assert item["qualidade"] == 4, item
    assert item["qualidade_craft"] == 5, item
    assert item["qualidade_craft_fonte"] == "url:crafting-quality", item
    assert item["motivo_qualidade_craft"] == "url:crafting-quality", item
    assert item["profissao_craft"] == "Ferraria", item
    assert item["profissao_craft_fonte"] == "link", item
    assert "profissao:link" in item["craft_indicio"], item


# ---------------------------------------------------------------------------
# (b) R5 pelo texto
# ---------------------------------------------------------------------------

def test_craftado_com_rank_no_texto() -> None:
    item = _montar_item(
        HTML_CRAFT_POR_TEXTO,
        "https://www.wowhead.com/pt/item=250002",
        "250002",
        nome="Lâmina de Teste",
    )

    assert item["qualidade_craft"] == 5, item
    assert item["qualidade_craft_fonte"] == "tooltip", item
    assert item["motivo_qualidade_craft"] == "texto:Rank 5", item
    assert item["profissao_craft"] == "Ferraria", item
    assert item["profissao_craft_fonte"] == "texto", item


# ---------------------------------------------------------------------------
# (c) Não craftado com a palavra "qualidade"
# ---------------------------------------------------------------------------

def test_nao_craftado_com_palavra_qualidade_fica_zero() -> None:
    item = _montar_item(
        HTML_NAO_CRAFTADO,
        "https://www.wowhead.com/pt/item=250009",
        "250009",
        nome="Anel da Sorte",
    )

    assert item["qualidade_craft"] == 0, item
    assert item["qualidade_craft_fonte"] == "", item
    assert item["motivo_qualidade_craft"] == "ausente", item
    assert item["profissao_craft"] == "", item
    assert item["craft_indicio"] == "ausente", item

    # Função pura: texto genérico nunca vira qualidade de craft.
    assert extrair_qualidade_craft("Item de qualidade 5") == 0
    assert extrair_qualidade_craft("Rank 5") == 0
    assert extrair_qualidade_craft("Item de qualidade superior") == 0


def test_qualidade_craft_por_rotulo_explicito() -> None:
    assert extrair_qualidade_craft("Qualidade de criação: 4") == 4
    assert extrair_qualidade_craft("Crafting Quality: 3") == 3
    valor, motivo = extrair_qualidade_craft_detalhado("Crafted by Couraria — Rank 2")
    assert (valor, motivo) == (2, "texto:Rank 2"), (valor, motivo)


# ---------------------------------------------------------------------------
# (d) Fallback receita → profissão
# ---------------------------------------------------------------------------

def test_fallback_receita_para_profissao() -> None:
    # 237831 está em base_conhecimento_ai_studio/craft_armas_s2.json (Ferraria)
    assert profissao_por_receita("237831") == "Ferraria"
    assert profissao_por_receita("237834") == "Ferraria"
    assert profissao_por_receita("999999") == ""

    item = _montar_item(
        HTML_FALLBACK_RECEITA,
        "https://www.wowhead.com/pt/item=237831",
        "237831",
        nome="Repreensão do Quebra-feitiço",
        item_level=246,
    )
    assert item["profissao_craft"] == "Ferraria", item
    assert item["profissao_craft_fonte"] == "receita", item
    assert item["craft_indicio"] == "profissao:receita", item


# ---------------------------------------------------------------------------
# (e) Evidência observada sem profissão NÃO é zerada em silêncio
# ---------------------------------------------------------------------------

def test_sem_profissao_registra_indicio() -> None:
    item = _montar_item(
        HTML_SEM_PROFISSAO_COM_QUALIDADE_URL,
        "https://www.wowhead.com/pt/item=250003?crafting-quality=5",
        "250003",
        nome="Elo Misterioso",
    )

    # Qualidade de craft não se aplica sem profissão...
    assert item["qualidade_craft"] == 0, item
    assert item["qualidade_craft_fonte"] == "", item
    # ...mas a evidência fica auditável.
    assert "ignorado:sem_profissao" in item["motivo_qualidade_craft"], item
    assert "url:crafting-quality" in item["motivo_qualidade_craft"], item
    assert "qualidade_craft:" in item["craft_indicio"], item


if __name__ == "__main__":  # pragma: no cover - fallback sem pytest
    import traceback

    falhas = 0
    for nome, funcao in sorted(globals().items()):
        if not (nome.startswith("test_") and callable(funcao)):
            continue
        try:
            funcao()
        except Exception:  # noqa: BLE001 - relatório simples
            falhas += 1
            print(f"[FALHOU] {nome}")
            traceback.print_exc()
        else:
            print(f"[OK] {nome}")
    print(f"\n{'FALHAS' if falhas else 'SUCESSO'}: {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
