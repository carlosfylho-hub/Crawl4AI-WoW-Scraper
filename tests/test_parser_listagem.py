#!/usr/bin/env python3
"""
Testes offline do parser de listagem por LINHA (Pacote 2).

Cobrem:
- fixture com 2 anchors para o mesmo item (ícone vazio + anchor nomeado)
  -> 1 registro, com o bônus da linha e o nome preenchido (RC-1/RC-4);
- variante canônica (sem bônus) marcada como `variante_fonte="canonica"`;
- listagem de 50 itens -> 50 registros com nome e bônus (sem descarte).

Execução:
    python -m pytest -q tests/test_parser_listagem.py
    python tests/test_parser_listagem.py        # fallback sem pytest
"""

from __future__ import annotations

import sys
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))


FIXTURE_ICONE_NOMEADO = """
<html><body>
  <table>
    <tr>
      <td>
        <a href="https://www.wowhead.com/pt/item=268265/relicario?bonus=13668:13987"
           tabindex="-1"></a>
      </td>
      <td>
        <a class="q4 listview-cleartext"
           href="https://www.wowhead.com/pt/item=268265/relicario">Relicário Aqiricida</a>
      </td>
    </tr>
  </table>
</body></html>
"""

FIXTURE_CANONICA = """
<html><body>
  <ul>
    <li>
      <a href="/pt/item=252258/garra" data-wowhead="item=252258&ilvl=334">Garra Talassiana</a>
    </li>
  </ul>
</body></html>
"""


def _html_lista_50() -> str:
    linhas = []
    for i in range(50):
        item_id = 300000 + i
        linhas.append(
            f"""
    <tr>
      <td><a href="https://www.wowhead.com/pt/item={item_id}/item-{i}?bonus=100:{200 + i}"
             tabindex="-1"></a></td>
      <td><a class="q4 listview-cleartext"
             data-wowhead="item={item_id}&ilvl=320"
             href="https://www.wowhead.com/pt/item={item_id}/item-{i}">Item {i}</a></td>
    </tr>
"""
        )
    return "<html><body><table>" + "".join(linhas) + "</table></body></html>"


def test_merge_icone_vazio_e_anchor_nomeado() -> None:
    """2 anchors (ícone vazio + nomeado) devem gerar 1 único registro."""
    from wow_season2 import parse_links_itens

    itens = parse_links_itens(FIXTURE_ICONE_NOMEADO, "https://www.wowhead.com/pt/guides/x")

    assert len(itens) == 1, itens
    item = itens[0]
    assert item["id"] == "268265"
    assert item["nome"] == "Relicário Aqiricida", item
    assert item["bonus_ids"] == ["13668", "13987"], item
    assert item["variante_fonte"] == "listagem", item
    # Nunca deve existir um registro apenas com o anchor de ícone vazio.
    assert all(i["nome"] for i in itens), itens


def test_variante_sem_bonus_e_canonica() -> None:
    """Sem bônus na listagem, `variante_fonte` deve ser 'canonica'."""
    from wow_season2 import parse_links_itens

    itens = parse_links_itens(FIXTURE_CANONICA, "https://www.wowhead.com/pt/guides/y")

    assert len(itens) == 1, itens
    item = itens[0]
    assert item["id"] == "252258"
    assert item["nome"] == "Garra Talassiana"
    assert item["bonus_ids"] == []
    assert item["variante_fonte"] == "canonica"
    assert item["item_level"] == 334


def test_listagem_50_itens_emite_50_registros() -> None:
    """50 linhas (cada uma com 2 anchors) devem virar 50 variações."""
    from wow_season2 import parse_links_itens

    itens = parse_links_itens(_html_lista_50(), "https://www.wowhead.com/pt/items/armor")

    assert len(itens) == 50, len(itens)
    assert all(i["nome"] for i in itens), "existe item sem nome"
    assert all(i["bonus_ids"] for i in itens), "existe item sem bônus"
    assert all(i["variante_fonte"] == "listagem" for i in itens)


def test_dedupe_por_variacao_nao_por_ilvl() -> None:
    """Mesmo item com bônus distintos deve permanecer como 2 registros."""
    from wow_season2 import parse_links_itens

    html = """
    <html><body><table>
      <tr><td>
        <a href="/pt/item=999001/a?bonus=111" tabindex="-1"></a>
        <a class="q4 listview-cleartext" href="/pt/item=999001/a">Variante A</a>
      </td></tr>
      <tr><td>
        <a href="/pt/item=999001/b?bonus=222" tabindex="-1"></a>
        <a class="q4 listview-cleartext" href="/pt/item=999001/b">Variante B</a>
      </td></tr>
    </table></body></html>
    """
    itens = parse_links_itens(html, "https://www.wowhead.com/pt/items/armor")
    bonus = sorted(tuple(i["bonus_ids"]) for i in itens)
    assert bonus == [("111",), ("222",)], itens


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
            print(f"[FAIL] {nome}")
            traceback.print_exc()
        else:
            print(f"[OK] {nome}")
    print(f"\n{'FALHAS' if falhas else 'SUCESSO'}: {falhas} falha(s)")
    sys.exit(1 if falhas else 0)
