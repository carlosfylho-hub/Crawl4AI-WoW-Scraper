# Auditoria dos JSON do projeto contra o Wowhead

**Data:** 2026-11-05
**Fonte:** `nether.wowhead.com/tooltip/item/<id>?dataEnv=1&locale=enUS`
**Método:** coleta local via Node — **zero créditos Firecrawl consumidos**
**Critério:** compara a **identidade** dos atributos (quais existem), não os valores numéricos. O tooltip padrão vem no track máximo e os números escalam com ilvl, então comparar valor bruto geraria falso positivo em massa.

---

## 1. Estado final (após correções)

| Métrica | Valor |
|---|---|
| IDs de item encontrados nos JSON | 190 |
| Coletados com sucesso | 187 |
| Não são itens (falsos positivos do extrator) | 3 |
| Registros de item analisados | 297 |
| Registros com bloco de stats comparável | 93 |
| Atributo primário divergente | **0** |
| Atributo secundário inventado | **0** |
| Atributo secundário faltando | **0** |
| Efeito citando atributo que o item não concede | **0** |
| Nome EN divergente do oficial | **0** |

Os 3 IDs não resolvidos são `136815`, `136824` (nós de talento, não itens) e `381991` (ID de notícia citado em `_meta.fontes`). Nenhum é item.

---

## 2. Correções aplicadas nesta auditoria

### 2.1 Trinket de Força tratado como BiS de conjurador

Item `250229`. O tooltip oficial confirma: **+148 de Crítico e 290 de FORÇA por 15s**. É trinket de melee.

| Arquivo | O que dizia | Correção |
|---|---|---|
| `demonology_warlock.json` | `Trinket2` do BiS M+ | Trocado por Nó de Serpentes Contorcidas (`273794`), passivo e de Intelecto |
| `demonology_warlock.json` | Covil de Nalorakk em rank 2 | Rank 2 passou para Altar das Presas |
| `demonology_warlock.json` | Item no `a_tier` | Removido do ranking |
| `season2_context.json` | "BiS berloque M+ do Demo" | Removido dos drops, virou nota de exclusão |
| `season2_context.json` | `specs_relevantes: Demo Warlock (BiS)` | `excluido: true` com motivo |
| `mplus_loot_database.json` | Errata afirmando ser o trinket DPS do covil | Errata corrigida |
| `mplus_loot_database.json` | `Critico: 10`, efeito "Intelecto/Força" | `Critico: 148`, Força, `usavel_por_conjurador: false` |
| `mplus_loot_database.json` | `A_tier` de casters | Removido da lista |

O substituto foi escolhido por ser **passivo**: o `Trinket1` do projeto é o Emblema Tempestuoso de Dazar, que é on-use, e a regra R4 proíbe dois on-use simultâneos.

### 2.2 Sete outros trinkets de Força ou Agilidade marcados

Cada um recebeu `atributo_concedido` e `usavel_por_conjurador: false` em `mplus_loot_database.json`:

| Item | Atributo |
|---|---|
| Pedra-presa Retorcida (`273795`) | Força |
| Semente da Natureza Voraz (`250238`) | Força |
| Presa de Merektha (`158367`) | Força |
| Casco de Ataflamas (`193762`) | Força no efeito |
| Mandato de Execução do Caos (`250225`) | Agilidade |
| Eletromental Pequeno no Pote (`158374`) | Agilidade |
| Plumagem Dourada Lustrosa (`159617`) | Agilidade |

Dois deles estavam no `B_tier` de casters e foram removidos.

### 2.3 Nomes EN errados — 26 substituições em 5 arquivos

| ID | O projeto chamava | O oficial é |
|---|---|---|
| `251132` | Hellfire Shroud | **Speakeasy Shroud** |
| `270169` | Grand Bagart's Doom Idol | **Hex Lord's Dooming Idol** |
| `250229` | War Loa's Idol | **Idol of the War Loa** |
| `271528` | Drowsy Gaze of the Enigmatic Dreamwatcher | **Enigmatic Dreamwatcher's Somnolent Stare** |
| `271526` | Plumage of the Enigmatic Dreamwatcher | **Enigmatic Dreamwatcher's Plumage** |
| `271531` | Lunar Raiment of the Enigmatic Dreamwatcher | **Enigmatic Dreamwatcher's Lunar Raiment** |
| `271529` | Gauntlets of the Enigmatic Dreamwatcher | **Enigmatic Dreamwatcher's Gauntlets** |
| `271527` | Legwraps of the Enigmatic Dreamwatcher | **Enigmatic Dreamwatcher's Leggings** |
| `271555` | True Sight of the Cosmic Penitent | **Cosmic Penitent's Truesight** |
| `271553` | Echoing Screams of the Cosmic Penitent | **Cosmic Penitent's Echoing Screams** |
| `271558` | Eclipse-Wracked Vestments of the Cosmic Penitent | **Cosmic Penitent's Eclipsing Robes** |
| `271556` | Celestial Gauntlets of the Cosmic Penitent | **Cosmic Penitent's Celestial Grips** |
| `271554` | Enveloping Culots of the Cosmic Penitent | **Enveloping Legwraps of the Cosmic Penitent** |

Distribuição: `balance_druid.json` (10), `shadow_priest.json` (11), `demonology_warlock.json` (1), `mplus_loot_database.json` (2), `season2_context.json` (2).

### 2.4 Campo com dois itens concatenados

`shadow_priest.json`, slot `Boots`: `item_en` continha `"Cackling Soultreads (21/50) / Trail of the Cosmic Penitent (12/50)"`. Desmembrado em nome limpo + campo `nota_uso` com os dois percentuais.

---

## 3. Pendências que a auditoria não fecha

| Pendência | Motivo |
|---|---|
| **Nomes PT-BR de `251132` e `270169`** | O nome EN estava errado, portanto o PT também está. "Mortalha do Inferninho" e "Ídolo da Perdição do Grão-bagateiro" precisam ser conferidos contra o Wowhead PT-BR |
| **204 registros sem bloco de stats** | Entradas como `drops_notaveis` e `todos_itens_bis_pt_br` só têm nome e id, então não há o que comparar |
| **Valores numéricos de stats** | A auditoria comparou identidade, não valor. Comparar valor exige fixar o ilvl de referência de cada registro |
| **Divergências de BiS contra Murlok e MaxRoll** | Capa, cinto e off-hand do Demo divergem das fontes externas. Isso é disputa de recomendação, não erro de cadastro |

---

## 4. Como re-rodar

```bash
node tools/audit_itens.js          # coleta incremental, pula IDs já baixados
node tools/audit_itens.js --force  # rebaixa tudo
node tools/compare_auditoria.js    # gera este relatório
node tools/corrigir_nomes.js       # dry-run das correções de nome
node tools/corrigir_nomes.js --aplicar
```

Artefatos: [`auditoria_itens.json`](auditoria_itens.json:1) (cache com tooltip cru de cada item), este relatório, e os três scripts em [`tools/`](tools/audit_itens.js:1).
