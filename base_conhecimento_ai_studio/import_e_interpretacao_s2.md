# Importação e Interpretação de Exports SimC — Especificação do Módulo

**Projeto:** WoW Calculator — Season 2
**Patch de referência:** 12.1.5 — A Maldição de Ula'tek (*The Curse of Ula'tek*)
**Formato de entrada:** SimulationCraft AddOn Export — `SimC AddOn 12.1.5-03`
**Documento irmão:** [`rune_ids_s2.json`](rune_ids_s2.json:1)

> 📌 **Antes deste módulo, leia o método:** [`00-INSTRUCOES-IA.md`](00-INSTRUCOES-IA.md:1). Este arquivo descreve como **ler** o export; o documento mestre descreve **o que fazer com ele** — em especial o protocolo de substituição (portões G0–G8) da seção 3.2, usado quando o usuário cola um export e pergunta se vale trocar uma peça.
**Última atualização:** 2026-11-05

---

# PARTE 0 — ESCOPO E DECISÃO ARQUITETURAL

## 0.1 Princípio fundador: interpretar, não simular

Este módulo **não calcula DPS**. Ele não reimplementa o SimulationCraft nem o Raidbots. A função dele é:

1. Ler o export do personagem e reconstruir o estado real (equipamento, talentos, runas, moedas, marcas de ilvl).
2. Cruzar esse estado com as bases de conhecimento já catalogadas no projeto.
3. Emitir **juízo situacional**: o que está adequado, o que está fora do lugar, o que buscar e por quê.

A diferença é a mesma entre um simulador e um consultor. O simulador responde "qual dos dois itens dá mais dano no patchwerk". O consultor responde "seu elmo é o tier regular e o BiS é o cantrip, e como o Catalyst S2 preserva cantrip, o alvo é o cantrip, não o tier".

Toda regra deste documento deve ser capaz de justificar o veredito **citando evidência textual e um arquivo do workspace**. Regra que não consegue citar evidência não entra.

## 0.2 ADR-001: apenas SimC AddOn; AskMrRobot fica fora de escopo

**Decisão:** o único formato de entrada suportado é o export do SimulationCraft AddOn.

**Contexto:** foram analisados dois exports do mesmo personagem, um no formato AskMrRobot `$181;US;Azralon;...` e outro no formato SimC AddOn.

**Achado que fundamenta a decisão:** os dois formatos carregam a mesma informação, mas o SimC é texto legível e auto-documentado. A prova cruzada foi feita no item `239648` (Braceletes do Mártir):

| Sinal | No AMR v181 | No SimC AddOn |
|---|---|---|
| Identificador do item | `239648s9n3615...` | `wrist=,id=239648` |
| Bônus aplicado | `b8790` | `bonus_id=.../8790/...` |
| Atributos de craft | `j36k32` | `crafted_stats=36/32` |
| Tuning de conteúdo | `n3615` | `content_tuning=3615` |
| Encantamento | `e7981` | `enchant_id=7981` |

> 🔧 **`enchant_id` não é o ID do pergaminho.** Ele é o ID da linha de `SpellItemEnchantment` — **uma por qualidade** (Tier 1 e Tier 2 do mesmo encantamento). Por isso `7981` não aparece em nenhum catálogo de item: `7981` = **Encantamento de Precisão de Jan'alai - Arma, Tier 2** (pergaminho `243971`). A tradução está em [`enchant_ids_s2.json`](enchant_ids_s2.json:1), gerada por [`tools/mapear_enchant_ids.js`](tools/mapear_enchant_ids.js:1) a partir do DB2 público `SpellItemEnchantment` (Wago Tools).
>
> ```bash
> node tools/mapear_enchant_ids.js 7981   # resolve um enchant_id do export
> ```
>
> **Regra:** ao ler um export, traduza **todo** `enchant_id` antes de concluir qualquer coisa sobre a arma. Encantamento de arma é parte do dano, não detalhe cosmético.

**Consequências:**

| Ganho | Perda |
|---|---|
| Zero engenharia reversa de formato binário proprietário | Perde-se o histórico de aquisição de itens (`.inv`) |
| Sem risco de quebra por mudança de versão do addon (`$181`) | Perde-se a lista de achievement IDs (`.ach`) |
| Fonte única de verdade, com comentários PT-BR, track de ilvl e nomes de item | — |
| Loadouts salvos continuam disponíveis via comentários `# Saved Loadout:` | — |

**Alternativa descartada:** suportar os dois com adapters. Descartada porque o AMR não agrega dado decisório e dobraria a superfície de manutenção.

**Revisão:** só reabrir esta ADR se surgir necessidade de histórico de aquisição ou de dados que apenas o AMR exponha.

**REVISÃO PARCIAL em 2026-11-05:** surgiu exatamente esse caso, e é pequeno. O export SimC **não** informa qual runa do Folio Ômnico está escolhida dentro de cada linha — `omnium_talents` traz um nó por linha, com rank 1, o que é estado de desbloqueio. O export AMR, nas seções `.s2` e `.s3`, traz a escolha real no formato `<spell_id>=<rank>`. Decisão: **não** reabrir o parser AMR; em vez disso, exigir um campo opcional `runas_atuais` no formulário de entrada. Detalhes em [`rune_ids_s2.json`](rune_ids_s2.json:1), chave `limitacao_critica_para_r5`.

**REVISÃO PARCIAL em 2026-11-05:** surgiu exatamente esse caso, e é pequeno. O export SimC **não** informa qual runa do Folio Ômnico está escolhida dentro de cada linha — `omnium_talents` traz um nó por linha, com rank 1, o que é estado de desbloqueio. O export AMR, nas seções `.s2` e `.s3`, traz a escolha real no formato `<spell_id>=<rank>`. Decisão: **não** reabrir o parser AMR; em vez disso, exigir um campo opcional `runas_atuais` no formulário de entrada, preenchido pelo usuário. Detalhes em [`rune_ids_s2.json`](rune_ids_s2.json:1), chave `limitacao_critica_para_r5`.

## 0.3 Fora de escopo explícito

- Simulação de DPS, HPS ou sobrevivência.
- Comparação de dois itens por ganho numérico de throughput.
- Leitura direta da API da Blizzard ou do armory.
- Parser do formato AMR v181.
- Interface gráfica. O insumo é texto colado e a saída é relatório em Markdown.

---

# PARTE 1 — CONTRATO DE ENTRADA

## 1.1 Detecção e normalização

O parser recebe uma string multilinha colada pelo usuário. Antes de qualquer decodificação:

1. **Descartar linhas em branco nas extremidades** e normalizar quebras de linha `\r\n` → `\n`.
2. **Detectar o formato pelo primeiro caractere útil**:
   - começa com `#` seguido de nome de personagem e `- Spec - data` → SimC AddOn, **aceitar**;
   - começa com `$` → AMR v181, **rejeitar** com mensagem explícita: *"Este projeto lê apenas o export do SimulationCraft AddOn. No jogo, use `/simc` e cole a saída."*
   - qualquer outro início → rejeitar com `alerta_parse: formato_desconhecido`.
3. **Preservar o texto bruto original** em `CharacterState.raw` para auditoria e para os golden files da Parte 6.

## 1.2 Gramática geral

O formato tem três tipos de linha:

| Tipo | Sintaxe | Tratamento |
|---|---|---|
| Cabeçalho de comentário | `# texto` | Metadado. Alguns são semanticamente relevantes (`# Saved Loadout:`, `# <nome PT-BR> (<ilvl>)`) |
| Chave-valor | `chave=valor` | Núcleo. Chaves repetidas são permitidas apenas em seções específicas |
| Separador de seção | `### Nome da Seção` | Delimita blocos; muda a semântica das linhas seguintes |

**Regra de ouro:** a mesma chave aparece com semânticas diferentes em seções diferentes. `neck=` no bloco principal é o item equipado; `neck=` em `### Gear from Bags` é uma alternativa na mochila. O parser **precisa** de máquina de estados por seção, não de um dicionário plano.

## 1.3 Mapa de seções

| Seção no arquivo | Delimitador | O que contém | Uso no motor |
|---|---|---|---|
| Cabeçalho | até a primeira linha `talents=` | Identidade, nível, raça, spec, profissões | Contexto e normalização |
| Talentos | `talents=` | Import string da árvore | R11 |
| Runas | `omnium_talents=` | 5 pares `rune_id:rank` | R5 |
| Equipamento | `head=` … `main_hand=` | Itens equipados | R1, R2, R3, R4, R12 |
| Loadouts salvos | linhas `# Saved Loadout: X` + `# talents=Y` | Builds nomeadas pelo usuário | R11 |
| Gear from Bags | `### Gear from Bags` | Alternativas na mochila (comentadas com `#`) | R7 |
| Additional Character Info | `### Additional Character Info` | Moedas, marcas de ilvl, achievements, extra rolls | R7, R8, R9 |
| Checksum | `# Checksum: <hex>` | Assinatura | Deduplicação de exports idênticos |

## 1.4 Campos do cabeçalho

| Campo | Exemplo do export real | Semântica | Confiança |
|---|---|---|---|
| `warlock=` / `druid=` / `priest=` | `warlock="Pyrogalth"` | Nome do personagem; a chave é a classe | Confirmado |
| `level` | `90` | Nível — Season 2 opera no teto de 90 | Confirmado |
| `race` | `dracthyr` | Raça, relevante para passivas raciais | Confirmado |
| `region` | `us` | Região | Confirmado |
| `server` | `azralon` | Reino | Confirmado |
| `role` | `spell` | Papel — `spell` = conjurador DPS | Confirmado |
| `professions` | `alchemy=100/enchanting=100` | Profissões e skill; define se o personagem **pode** consumir o que se recomenda | Confirmado |
| `spec` | `demonology` | Especialização ativa | Confirmado |
| `# loot_spec=<spec>` | `# loot_spec=demonology` | Loot spec ativa. **Comentada** — presente mas opcional | Confirmado |

**Regra derivada:** se `professions` não incluir `alchemy`, o motor não pode recomendar frascos e poções como "craftáveis por você" — apenas como item de leilão. Idem para `enchanting` com óleos de arma.

## 1.5 Gramática do bloco de equipamento

Forma canônica:

```
<slot>=,id=<item_id>,enchant_id=<id>,gem_id=<id>,bonus_id=<a>/<b>/<c>,content_tuning=<id>,crafted_stats=<a>/<b>,crafting_quality=<n>,redirected_base_stats=<id>
```

Nem todos os campos aparecem em todo slot. Tabela de presença observada no export real:

| Slot | `id` | `enchant_id` | `gem_id` | `bonus_id` | `content_tuning` | `crafted_stats` |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| `head` | ✅ | ✅ | ✅ | ✅ | — | — |
| `neck` | ✅ | — | ✅ | ✅ | — | — |
| `shoulder` | ✅ | ✅ | — | ✅ | — | — |
| `back` | ✅ | — | — | ✅ | ✅ | ✅ |
| `chest` | ✅ | ✅ | — | ✅ | — | — |
| `tabard` | ✅ | — | — | — | ✅ | — |
| `wrist` | ✅ | — | — | ✅ | ✅ | ✅ |
| `hands` | ✅ | ✅ | — | ✅ | — | — |
| `waist` | ✅ | — | ✅ | ✅ | — | — |
| `legs` | ✅ | ✅ | — | ✅ | — | — |
| `feet` | ✅ | ✅ | — | ✅ | — | — |
| `finger1` / `finger2` | ✅ | ✅ | ✅ | ✅ | ✅ (`finger2`) | — |
| `trinket1` / `trinket2` | ✅ | — | — | ✅ | — | — |
| `main_hand` | ✅ | ✅ | — | ✅ | — | — |
| `off_hand` | ✅ | — | — | ✅ | — | — |

**Regras de leitura:**

- Slots ausentes do bloco principal = slot vazio. O personagem do export usa cajado de duas mãos, portanto não há `off_hand` equipada.
- Uma linha de slot **comentada** (`# neck=,id=...`) dentro de `### Gear from Bags` **não** é item equipado.
- `redirected_base_stats` indica item com atributos primários redistribuídos (comum em tier e em itens cantrip). O motor deve registrar mas **não** tentar inferir stats a partir dele.
- O comentário imediatamente acima de cada slot traz nome PT-BR e ilvl entre parênteses: `# Crânio do Necrólito Maldito (321)`. Esse é o caminho mais confiável para obter **ilvl** e **nome PT-BR** sem consulta externa.

## 1.6 Bloco `### Additional Character Info`

Todos os valores deste bloco vêm comentados (`# `). São eles:

| Chave | Exemplo | Semântica | Confiança |
|---|---|---|---|
| `catalyst_currencies` | `2813:8/3269:8/3116:8/...` | Cargas de Catalyst por tier de conteúdo (`id:cargas`) | Alta — formato inferido |
| `upgrade_currencies` | `c:1792:4668/c:2122:22/i:280562:3/...` | Brasões (`c:`) e itens (`i:`) com quantidade | Alta |
| `slot_high_watermarks` | `0:321:321/1:341:341/.../14:259:305` | `índice_slot:ilvl_atual:ilvl_max_histórico` | **Média** — ver 1.7 |
| `upgrade_achievements` | `19577/19578/...` | IDs de conquista de upgrade | Alta |
| `bonus_roll_currencies` | `3418:0/3511:0` | Moedas de extra roll e saldo | Alta |
| `bonus_roll_items` | `3418:279621:190:12:273649:266` | Item rolado, ilvl, resultado | Baixa — formato não decodificado |

## 1.7 O problema aberto das marcas de ilvl

`slot_high_watermarks` é a chave de maior valor e de maior incerteza. Ela responde "quanto ainda cabe neste slot antes de eu precisar de drop novo", o que é exatamente o tipo de juízo que este projeto quer emitir.

Valores reais do export analisado:

```
0:321:321  1:341:341  2:321:324  3:321:321  4:334:334
5:321:321  6:321:321  7:331:331  8:321:321  9:321:321
10:341:341 11:331:331 12:341:341 13:321:321 14:259:305
15:256:256 16:334:334
```

Distribuição dos ilvls equipados no mesmo personagem: `321` sete vezes, `331` duas, `334` duas, `341` quatro. A lista de marcas tem `321` oito vezes, `341` três, `331` duas, `334` duas, mais `259` e `256` isolados.

**Conclusão honesta:** os índices **não** batem com nenhuma ordenação óbvia — nem com a ordem alfabética de slots do SimC, nem com a ordem de exibição do paperdoll. Há 17 entradas e o personagem tem 15 slots preenchidos, então dois índices correspondem a slots vazios.

**O que já é seguro afirmar:**

- O índice `14` é o único em que o ilvl atual está **abaixo** da própria marca máxima (`259` contra `305`). Isso indica slot historicamente preenchido com item melhor e hoje ocupado por item inferior.
- Os valores `259` e `256` não aparecem em nenhum item equipado, confirmando que esses dois índices são os slots vazios.
- Os pares são monotônicos (`atual ≤ máximo`) em 17 de 17 entradas, o que valida a hipótese de que a segunda coluna é o máximo histórico.

**Protocolo para fechar o mapa:** coletar exports de 3 personagens com composições de slot diferentes (um com off-hand, um sem trinket, um com dois anéis de ilvl distinto). A interseção das posições que mudam de valor identifica cada índice sem ambiguidade. **Enquanto isso não for feito, R7 lê a chave apenas para o índice 14 e marca os demais como `informativo`.**

---

# PARTE 2 — DECODIFICAÇÃO PARA `CharacterState`

## 2.1 Tabela de tokens e confiança

| Token | Campo | Interpretação | Confiança | Impacto se errado |
|---|---|---|---|---|
| `id=` | item id | Identificador único do item | Confirmado | Nenhum |
| `enchant_id=` | encantamento | ID de encantamento aplicado | Confirmado | Baixo |
| `gem_id=` | gema | ID de gema engastada | Confirmado | Baixo |
| `bonus_id=` | modificadores | Lista de bônus que definem track, terciário, engaste e marca de tier | **Parcial** | Alto — define track e tier |
| `crafted_stats=a/b` | atributos de craft | IDs de atributo na ordem escolhida | **Alta** | Médio |
| `content_tuning=` | tuning de conteúdo | Origem/escala do item | **Média** | Médio |
| `crafting_quality=` | qualidade | 1 a 5 | Confirmado | Baixo |
| `redirected_base_stats=` | base redirecionada | Item com primário remapeado | Alta | Baixo |
| `talents=` | árvore | Import string | Confirmado | Alto |
| `omnium_talents=` | runas | `rune_id:rank` | Confirmado | Alto |

## 2.2 Interpretação de `crafted_stats` — validação real

Os IDs de atributo seguem a numeração de `ItemModType` do cliente:

| ID | Atributo |
|:-:|---|
| 32 | Acerto Crítico (*Critical Strike*) |
| 36 | Aceleração (*Haste*) |
| 40 | Versatilidade (*Versatility*) |
| 49 | Maestria (*Mastery*) |

Validação contra o export: o item `239648` (Braceletes do Mártir) vem com `crafted_stats=36/32`, ou seja **Aceleração + Crítico**. Em [`demonology_warlock.json`](demonology_warlock.json:109) a recomendação para esse mesmo item é literalmente `"Aceleração + Crítico"`. Confirmação cruzada bem-sucedida.

O item `239656` (capa craftada) vem com `crafted_stats=32/40` → **Crítico + Versatilidade**. Este é um desvio que o motor deve sinalizar: a prioridade declarada do Demo Warlock em M+ é `Aceleração > Crítico > Maestria > Versatilidade`, ver [`mplus_loot_database.json`](mplus_loot_database.json:97), e a capa está com Versatilidade no lugar de Aceleração ou Maestria.

## 2.3 `bonus_id` — classificação parcial

Existem séries reconhecíveis pelos valores observados:

| Série | Exemplos no export | Hipótese de função | Confiança |
|---|---|---|---|
| `128xx` | `12846`, `12854`, `12856`, `12843`, `12848`, `12841`, `12835`, `12817`, `12818` | Track de upgrade / nível de dificuldade do item | **Média** |
| `1369x` | `13690`, `13691`, `13692`, `13693`, `13694`, `13695`, `13696`, `13697`, `13698` | Marca de peça de tier set | **Média-alta** |
| `6652`, `13440`, `12699` | — | Atributo terciário (sorte/velocidade/absorção) | Baixa |
| `12214`, `12249` | — | Marca de item craftado | Média |
| `40`, `41`, `42`, `43` | `41` em `legs` | Modificador de stat secundário adicional | Baixa |
| `1574`, `1587` | — | Variante de ilvl dentro do mesmo track | Baixa |

**Regra de engenharia:** nunca derivar track a partir de `bonus_id` sozinho. A fonte confiável de track é o **comentário de ilvl** da linha (`# ... (321)`) combinado com a tabela `tabela_ilvl_mplus` de [`mplus_loot_database.json`](mplus_loot_database.json:29). `bonus_id` serve como desempate e como assinatura de tier.

### 2.3.1 Método empírico validado (2026-11-05)

As hipóteses acima foram testadas contra a fonte e parcialmente confirmadas. O método que funciona não é adivinhar séries: é consultar o tooltip do item **com a lista exata de bônus do export**.

```
https://nether.wowhead.com/tooltip/item/<item_id>?dataEnv=1&locale=3&bonus=<id>%3A<id>%3A<id>
```

Retorna `application/json` com nome, ilvl, rótulo de track e o texto integral do efeito, já com todos os bônus aplicados. Custo: 1 crédito por item.

Resultado dos três tracks em uso no export:

| bonus_id | Track | ilvl observado | Item de prova |
|---|---|---|---|
| `12846` | Herói 6/6 | 321 | `271546` (head) |
| `12854` | Mítico 6/6 | 334 | `271543` (waist) |
| `12856` | Mítico (dificuldade de raide) | 341 | `273781` (neck) |

Achado que invalida a heurística anterior: `12854` e `12856` produzem o **mesmo rótulo "Mythos"** com ilvl diferentes (334 e 341). O rótulo não distingue track de dificuldade. Portanto o ilvl é a âncora, e `bonus_id` nunca deve ser lido isoladamente.

Tabela completa, evidências e próximos passos em [`bonus_ids_s2.json`](bonus_ids_s2.json:1).

### 2.3.2 Correção aplicada por este método

O bônus de 4 peças do Demonology Warlock estava divergente entre duas bases. O tooltip oficial do item `271546` resolveu: **350% no alvo principal e 315% nos secundários**. [`season2_context.json`](season2_context.json:842) foi corrigido; [`demonology_warlock.json`](demonology_warlock.json:23) já estava certo.

### 2.3.3 Como detectar tier sem depender da série

O teste com os bônus `13692/13695/13698` retornou o conjunto `(0/5)` com os bônus de 2pc e 4pc por spec. Isso confirma que a família aparece em itens de tier, mas **não isola qual dos três é o marcador**. A detecção confiável é pela pertinência ao conjunto no texto do tooltip, ou por mapa explícito de `item_id`, não pela série.

## 2.4 Schema canônico

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CharacterState",
  "type": "object",
  "required": ["meta", "identidade", "talentos", "equipamento", "runas_folio", "alertas_parse"],
  "properties": {
    "meta": {
      "type": "object",
      "required": ["formato", "versao_addon", "patch", "checksum"],
      "properties": {
        "formato": { "const": "simc_addon" },
        "versao_addon": { "type": "string", "example": "12.1.5-03" },
        "patch": { "type": "string", "example": "12.1.5.70783" },
        "toc": { "type": "string", "example": "120105" },
        "checksum": { "type": "string" },
        "gerado_em": { "type": "string", "format": "date-time" }
      }
    },
    "identidade": {
      "type": "object",
      "required": ["nome", "classe", "spec", "nivel", "reino", "regiao"],
      "properties": {
        "nome": { "type": "string" },
        "classe": { "type": "string" },
        "spec": { "type": "string" },
        "nivel": { "type": "integer" },
        "raca": { "type": "string" },
        "reino": { "type": "string" },
        "regiao": { "type": "string" },
        "papel": { "type": "string" },
        "loot_spec": { "type": ["string", "null"] },
        "profissoes": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "nome": { "type": "string" },
              "skill": { "type": "integer" }
            }
          }
        }
      }
    },
    "talentos": {
      "type": "object",
      "properties": {
        "import_string_ativa": { "type": "string" },
        "hero_tree_inferida": { "type": ["string", "null"] },
        "loadouts_salvos": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "nome": { "type": "string" },
              "import_string": { "type": "string" },
              "corresponde_a_ativa": { "type": "boolean" }
            }
          }
        }
      }
    },
    "equipamento": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": ["item_id"],
        "properties": {
          "item_id": { "type": "integer" },
          "nome_pt": { "type": ["string", "null"] },
          "ilvl": { "type": ["integer", "null"] },
          "track": { "type": ["string", "null"] },
          "enchant_id": { "type": ["integer", "null"] },
          "gem_id": { "type": ["integer", "null"] },
          "bonus_ids": { "type": "array", "items": { "type": "integer" } },
          "crafted_stats": {
            "type": "array",
            "items": { "type": "integer" },
            "description": "IDs de ItemModType: 32=Crit, 36=Haste, 40=Vers, 49=Mastery"
          },
          "crafting_quality": { "type": ["integer", "null"] },
          "content_tuning": { "type": ["integer", "null"] },
          "redirected_base_stats": { "type": ["integer", "null"] },
          "eh_tier": { "type": "boolean" },
          "eh_cantrip": { "type": "boolean" },
          "origem": { "type": "string", "enum": ["equipado", "mochila"] }
        }
      }
    },
    "runas_folio": {
      "type": "array",
      "minItems": 0,
      "maxItems": 5,
      "items": {
        "type": "object",
        "required": ["rune_id", "rank"],
        "properties": {
          "rune_id": { "type": "integer" },
          "rank": { "type": "integer" },
          "patamar": { "type": ["integer", "null"] },
          "escolha": { "type": ["string", "null"] },
          "codigo_cxx": { "type": ["string", "null"] }
        }
      }
    },
    "marcas_ilvl": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "indice": { "type": "integer" },
          "ilvl_atual": { "type": "integer" },
          "ilvl_maximo": { "type": "integer" },
          "slot_resolvido": { "type": ["string", "null"] }
        }
      }
    },
    "moedas": {
      "type": "object",
      "properties": {
        "catalyst": { "type": "object" },
        "upgrades": { "type": "object" },
        "bonus_roll": { "type": "object" }
      }
    },
    "alertas_parse": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "codigo": { "type": "string" },
          "severidade": { "type": "string", "enum": ["bloqueante", "alto", "medio", "baixo", "informativo"] },
          "mensagem": { "type": "string" },
          "linha": { "type": "integer" }
        }
      }
    },
    "raw": { "type": "string", "description": "Texto original colado, preservado para auditoria" }
  }
}
```

## 2.5 Códigos de alerta de parse

| Código | Significado | Ação |
|---|---|---|
| `formato_desconhecido` | Não é SimC nem AMR | Abortar, pedir novo export |
| `formato_amr_rejeitado` | É AMR v181 | Abortar com instrução de usar `/simc` |
| `omnium_incompleto` | `omnium_talents` com menos de 5 runas | R5 vira `informativo` |
| `runas_nao_verificadas` | IDs ausentes de [`rune_ids_s2.json`](rune_ids_s2.json:1) como confirmados | R5 suprime veredito |
| `slot_sem_ilvl` | Linha de slot sem comentário de ilvl | R7 e R8 suprimidas para o slot |
| `high_watermark_nao_mapeado` | Índice de `slot_high_watermarks` não resolvido | R7 parcial, apenas índice 14 |
| `bonus_id_desconhecido` | Bônus fora das séries catalogadas | Registrar, não bloquear |
| `profissao_divergente` | Recomendação exige profissão que o personagem não tem | R10 ajusta para "comprar no leilão" |

---

# PARTE 3 — MOTOR DE REGRAS

## 3.0 Formato do veredito

Toda regra emite objetos deste tipo:

```json
{
  "regra": "R1",
  "slot": "head",
  "severidade": "alto",
  "veredito": "O elmo equipado é o tier regular 271546; o BiS é o cantrip 271874.",
  "evidencia": [
    "item_id 271546 ≠ 271874",
    "tier já está em 5/5, então trocar o elmo não quebra o 4pc",
    "Catalyst S2 preserva efeito cantrip, logo o cantrip pode virar tier"
  ],
  "acao": "Priorizar Ula'tek e gastar Núcleo Vazio Nebuloso nele.",
  "fontes": [
    "demonology_warlock.json#gear.bis_overall.slots.helm",
    "season2_context.json#itens_cantrip"
  ]
}
```

Severidades: `bloqueante` (impede recomendação), `alto` (perda relevante), `medio` (subótimo), `baixo` (cosmético), `informativo` (observação).

## 3.1 Tabela-resumo

| Regra | Pergunta | Entradas |
|---|---|---|
| R1 | Slot abaixo do BiS da situação | CharacterState, ficha de spec, season2_context |
| R2 | Saldo de atributos fora da prioridade | CharacterState, mplus_loot_database |
| R3 | Distância para o 4pc de tier | CharacterState, ficha de spec |
| R4 | Conflito de arquétipo de trinket | CharacterState, ficha de spec |
| R5 | Runas do Folio batem com o recomendado | CharacterState, rune_ids_s2, consumiveis |
| R6 | Códice aplicado onde é inativo | CharacterState, talent_builds_season2 |
| R7 | Upgrade barato por Brasão antes de caçar drop | CharacterState, marcas de ilvl, tabela ilvl |
| R8 | BiS de Raid num slot já coberto por M+ | CharacterState, season2_context |
| R9 | Extra roll sendo gasto no boss certo | CharacterState, prioridade de Voidcore |
| R10 | Consumíveis corretos para a situação | CharacterState, consumiveis |
| R11 | Build ativa é a certa para a situação | CharacterState, talent_builds_season2 |
| R12 | Cantrip não catalisado onde tier daria 4pc **+ regra do Catalisador** (peça Mítica → tier Mítico) | CharacterState, ficha de spec, season2_context |

## 3.2 Detalhamento

### R1 — Coerência de slot contra o BiS

- **Pergunta:** para a situação informada, o item equipado é o recomendado?
- **Condição de disparo:** `item_id` do slot ≠ `item_id` do BiS mapeado para aquela situação.
- **Graduação da severidade:**
  - `alto` se o BiS tem efeito cantrip e o equipado não tem;
  - `medio` se ambos não têm efeito e a diferença é só de stats;
  - `baixo` se o slot é de tier e a diferença é apenas de track.
- **Anti falso-positivo:** aceitar como equivalente quando o item equipado é o **mesmo efeito** obtido por Catalyst de outra fonte (o Catalyst S2 preserva stats e efeito). Comparar por efeito, não por ID, quando ambos têm `eh_cantrip = true`.
- **Saída:** veredito + ação de aquisição (boss ou dungeon) + se cabe extra roll.

### R2 — Saldo de atributos

- **Pergunta:** a soma dos secundários equipados respeita a prioridade da spec naquela situação?
- **Entrada de prioridade:** [`mplus_loot_database.json`](mplus_loot_database.json:96) → `pesos_de_atributo.<spec>.<situacao>.prioridade`.
- **Cálculo permitido:** somar `crafted_stats` decodificados e os stats numéricos já catalogados nas fichas. **Não** estimar stat de item desconhecido.
- **Condição:** o atributo de maior peso não é o de maior soma, ou o de menor peso tem soma comparável ao primeiro.
- **Severidade:** `medio`; `baixo` se a diferença for menor que a margem de um único item.
- **Limite explícito:** a regra aponta desalinhamento, não quantifica perda de dano.

### R3 — Distância para o 4pc

- **Pergunta:** quantas peças de tier faltam para fechar o bônus de 4 peças?
- **Como contar:** slots com `eh_tier = true`, onde `eh_tier` é derivado da série `1369x` em `bonus_id` **ou** do item mapeado como tier na ficha da spec. Contagem máxima útil é 5; acima de 4 é redundante.
- **Condição:** contagem < 4.
- **Saída:** quais slots trocar e qual o caminho mais curto (Catalyst de qual dungeon, ou Great Vault).
- **Caso especial:** tier via Catalyst de Templo de Sethraliss para Demo Warlock, registrado em [`season2_context.json`](season2_context.json:302).

### R4 — Conflito de arquétipo de trinket

- **Pergunta:** os dois trinkets equipados competem pelo mesmo recurso?
- **Como classificar:** `tipo_efeito` da ficha de spec (`ativo`, `passivo`, `hibrido`).
- **Condição:** ambos `ativo`.
- **Severidade:** `alto` — dois on-use dividem recarga e se anulam parcialmente.
- **Saída:** qual manter por situação e qual substituir por passivo.
- **Validação no export real:** `273649` (Emblema Tempestuoso de Dazar, ativo) + `273796` (Ampola Torpe, ativo) → conflito confirmado. O par BiS em [`demonology_warlock.json`](demonology_warlock.json:339) é `281215` (passivo) + `270164` (passivo).

### R5 — Folio Ômnico

- **Pergunta:** as runas equipadas correspondem ao código Cxx recomendado para a situação?
- **Limitação estrutural descoberta em 2026-11-05:** `omnium_talents` **não** contém a escolha, apenas o nó de cada linha com rank 1. Um personagem com o sistema desbloqueado sempre exporta exatamente 5 nós, independentemente das runas escolhidas. Portanto R5 é **impossível** apenas com entrada SimC.
- **Entrada adicional obrigatória:** campo opcional `runas_atuais` no formulário, com os 5 spell IDs ou a combinação em formato `1A-2B-3A-4A-5A`. Sem esse campo, R5 degrada para `informativo` listando apenas quais linhas estão desbloqueadas.
- **Pré-condições:** `runas_atuais` preenchido e todas as runas correspondentes em [`rune_ids_s2.json`](rune_ids_s2.json:1) com `status_verificacao = "confirmado"`.
- **Como decidir:** mapear os spell IDs para linha e escolha, derivar o `Cxx` pela fórmula de `derivacao_codigo_cxx` — **72 combinações, não 54** — e comparar com o código da matriz situacional de [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:484).
- **Além do código:** sinalizar runas que contradizem a prioridade do spec — por exemplo linha 4 com Maestria quando a prioridade é Aceleração. A linha 4 tem **quatro** opções, incluindo a de Versatilidade, ausente na documentação atual do projeto.
- **Saída:** código atual, código recomendado, diff por linha.

### R6 — Códice Corrosivo e regra de localização

- **Pergunta:** o motor está prestes a recomendar Códice num conteúdo onde ele é inativo?
- **Regra dura:** o Códice opera **exclusivamente** em mundo aberto e Imersões. Em Raide e M+ os poderes ficam inativos. Ver [`talent_builds_season2.json`](talent_builds_season2.json:357).
- **Condição:** situação ∈ {`raid`, `mplus`} e há recomendação de Códice na cadeia.
- **Severidade:** `bloqueante` — a recomendação deve ser removida da saída, não apenas marcada.
- **Saída:** par `Pxx` recomendado apenas em `delves` e `outdoor`.

### R7 — Upgrade barato antes de drop

- **Pergunta:** existe slot cujo teto de ilvl ainda permite ganho sem depender de sorte?
- **Entrada:** `marcas_ilvl` + `tabela_ilvl_mplus`.
- **Condição:** `ilvl_maximo − ilvl_atual` ≥ 13, valor de corte definido em [`mplus_loot_database.json`](mplus_loot_database.json:100) como a diferença que compensa stats subótimas.
- **Estado atual da regra:** parcial. Só avaliar índices cujo `slot_resolvido` estiver preenchido. No export analisado apenas o índice 14 satisfaz a condição (`259` → `305`).
- **Saída:** "gaste Brasão neste slot antes de caçar drop novo", com o nível de chave que gera o ilvl alvo.

### R8 — Raid contra M+ no mesmo slot

- **Pergunta:** o BiS alvo é de Raid num slot onde o personagem já tem cobertura alta via M+?
- **Entrada:** `fonte_tipo` de cada BiS em [`season2_context.json`](season2_context.json:386) e o ilvl atual do slot.
- **Condição:** BiS é `Raid`, o slot está com item `M+` dentro de 13 ilvl do track máximo acessível, e o extra roll já foi comprometido em outro boss.
- **Severidade:** `baixo` — o BiS continua sendo BiS, mas a fila de prioridade desce.
- **Saída:** reordenação explícita da fila de farm, com o motivo.

### R9 — Uso do Núcleo Vazio Nebuloso

- **Pergunta:** o extra roll está sendo gasto num boss que resolve um slot ainda aberto?
- **Entrada:** prioridade por spec em [`season2_context.json`](season2_context.json:748) + R1.
- **Condição:** boss escolhido não contém nenhum BiS de slot aberto, ou contém BiS de slot já resolvido.
- **Severidade:** `medio`.
- **Saída:** boss recomendado + estimativa de quantos BiS ainda abertos aquele boss cobre.
- **Detalhe de loot spec:** registrar a recomendação de loot spec divergente da ativa — `Holy` para Shadow Priest e `Restoration`/`Guardian` para Balance Druid em Ula'tek, conforme [`season2_context.json`](season2_context.json:171). Se `loot_spec` do export for igual à spec de dano, emitir aviso.
- **Cruzamento obrigatório com o Catalisador:** o valor de um boss para o Voidcore **não** se mede só pela lista de BiS. Se o boss dropa peça em **Head, Shoulder, Chest, Hands ou Legs** no track **Mítico**, esse drop vale como **peça de tier**: o Matrix Catalyst o converte no tier do spec mantendo o track e o nível (Mítico 6/6 → tier Mítico 6/6, ilvl 334). A ordem de prioridade está em [`mplus_loot_database.json`](mplus_loot_database.json:3288) (`catalisador_na_comparacao.ordem_de_prioridade_do_voidcore`):
  1. boss que dropa **BiS e slot de tier** no Mítico;
  2. boss que dropa **slot de tier no Mítico** quando faltam **2 ou mais** peças para o 4pc;
  3. boss que dropa **BiS de slot sem tier** (Cloak, Wrist, Waist, Feet, Neck, Ring, Trinket, Weapon, OffHand) — o Catalisador **nunca** resolve esses slots;
  4. boss que dropa slot de tier no Mítico quando falta **só 1** peça;
  5. boss que dropa **apenas tier de track Heroico** — o Catalisador já resolve isso com peça Heroica, então o Voidcore é desperdício.
- **Saída adicional:** quantos drops do boss são "tier-ready" (catalisáveis) e quantos são BiS de slot sem tier.

### R10 — Consumíveis

- **Pergunta:** a mochila e as escolhas ativas respeitam a matriz situacional?
- **Entrada:** [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:361) partes 3 e 4.
- **Condição:** atributo priorizado pelo frasco/comida difere da prioridade do spec na situação.
- **Ajuste por profissão:** se `professions` não tem `alchemy`, frascos e poções vêm do leilão; se não tem `enchanting`, óleos vêm do leilão; se não tem `inscription`, runas vêm do leilão.
- **Severidade:** `baixo` a `medio`.

### R11 — Build de talentos

- **Pergunta:** a árvore ativa é a recomendada para a situação?
- **Como comparar:** a `import_string` ativa costuma **não** ser idêntica a nenhum loadout salvo, porque o jogador edita talentos sem salvar. A comparação deve ser por **propriedades deriváveis**, não por igualdade de string:
  1. arquétipo de talentos heroicos inferido do prefixo e dos nós ativos;
  2. presença dos talentos-chave listados em [`talent_builds_season2.json`](talent_builds_season2.json:119);
  3. presença de defensivos obrigatórios para `delves`.
- **Condição:** arquétipo inferido ≠ arquétipo recomendado para a situação.
- **Saída:** arquétipo atual, arquétipo recomendado, e a lista de talentos-chave ausentes.
- **Limite:** se o parsing de talentos não estiver implementado, a regra degrada para apenas reportar a string ativa e comparar com os loadouts salvos por igualdade, marcando `severidade: informativo`.

### R12 — Cantrip contra tier (e a substituição por Catalisador)

- **Pergunta:** existe cantrip equipado sem catalisação ocupando slot que poderia fechar tier?
- **Condição:** R3 indica falta de peça de tier **e** há slot com `eh_cantrip = true` sem marca de tier em `bonus_id`.
- **Por que importa:** o Catalyst S2 preserva stats e efeitos especiais do item original ao converter para tier, conforme [`season2_context.json`](season2_context.json:49). Portanto o caminho ótimo é catalisar o cantrip, não substituí-lo.
- **Severidade:** `alto`.
- **Saída:** ordem exata de catalisação.

**A regra do Catalisador em si** (vale para toda análise, não só para cantrip):

| Item | Regra |
| :--- | :--- |
| O que ele faz | Converte uma peça de armadura elegível na peça de tier do spec. **Mantém** os stats base, os efeitos especiais e o **track/nível de aprimoramento** da peça de entrada. |
| O que ele **não** faz | Não sobe de track. Peça Heroica 6/6 → tier Heroico 6/6 (**321**). Peça Mítica 6/6 → tier Mítico 6/6 (**334**). |
| Slots que têm tier | **Head, Shoulder, Chest, Hands, Legs** (5 slots). |
| Slots que **não** têm tier | Cloak, Wrist, Waist, Feet, Neck, Ring, Trinket, Weapon, OffHand. |
| Consequência | **Todo** drop em um dos 5 slots de tier é um drop de tier em potencial, mesmo com secundários ruins. Nesses slots, "não é BiS" não significa "não presta": significa "vale uma carga de Catalisador". |
| Direção inversa | Nos slots **sem** tier, o Catalisador não ajuda: ali o que importa é o drop em si. É por isso que BiS de Cloak/Wrist/Waist/Feet/Trinket/Arma/Ring/Neck sobe de prioridade quando o tier já está fechado. |

- **Como isso entra na decisão de Voidcore:** ver R9. A conclusão prática é que um boss com secundários medianos em um slot de tier Mítico pode valer mais Voidcore do que um boss com um BiS isolado de slot sem tier, quando ainda faltam 2+ peças para o 4pc.

---

# PARTE 4 — MATRIZ DE CRUZAMENTO

| Regra | Arquivo consultado | Chave lida | Se ausente |
|---|---|---|---|
| R1 | [`demonology_warlock.json`](demonology_warlock.json:178) / [`shadow_priest.json`](shadow_priest.json:1) / [`balance_druid.json`](balance_druid.json:244) | `gear.bis_overall.slots` | Suprime R1 |
| R1 | [`season2_context.json`](season2_context.json:386) | `todos_itens_bis_pt_br` | Mantém R1 sem ação de aquisição |
| R2 | [`mplus_loot_database.json`](mplus_loot_database.json:96) | `pesos_de_atributo` | Suprime R2 |
| R2 | [`delve_loot_kindojan.json`](delve_loot_kindojan.json:96) | `pesos_de_atributo` | Usa o do M+ |
| R3 | fichas de spec | `gear.tier_set.id_set` e `pecas` | Suprime R3 |
| R4 | fichas de spec | `trinkets_ranking[*].tipo_efeito` | Suprime R4 |
| R5 | [`rune_ids_s2.json`](rune_ids_s2.json:1) | `runas_capturadas` | `informativo` |
| R5 | [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:484) | matriz situacional | `informativo` |
| R6 | [`talent_builds_season2.json`](talent_builds_season2.json:353) | `altar_corroido.funciona_em` | Assume inativo em raid/M+ |
| R7 | [`mplus_loot_database.json`](mplus_loot_database.json:29) | `tabela_ilvl_mplus` | Suprime a parte de chave-alvo |
| R8 | [`season2_context.json`](season2_context.json:175) | `dungeons_mythic_plus` e `raid_abismo_peconhento` | Suprime R8 |
| R9 | [`season2_context.json`](season2_context.json:748) | `extra_roll_por_spec` | Usa `extra_roll_voidcore` da ficha |
| R10 | [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:361) | partes 3, 4 e 5 | Suprime R10 |
| R11 | [`talent_builds_season2.json`](talent_builds_season2.json:1) | todos os `builds_*` | `informativo` |
| R12 | [`season2_context.json`](season2_context.json:49) | `visao_geral_temporada.catalyst` | Suprime R12 |

**Regra de degradação:** nenhuma ausência de base pode gerar exceção. A regra afetada sai do relatório e o motivo vai para `alertas_parse`.

---

# PARTE 5 — FORMATO DO RELATÓRIO

## 5.1 Estrutura

```markdown
## 1. Identificação
Personagem, spec, nível, reino, data do export, checksum.

## 2. Situação informada
raid | mplus:<chave> | delves:<tier> | outdoor

## 3. Vereditos por severidade
Tabela: severidade | slot | regra | veredito | ação

## 4. Plano de aquisição
Fila ordenada: boss/dungeon → slot → item → se cabe extra roll.

## 5. Sistemas de poder emprestado
Folio: código atual vs recomendado. Códice: aplicável ou inativo.

## 6. Consumíveis
Frasco, comida, óleo, poção, runa — com aviso de origem se não craftável.

## 7. Talentos
Arquétipo atual vs recomendado.

## 8. Alertas de parse
O que não pôde ser avaliado e por quê.
```

## 5.2 Exemplo resolvido — Pyrogalth, Demonology Warlock

Entrada: export SimC, situação `mplus:10`.

**Decodificado:**

| Campo | Valor |
|---|---|
| Spec | `demonology`, nível 90, dracthyr, US/Azralon |
| Profissões | Alquimia 100, Encantamento 100 |
| Talentos | `CoQAMrNP5kak+...` — não coincide com nenhum dos 7 loadouts salvos |
| Runas | 136824, 136815, 136817, 136819, 136822 (todas rank 1) |
| Tier | 5 de 5 peças (`271546`, `271544`, `271549`, `271547`, `271545`) |
| Arma | Cajado `251156`, encantamento `7981` |
| Off-hand | Vazio |
| Trinkets | `273649` ativo + `273796` ativo |
| Anéis | `275527` (321) e `272147` (334) |
| Marcas de ilvl | 17 entradas; índice 14 em `259` contra teto `305` |

**Vereditos:**

| Sev. | Slot | Regra | Veredito |
|---|---|---|---|
| alto | head | R1 | Tier regular `271546`; BiS é o cantrip `271874`. Como o tier já está em 5/5, a troca não custa 4pc |
| alto | trinket1/2 | R4 | `273649` e `273796` são ambos on-use; dividem recarga. O par BiS é passivo + passivo |
| alto | main_hand | R1 | Cajado `251156`; BiS é 1H `271092` + off-hand `245769`. Trocar libera o slot de off-hand hoje vazio |
| medio | back | R2 | Craft com `32/40` = Crítico + Versatilidade; a prioridade M+ é Aceleração e Crítico. Recraftar para Aceleração + Maestria |
| medio | off_hand | R7 | Marca do índice 14 está em `305` contra `259` atual — há ganho por Brasão antes de depender de drop |
| medio | — | R9 | Confirme que o Núcleo Vazio Nebuloso está indo em Ula'tek e Kith'ix, não em bosses de slot já resolvido |
| informativo | — | R5 | Runas capturadas mas não verificadas; impossível comparar com o código Cxx recomendado |
| informativo | — | R11 | Build ativa não é nenhuma das salvas. Comparação por arquétipo indisponível até o parser de talentos existir |

**O que este relatório deliberadamente NÃO diz:** quanto de DPS cada troca vale, se o item X é melhor que Y por margem numérica, ou qual seria o resultado no patchwerk. Isso é trabalho de simulador.

---

# PARTE 6 — ESTRATÉGIA DE VALIDAÇÃO

## 6.1 Golden file principal

O export completo do Pyrogalth vira `tests/fixtures/simc_pyrogalth_demo.txt`. O teste compara o `CharacterState` produzido contra `tests/fixtures/simc_pyrogalth_demo.expected.json` versionado.

Cobertura mínima do golden:

- 15 slots preenchidos, incluindo `main_hand` de duas mãos e ausência de `off_hand`;
- item craftado com `crafted_stats`;
- item com `redirected_base_stats`;
- `content_tuning` presente em 4 slots;
- 7 loadouts salvos;
- `omnium_talents` com 5 entradas;
- 17 marcas de ilvl.

## 6.2 Checagens de consistência interna

Estas validações rodam sobre qualquer export e não precisam de base externa:

| Checagem | Regra | Por que |
|---|---|---|
| Monotonicidade das marcas | `ilvl_atual ≤ ilvl_maximo` em 100% das entradas | Formato mal interpretado inverteria as colunas |
| Contagem de slots | nº de slots preenchidos + nº de marcas com valor órfão = 17 | Detecta índice deslocado |
| Ilvl do comentário | ilvl entre 200 e 400 | Detecta captura de campo errado |
| Tier | contagem de `eh_tier` ≤ 5 | Série `1369x` mal classificada inflaria a contagem |
| Runas | exatamente 5 ou zero | Árvore incompleta |
| Craft | `crafted_stats` só em itens com `crafting_quality` | Evita falso positivo de stats |
| Checksum | formato hexadecimal de 8 caracteres | Confirma que a linha não foi truncada na cópia |

## 6.3 Casos de borda obrigatórios

1. Export com equipamento vazio (personagem novo).
2. Export sem `omnium_talents`.
3. Export com `off_hand` preenchida e `main_hand` de uma mão.
4. Export de outra classe (Shadow Priest e Balance Druid) para validar que nada está preso ao Warlock.
5. String AMR colada por engano → deve retornar `formato_amr_rejeitado`, nunca exceção.
6. Texto truncado no meio do bloco `Additional Character Info`.
7. Export com `# loot_spec=` ausente.

## 6.4 Critério de aceite

O módulo é considerado pronto quando:

- o golden file passa sem diff;
- as 7 checagens de consistência rodam em todos os fixtures;
- todas as regras degradam de forma controlada quando a base correspondente é removida do workspace;
- nenhuma regra emite veredito sem preencher `evidencia` e `fontes`.

---

# PARTE 7 — LIMITAÇÕES E PENDÊNCIAS

## 7.1 Não-objetivos reiterados

- Sem simulação de dano.
- Sem comparação numérica entre dois itens.
- Sem parser AMR.
- Sem acesso à API da Blizzard.

## 7.2 Pendências bloqueantes

| Pendência | Bloqueia | Como resolver |
|---|---|---|
| Receber o campo `runas_atuais` do usuário | R5 completa | `omnium_talents` só traz os nós desbloqueados; sem a escolha declarada, R5 fica informativa |
| Fechar o mapa de índices de `slot_high_watermarks` | R7 completa | Coletar 3 exports de personagens com composições distintas |
| Classificar as séries de `bonus_id` | R3 e R12 com precisão | Coletar exports de itens do mesmo slot em tracks diferentes |
| Implementar leitura de import string de talentos | R11 por arquétipo | Definir biblioteca de decodificação de talent string |

## 7.3 Pendências secundárias

- ~~Padronizar a nomenclatura das runas~~ **RESOLVIDO**: a nomenclatura oficial está em [`rune_ids_s2.md`](rune_ids_s2.md:1), com o de-para dos nomes antigos na seção de correções.
- ~~Corrigir a divergência de bônus 4pc~~ **RESOLVIDO em 2026-11-05**: `demonology_warlock.json` e `season2_context.json` estão ambos em **350%/315%** (o valor 250%/225% não existe mais em nenhum arquivo).
- ~~Adicionar `import_e_interpretacao_s2.md` e `rune_ids_s2.json` ao inventário~~ **RESOLVIDO**: os dois já constam na tabela de dados de [`pendencias.md`](pendencias.md:1).

## 7.4 Risco residual

Os três primeiros itens da seção 7.2 dependem de dados externos ao workspace. Enquanto não forem resolvidos, o módulo entrega valor em R1, R2, R3, R4, R6, R8, R9 e R10 — oito das doze regras — e degrada R5, R7, R11 e R12 para nível informativo. Isso é aceitável como primeiro incremento e está refletido na ordem do todo list.
