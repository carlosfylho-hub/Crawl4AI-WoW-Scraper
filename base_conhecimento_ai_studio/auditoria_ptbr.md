# Auditoria de nomes e valores contra o Wowhead PT-BR

**Fonte:** `nether.wowhead.com/tooltip/item/<id>?dataEnv=1&locale=8` (PT-BR oficial)
**Data:** 2026-11-05 · **Créditos Firecrawl gastos: 0**

---

## Resposta curta

| Pergunta | Resposta |
|---|---|
| Os nomes PT-BR são reais? | **Sim.** Vieram do Wowhead PT e conferem. |
| Os nomes EN são reais? | **Não eram.** 13 itens tinham nome inventado. Corrigido. |
| Os atributos listados existem? | **Sim.** 0 divergências de atributo primário e de combinação de secundários. |
| Os valores numéricos são reais? | **Não eram.** Ficavam de 1,9× a 3,9× abaixo do oficial. **Corrigido agora.** |

---

## 1. O diagnóstico dos valores

Antes da correção, comparando cada registro com o tooltip oficial no ilvl máximo do item:

| Atributo | Amostras | Razão oficial/projeto (mediana) |
|---|---|---|
| Vigor | 36 | **3,89×** |
| Intelecto | 40 | **2,94×** |
| Aceleração | 37 | 1,89× |
| Maestria | 36 | 1,88× |
| Crítico | 31 | 1,88× |
| Versatilidade | 9 | 1,86× |
| Força | 3 | 27,29× |
| Agilidade | 3 | 31,83× |

A razão é **constante dentro de cada atributo** e **diferente entre atributos**. Isso descarta erro de arredondamento: os números seguiam uma escala própria, coerente entre si, mas ~80 níveis de item abaixo do item real. Como nenhuma dessas peças existe nesse ilvl, os valores foram **estimados ou transportados de outra escala**, não raspados.

Exemplo direto do item `271528`, Olhar Soporífero do Velassonhos Enigmático:

| Campo | Antes | Oficial | Razão |
|---|---|---|---|
| Intelecto | 65 | 189 | 2,9× |
| Vigor | 1005 | 3910 | 3,9× |
| Aceleração | 76 | 142 | 1,9× |
| Versatilidade | 32 | 59 | 1,8× |

---

## 2. O que a correção fez

**93 registros** tiveram os números substituídos pelos oficiais no **ilvl máximo de cada item**, com rastreabilidade:

| Arquivo | Registros corrigidos |
|---|---|
| `balance_druid.json` | 27 |
| `demonology_warlock.json` | 23 |
| `shadow_priest.json` | 22 |
| `mplus_loot_database.json` | 21 |

Cada registro agora carrega:

```json
"stats": {
  "ilvl_referencia": 334,
  "track_referencia": "Mito 6/6",
  "stats_fonte": "nether.wowhead.com locale=8, ilvl maximo do item, 2026-11-05",
  "AtributoPrimario": 189,
  "primario_dual": "Agilidade ou Intelecto",
  "Vigor": 3910,
  "Aceleração": 142,
  "Versatilidade": 59
}
```

Armaduras de Midnight usam **primário combinado** (`+189 [Agilidade ou Intelecto]`). Antes eu gravava os dois valores duplicados; agora fica um único `AtributoPrimario` mais a string `primario_dual`.

---

## 3. Ilvl máximo por origem — o mapa real

O máximo **não é uniforme** entre as fontes de item:

| ilvl máximo | Rótulo no tooltip | Slots | Itens |
|---|---|---|---|
| **344** | Mítico · **Amaldiçoado com Peçonha** | Cantrip de raide (elmo, pernas, arma, pescoço) + cinto, botas | 9 |
| **341** | Mítico+ · **Ascendente Forjado com Peçonha: Mito** | Pescoço, berloque, arma e mão secundária | 35 |
| **334** | Mítico · Mito 6/6 | Tier de raide | 96 |
| **328** | **Ascendente Forjado com Peçonha: Herói** | Pescoço, berloque, arma e mão secundária | 14 |
| **321** | Herói · Herói 6/6 | Tier de raide | 26 |
| 308 | Campeão 6/6 | — | 1 |
| 246 | Legado de temporadas anteriores | — | 6 |

### 3.1 O sistema Forjado com Peçonha — confirmado

Você estava certo sobre o +7, e o nome oficial é **Ascendente Forjado com Peçonha** (*Ascendant Venomforged*).

| Track | Base sem forja | Com forja | Diferença |
|---|---|---|---|
| Herói | 321 | **328** | +7 |
| Mítico | 334 | **341** | +7 |

**Slots afetados:** pescoço, berloque, arma (uma mão, duas mãos e mão secundária).

Evidências diretas do tooltip PT-BR:

| Item | Slot | Rótulo | ilvl |
|---|---|---|---|
| Periapto Sussurrante (`272228`) | Pescoço | Ascendente Forjado com Peçonha: Herói | 328 |
| Talismã Serpentino (`272229`) | Pescoço | Ascendente Forjado com Peçonha: Herói | 328 |
| Adaga do Eidolon Esquecido (`272266`) | Adaga | Ascendente Forjado com Peçonha: Herói | 328 |
| Feixe de Presas Protetoras (`273781`) | Pescoço | Ascendente Forjado com Peçonha: Mito | 341 |
| Navalha de Lumineira Afiada (`275070`) | Adaga | Ascendente Forjado com Peçonha: Mito | 341 |
| Nó de Serpentes Contorcidas (`273794`) | Berloque | Ascendente Forjado com Peçonha: Mito | 341 |

No acervo do projeto há **49 itens forjados**: 14 em 328 e 35 em 341.

**Correção que permanece:** Herói 6/6 de tier é **321**, não 328. Os 328 são as peças forjadas do track Herói. Confirmado em dois pontos independentes — o `271546` com bônus de Herói retorna 321 e o `271543` com Mítico retorna 334.

**Cuidado ao comparar:** um berloque forjado de 341 não equivale a uma peça comum de 341. Ele é um item de track mítico (334) com +7 da forja. Sempre normalizar pelo `ilvl_referencia` antes de comparar dois itens.

---

## 4. Nomes

| Verificação | Resultado |
|---|---|
| Nome PT-BR divergente do Wowhead PT | **0** (o único sinalizado tinha sufixo descritivo, não era erro) |
| Nome EN divergente do Wowhead | 31 ocorrências em 13 itens, **todas corrigidas** |

Os dois casos mais graves eram nomes que **não existem**:

| ID | O projeto chamava | O oficial é |
|---|---|---|
| `251132` | Hellfire Shroud | **Speakeasy Shroud** |
| `270169` | Grand Bagart's Doom Idol | **Hex Lord's Dooming Idol** |

Os outros 11 eram peças de tier com nome remontado: `Drowsy Gaze of the Enigmatic Dreamwatcher` no lugar de `Enigmatic Dreamwatcher's Somnolent Stare`, `Legwraps` no lugar de `Leggings`, `Culots` no lugar de `Legwraps`, `Vestments` no lugar de `Eclipsing Robes`.

---

## 5. Confiabilidade por camada

| Camada | Status |
|---|---|
| ID do item | ✅ 187 de 190 resolvem para item real |
| Nome PT-BR | ✅ Confiável |
| Nome EN | ✅ Corrigido agora |
| Combinação de atributos | ✅ 0 divergências |
| Atributo primário | ✅ 0 divergências |
| Valores numéricos | ✅ Corrigido agora, com ilvl de referência explícito |
| Texto do efeito | ⚠️ Revisado quanto a atributo errado, não quanto a valor numérico |

---

## 6. Cuidado ao comparar itens

Os valores agora são de **ilvl máximo**. Comparar dois itens exige o **mesmo ilvl dos dois lados** — por isso todo registro tem `ilvl_referencia`. A regra do projeto de "+13 ilvl compensa stats subótimas" continua válida e deve ser aplicada sobre valores normalizados, não sobre estes diretamente.

---

## 7. Artefatos e como re-rodar

| Arquivo | Função |
|---|---|
| [`stats_oficiais_itens.json`](stats_oficiais_itens.json:1) | Referência oficial dos 187 itens: nome PT, nome EN, ilvl máximo, track e atributos |
| [`auditoria_itens.json`](auditoria_itens.json:1) | Cache com o tooltip cru em enUS |
| [`auditoria_ptbr.json`](auditoria_ptbr.json:1) | Cache com o tooltip cru em PT-BR |
| [`tools/audit_itens.js`](tools/audit_itens.js:1) | Coleta enUS |
| [`tools/audit_ptbr.js`](tools/audit_ptbr.js:1) | Coleta PT-BR e compara |
| [`tools/gerar_stats_oficiais.js`](tools/gerar_stats_oficiais.js:1) | Gera a referência e este relatório |
| [`tools/injetar_stats.js`](tools/injetar_stats.js:1) | Injeta os valores oficiais nos JSON |

```bash
node tools/audit_itens.js --force   # rebaixa enUS
node tools/audit_ptbr.js            # rebaixa PT-BR e compara
node tools/gerar_stats_oficiais.js  # regenera a referência
node tools/injetar_stats.js --aplicar
```

---

# Auditoria do sistema de criação (*craft*) — 2026-11-05

Auditoria nova, independente das 190 entradas de item: **91 IDs** do sistema de craft consultados em `nether.wowhead.com/tooltip/item` nos locales `8` (PT-BR) e `0` (enUS). **91 acertos, 0 falhas.** Script [`tools/auditar_craft.js`](tools/auditar_craft.js:1), saída [`craft_sistemas_s2.json`](craft_sistemas_s2.json:1).

## O que a auditoria passou a ter

| Campo extraído | Para que serve |
| :--- | :--- |
| `nome_pt` e `nome_en` | Conferência de nome oficial dos embelezamentos e missivas |
| `ilvl_craft` | Separa reagente (72/80/90) de equipamento (246) |
| `usavel_com` | **Restrição de slot real**, tirada do tooltip — não de guia |
| `fornece_propriedade` | Texto do efeito concedido pelo reagente |
| `reagente_opcional` | Distingue reagente de criação de item equipável |

## Correções que a auditoria produziu

| Item | Antes | Depois | Evidência |
| :--- | :--- | :--- | :--- |
| Profissão da Lanterna de Aln'hara (`245769`) | Alfaiataria | **Escrivania** | Página do item no Wowhead: *Midnight Inscription* |
| Nome PT do *Arcanoweave Lining* | “Forro Arcanoentrelaçado” | **Forro de Arcanotrama** | Tooltip PT-BR, `240167` |
| Nome PT do *Hunter's Ritual Stone* | “Pedra Ritual do Caçador” | **confirmado** | Tooltip PT-BR, `273060` |
| Nome PT da *Thalassian Missive of the Quickblade* | “Lâmina Veloz” | **Gumepresto** | Tooltip PT-BR, `245791` |
| Embelezamento na mão secundária | Pedra Ritual do Caçador | **Signo de Negraluna** | “Usável com: Armas de Ferraria de Midnight” exclui Escrivania |
| Tag do limite | “conjunto limitado a 2 peças” | **“Único-equipado: Embelezado (2)”** | Tooltip de item embelezado + guia oficial de profissões |

## Onde os resultados foram aplicados

- [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1) — documento novo do sistema.
- [`season2_context.md`](season2_context.md:1) — seção 11.
- [`demonology_warlock.json`](demonology_warlock.json:1), [`balance_druid.json`](balance_druid.json:1), [`shadow_priest.json`](shadow_priest.json:1) — profissão da Lanterna e embelezamento válido em mão secundária.
- [`mplus_loot_database.json`](mplus_loot_database.json:1) — entrada `alnhara_lantern_craftado` corrigida, com a nota de restrição.

```bash
node tools/auditar_craft.js          # regrava craft_sistemas_s2.json (91 IDs, 2 locales)
node tools/auditar_craft.js --dry    # só imprime
node tools/auditar_craft.js --falhas # só os IDs com erro
```

## Segunda rodada — armas, encantamentos e gemas

Depois da primeira auditoria ficou claro que __peça craftável__ não é o mesmo que __arma__ e que encantamento e gema não estavam catalogados. Três auditorias novas, todas no endpoint gratuito:

| Auditoria | Script | Resultado |
| :--- | :--- | :--- |
| **Armas craftáveis** | [`tools/auditar_armas_craft.js`](tools/auditar_armas_craft.js:1) | **24 armas** com nome PT-BR oficial, tipo e atributos → [`craft_armas_s2.json`](craft_armas_s2.json:1) |
| **Descoberta por faixa de ID** | [`tools/varrer_itens.js`](tools/varrer_itens.js:1) | **244 itens** varridos nas faixas 243947–244100, 240840–240990 e 273065–273080 → [`varredura_itens.json`](varredura_itens.json:1) |
| **Encantamentos, gemas e pernas** | [`tools/auditar_encantamentos_gemas.js`](tools/auditar_encantamentos_gemas.js:1) | **38 encantamentos (76 IDs)**, **72 gemas** e **6 aprimoramentos de perna (12 IDs)**, 0 falhas → [`encantamentos_e_gemas_s2.json`](encantamentos_e_gemas_s2.json:1) |

### Por que a varredura por faixa foi necessária

As páginas de guia do Wowhead listam apenas parte das receitas: a de Encantamento mostrava 8 encantamentos, enquanto a faixa 243947–244037 contém **38**. Só a varredura revelou, por exemplo, os encantamentos de anel (`Encantamento da Aceleração Talassiana - Anel`), que não apareciam no guia.

### Achado que muda o cálculo

A varredura **não encontrou encantamento de pulsos, mãos nem capa** na temporada 2. Se isso se confirmar no jogo, o teto de encantamento por personagem cai para cabeça, ombros, peitoral, pés, dois anéis e arma. Registrado como pendência.

**Pernas é caso separado:** o slot não recebe encantamento, recebe **Magilinha** (*Spellthread*, Alfaiataria — ex.: \`Magilinha de Arcanotrama\`, \`240154\`/\`240155\`) ou **Kit de Armadura** (Couraria — ex.: \`Kit de Armadura do Caçador da Floresta\`, \`244640\`/\`244641\`). São 6 nomes em 12 IDs, catalogados na seção 2.2 de [\`encantamentos_e_gemas_s2.md\`](encantamentos_e_gemas_s2.md:1).

**Cada encantamento existe em duas qualidades** (dois IDs, mesmo nome no tooltip): 38 nomes = 76 IDs. A primeira versão deste relatório contava só 38 e por isso parecia faltar encantamento de botas, ombros e arma.

### Regra de nome que passou a valer

Todo nome em qualquer documento do projeto é **cópia literal do tooltip oficial PT-BR** (\`locale=8\`), inclusive o sufixo de slot que o cliente imprime (\`- Torso\`, \`- Elmo\`, \`- Ombros\`, \`- Botas\`, \`- Anel\`, \`- Arma\`). Nenhum nome é tradução livre.

```bash
node tools/auditar_armas_craft.js        # regrava craft_armas_s2.json (24 armas)
node tools/varrer_itens.js --gravar 240840 240990   # atualiza o cache de varredura
node tools/auditar_encantamentos_gemas.js           # regrava encantamentos_e_gemas_s2.json
node tools/gerar_doc_encantamentos_gemas.js         # regera o .md a partir do .json
```

## Terceira rodada — item craftado não tem atributo nem efeito fixos

Correção estrutural, apontada pelo usuário ao comparar as fichas com o item equipado dele.

| O que estava escrito | O que é verdade | Onde foi corrigido |
| :--- | :--- | :--- |
| “Lanterna de Aln'hara — Missiva: Aceleração + Maestria” | peça craftada **não tem** secundário fixo: o tooltip traz *“Atributo Aleatório 1/2”* e quem define é a **missiva** na ordem | fichas do Demo, do Shadow e do Balance (`.md` e `.json`) |
| “Embelezamento: Signo de Negraluna: Caçada” como se fosse do item | embelezamento é **reagente opcional**, logo é escolha; o item sai sem efeito se não for aplicado | mesmos arquivos + [`mplus_loot_database.json`](mplus_loot_database.json:1) |
| “Pedra Ritual do Caçador não vale na Lanterna” (tooltip) | o tooltip do reagente diz “Armas de Ferraria”, **mas** há Lanterna de Escrivania com o proc de 101 de secundário e +50% em Caça às Presas — item do próprio usuário | divergência registrada em [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1) §5.1 e em [`pendencias.md`](pendencias.md:1) §3.10 |

### Regra que passou a valer em todo documento

1. Ficha de item craftado lista **apenas os atributos fixos** (primário, Vigor, armadura).
2. Secundários aparecem como **recomendação** + lista das **6 missivas** possíveis.
3. Embelezamento aparece como **lista de opções válidas do slot**, nunca como propriedade da peça.
4. A combinação real do jogador (print ou `crafted_stats` do export) é dado **do personagem**, não do item.
5. Quando o item de jogo contradiz o tooltip, **o item vence para aquele personagem** e o conflito fica aberto — não se generaliza a exceção para o catálogo.

Método completo em [`00-INSTRUCOES-IA.md`](00-INSTRUCOES-IA.md:1), seção 1.7.

---

## Quarta rodada — varredura de lacunas (encantamentos, gemas, embelezamentos)

Cruzamento do DB2 `SpellItemEnchantment` (5.338 linhas) contra o catálogo, mais fontes web.

| Frente | Resultado |
| :--- | :--- |
| **Encantamentos de equipamento** | **Completo.** 126 linhas de encantamento no DB2; os 76 IDs mapeados cobrem todos os `Enchant <slot>` de combate. O resto é ferramenta, óleo, tinker e ilusão |
| **Embelezamentos** | **Completo.** O patch 12.1 adiciona **exatamente 5** (Adorned Fang, Snakeskin Lining, Polished Ammolite, Hunter's Ritual Stone, Coiled Snake-Eye) — todos catalogados |
| **Gemas** | **Completo.** 4 famílias de cor × 2 níveis + 4 diamantes × 2 níveis. As “Amani” da página de Joalheria são decoração de casa |
| **Óleos de arma** | **Lacuna fechada:** 8 `enchant_id` — Fênix Talassiano `8051`/`8052`, Aurora `8053`/`8054`, **Gume Encantado do Contrabandista `8055`/`8056`** (faltava no guia) e **Olho de Lince do Contrabandista `8612`/`8613`** (efeito não confirmado) |
| **Tinker de elmo** | **Lacuna fechada:** **R0CKY** `8702` / item `275676` — queda lenta por 2 min, ocupando a linha do encantamento de elmo |
| **Runa Vantus** | **Corrigida duas vezes.** 1ª: *O Abismo Venenoso* não existe — a runa da temporada é **Marés** (`272194` +130 / `272195` +162, Templo de Ula'tek). 2ª (2026-11-05, fonte: receita `1290561` do Wowhead): a **Resplandecente** (`245879` +259 / `245880` +324) **não** é runa alternativa — é **insumo** do craft da Marés, e a aura dela só vale contra chefes da Temporada 1 |
| **Encantamentos de ferramenta** | 6 nomes / 12 IDs mapeados com nome PT-BR, fora do cálculo de combate |

### Correções numéricas que a varredura pegou

| Item | Estava | Correto |
| :--- | :--- | :--- |
| Óleo da Aurora | *(eu registrei aqui que o ID 243736 e o valor 1.879 estariam errados)* | **Retratação:** `243735` (ilvl 278, **1.503**) e `243736` (ilvl 295, **1.879**) são **duas qualidades do mesmo óleo**. O documento original estava certo; a "correção" desta rodada foi o erro |
| Óleo de arma × encantamento | “o slot do óleo é sempre o Fênix Talassiano”, sugerindo exclusividade | **coexistem**: 1 óleo temporário (120 min) + 1 encantamento permanente |

```bash
node tools/analisar_enchant_db2.js --midnight    # DB2 x catálogo: o que falta
node tools/consultar_enchant_id.js 8702 8056     # nome oficial + efeito do feitiço
node tools/dump_enchant_row.js 8051              # linha crua do DB2
node tools/mapear_enchant_ids.js                 # reconstrói o mapa (97 IDs)
```
