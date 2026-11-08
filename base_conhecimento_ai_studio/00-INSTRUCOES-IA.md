# INSTRUÇÕES MESTRAS — como analisar este projeto e montar builds

> **Este é o primeiro arquivo a ser lido.** Qualquer IA que abrir esta pasta deve começar por aqui. Ele não contém dados de jogo: contém o **método** para usar os dados dos outros arquivos sem inventar, sem contradizer e sem repetir erros já corrigidos.
>
> **Projeto:** calculadora de build para World of Warcraft: Midnight — Patch 12.1.5 (*A Maldição de Ula'tek*), Temporada 2.
> **Specs cobertas:** Bruxo Demonologia, Bruxo Suplício, Bruxo Destruição (fichas completas em 06/11/2026), Sacerdote das Sombras, Druida do Equilíbrio.
> **Situações cobertas:** Masmorras Mítico+ (M+), Raide e Imersões (*Delves*).
> **Idioma:** português do Brasil. Nome de item, encantamento, gema e runa **sempre** com o nome PT-BR oficial do tooltip e o nome em inglês entre parênteses ou em *itálico*.

---

# PARTE 0 — O contrato

## 0.1 O que esta IA deve fazer

1. Ler os dados do projeto e **responder com uma build específica e justificada**, não com uma lista de possibilidades.
2. **Considerar sempre as três situações** (M+, raide e imersão) e dizer em qual delas a build brilha e em qual ela falha.
3. Quando o pedido não especificar o objetivo, **assumir a matriz de perfis** da §2.3 e entregar a recomendação para dano, para equilíbrio e para sobrevivência.
4. Explicitar o **custo de oportunidade** de cada escolha: o que se perde ao ganhar aquilo.
5. Declarar **o que não sabe** e o que precisaria de simulação para fechar.
6. **Quando o usuário colar um export do SimC e um item**, não responder "vale/não vale": aplicar o **protocolo de substituição** da §3.2, com portões G0–G8 e um dos cinco vereditos.
7. Se o export não tiver o necessário para julgar (runas escolhidas, ID do candidato, checksum), **pedir o campo específico** em vez de adivinhar.

## 0.2 O que esta IA nunca pode fazer

| Proibição | Motivo | O que fazer no lugar |
| :--- | :--- | :--- |
| Inventar número de atributo, dano ou proc | O projeto já foi corrigido por valores 1,9× a 3,9× errados em 93 registros | Usar só o valor catalogado e citar o arquivo |
| Prometer DPS ou dizer "isso dá +X%" | O projeto **não** simula. Simulação é Raidbots/SimC | Dizer o que muda e mandar simular |
| Traduzir nome de item por conta própria | Já houve 15 nomes de consumível e 1 embelezamento inventados | Copiar o nome do tooltip PT-BR |
| Listar item que não está no catálogo | O catálogo é auditado contra o Wowhead | Apontar a lacuna como pendência |
| Desenhar árvore de talentos em imagem | O ambiente bloqueia ícones externos | Entregar código de exportação + talentos em texto + link do calculador |
| Contar "2 peças craftadas" como limite | O limite é de **efeitos de embelezamento**, não de peças | Ver §1.4 |
| Responder em inglês porque a fonte estava em inglês | A saída é **sempre** em PT-BR; o inglês é só identificador | Ver §1.5 |
| Comparar item forjado com item comum pelo número do nível | Um forjado de 341 é um item de 334 com +7 | Normalizar pelo nível de referência |

---

# PARTE 1 — Mapa do conhecimento (leia nesta ordem)

## 1.1 Ordem de leitura obrigatória

| # | Arquivo | O que ele resolve | Quando consultar |
| :-: | :--- | :--- | :--- |
| 1 | **este arquivo** | método, hierarquia de decisão, formato de resposta | sempre |
| 2 | [`season2_context.md`](season2_context.md:1) | temporada, faixas de nível, forja, tier, afixos, Catalyst, craft | sempre |
| 3 | ficha do spec: [`demonology_warlock.md`](demonology_warlock.md:1), [`affliction_warlock.md`](affliction_warlock.md:1), [`shadow_priest.md`](shadow_priest.md:1), [`balance_druid.md`](balance_druid.md:1) | BiS por situação, tier, embelezamentos, prioridade de atributo. A ficha do Suplício traz também Folio Ômnico e Códice Corrosivo por cenário | sempre |
| 4 | [`mplus_loot_database.md`](mplus_loot_database.md:1) | banco de loot de M+, pesos de atributo por situação | M+ e comparação de slot |
| 5 | [`delve_loot_kindojan.md`](delve_loot_kindojan.md:1) | loot de imersão, Tier 11, conjunto Pisa-piras | imersão |
| 6 | [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:1) | frascos, comida, poção, óleo, runa, matriz do Folio | toda recomendação de consumível e runa |
| 7 | [`rune_ids_s2.md`](rune_ids_s2.md:1) / [`rune_ids_s2.json`](rune_ids_s2.json:1) | 13 runas, 72 combinações, códigos C01–C72 | runas |
| 8 | [`talent_builds_season2.md`](talent_builds_season2.md:1) | builds por spec e situação, códigos de exportação; inclui a avaliação de **Suplício e Destruição** contra Demonologia (M+, raide, Delve, Caçada e Ilha Enrolada) | talentos |
| 9 | [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1) + [`craft_receitas_s2.json`](craft_receitas_s2.json:1) + [`craft_armas_s2.json`](craft_armas_s2.json:1) | craft: 331, 2 embelezamentos, missivas, 29 armas | qualquer peça craftada |
| 10 | [`encantamentos_e_gemas_s2.md`](encantamentos_e_gemas_s2.md:1) | 38 encantamentos (76 IDs), 72 gemas, Magilinha e Kit de Armadura | toda peça com encantamento/gema/perna |
| 10b | [`enchant_ids_s2.json`](enchant_ids_s2.json:1) | resolve o `enchant_id` do SimC para o encantamento do catálogo (**97 IDs**: 76 de equipamento, 8 óleos, 1 tinker, 12 de ferramenta) | **sempre** que houver `enchant_id=` num export |
| 11 | [`import_e_interpretacao_s2.md`](import_e_interpretacao_s2.md:1) | como ler um export do SimC e as 12 regras R1–R12 | quando houver personagem real para avaliar |
| 12 | [`stats_oficiais_itens.md`](stats_oficiais_itens.md:1) | atributos oficiais no nível máximo de cada item | conferência numérica |
| 12b | [`monitor_upgrades_s2.md`](monitor_upgrades_s2.md:1) | **armas, pescoços, mão secundária e berloques** separados nos dois tetos: **341** (Mito 6/6 + forja) e **328** (Herói 6/6 + forja) | quando a pergunta é "esse item sobe até quanto?" ou "vale trocar arma/pescoço/berloque?" |
| 13 | [`pendencias.md`](pendencias.md:1) e [`auditoria_ptbr.md`](auditoria_ptbr.md:1) | o que está em aberto e o que já foi corrigido | antes de afirmar algo "estranho" |
| 14 | [`PROTOCOLO_FIRECRAWL_WOWHEAD.md`](PROTOCOLO_FIRECRAWL_WOWHEAD.md:1) | protocolo mestre de extração com Firecrawl, captura de ícones na CDN Zamimg e enriquecimento | antes de qualquer operação de scraping ou busca no Wowhead |

## 1.2 Regra de precedência entre arquivos

Quando dois arquivos divergirem, vale a seguinte ordem — do mais forte para o mais fraco:

1. **Tooltip oficial** gravado em JSON de auditoria (`stats_oficiais_itens.json`, `craft_sistemas_s2.json`, `craft_armas_s2.json`, `encantamentos_e_gemas_s2.json`).
2. **Ficha de spec** (`.md` e `.json`).
3. **`season2_context`** (regras da temporada).
4. **Guias de terceiros** (Icy Veins, Method, LevelUpper, Murlok) — só quando o tooltip não responde.
5. **Nunca**: memória do modelo, "acho que na temporada passada era assim", vídeo sem número.

Se a divergência for real, **não escolha uma em silêncio**: registre nas pendências e diga qual fonte venceu e por quê.

## 1.3 Vocabulário de nível (o erro mais comum do projeto)

| Nível | Rótulo | Origem | Regra de leitura |
| :-: | :--- | :--- | :--- |
| **344** | Amaldiçoado com Peçonha (*Venom-Cursed*) | cantrip de raide (elmo, pernas, arma, pescoço) + cinto/botas | +10 sobre o tier mítico |
| **341** | Ascendente Forjado com Peçonha: Mito | pescoço, berloque, arma, mão secundária | é um item **334** com +7 de forja |
| **334** | Mítico 6/6 | tier de raide | referência de "mítico" |
| **331** | **craft** com Centelha + 80 cristas míticas | craft | teto do craft da temporada |
| **328** | Forjado com Peçonha: Herói | pescoço, berloque, arma | é um item **321** com +7 |
| **321** | Herói 6/6 | tier de raide | — |
| **318 / 305 / 292** | craft com cristas heroicas / só Centelha | craft | ver [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1) |
| **308** | Campeão 6/6 | — | piso de conteúdo |
| **246** | base craftada sem melhoria | craft | é o **piso**, não o valor final |

**Consequência obrigatória:** antes de comparar dois itens, **normalize pelo nível de referência**. Um berloque forjado de 341 não é "7 níveis melhor" que um 341 comum — ele é um 334 com forja.

## 1.4 Os cinco tetos que limitam qualquer build

| Teto | Regra | Fonte |
| :--- | :--- | :--- |
| **Craft** | máximo **331** | [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1) |
| **Embelezamento** | **2 efeitos** ativos (`Único-equipado: Embelezado (2)`). Não há limite de **peças** craftadas | idem, §0 |
| **Gema prismática** | **1** diamante de Eversong (`Unique-Equipped: Thalassian Diamond (1)`) | [`encantamentos_e_gemas_s2.md`](encantamentos_e_gemas_s2.md:1) |
| **Runas** | 5 linhas, 13 runas, **72 combinações** (linha 4 tem 4 opções) | [`rune_ids_s2.md`](rune_ids_s2.md:1) |
| **Berloques** | 2 slots; **não** repetir arquétipo on-use (regra R4) | [`import_e_interpretacao_s2.md`](import_e_interpretacao_s2.md:1) |

## 1.5 Regra bilíngue — entrada em qualquer idioma, saída em PT-BR

O projeto guarda **nome em inglês e nome em PT-BR de propósito**: o usuário pode trazer print, link, vídeo ou export em inglês. As duas línguas existem para **identificar o item**, não para mudar o idioma da resposta.

| Regra | Detalhe |
| :--- | :--- |
| **Entrada** | pode vir em inglês, português, print de tela, link do Wowhead, export do SimC ou nome solto |
| **Processo** | nome em inglês → **ID** → **nome oficial PT-BR** do tooltip. Nessa ordem, sempre |
| **Saída** | **sempre em PT-BR**. O nome em inglês aparece uma vez, em *itálico* ou entre parênteses, como identificador |
| **Nunca** | traduzir de cabeça. Se não houver nome PT-BR no catálogo, escreva o inglês e marque "PT a confirmar" |
| **Ferramentas** | nenhum script do projeto traduz: todos **consultam** o nome oficial (tooltip `locale=8` ou coluna `Name_lang` do DB2) e gravam de onde veio no campo `fonte_nome` |

**Como resolver nome inglês → PT-BR:**

1. Procurar o nome no JSON correspondente (`craft_sistemas_s2.json`, `craft_armas_s2.json`, `encantamentos_e_gemas_s2.json`, `stats_oficiais_itens.json`, fichas de spec).
2. Se não estiver no catálogo, pegar o **ID** no Wowhead (o link do item traz o ID) e rodar `node tools/consultar_ids.js <id>` — o tooltip vem em PT-BR.
3. Se só houver **print**, comparar o nome em inglês com o catálogo; se não bater, dizer qual nome foi assumido e qual ID foi usado.
4. Nunca inventar tradução. Nome sem confirmação é nome em inglês + marcação de pendência.

> **Formato final de citação:** **Braceletes do Mártir** *Martyr's Bindings* `239648` — primeiro o PT-BR, o inglês em itálico, o ID por último.

## 1.6 Slots que não aceitam encantamento

Na Temporada 2 **não existe** encantamento para **pulsos, mãos e capa**. Existe para **cabeça, ombros, peitoral, pés, os dois anéis e arma**.

**Pernas** não recebem encantamento: recebem **Magilinha** (*Spellthread*, Alfaiataria) ou **Kit de Armadura** (*Armor Kit*, Couraria). Tratar pernas como "slot vazio" é erro de cálculo.

### 1.6.1 Camadas do mesmo slot — arma, elmo e pernas

Dois aprimoramentos podem disputar o mesmo slot sem serem a mesma coisa. Confundir isso gera conselho errado.

| Slot | Camada A | Camada B | Regra |
| :--- | :--- | :--- | :--- |
| **Arma** | encantamento **permanente** (`7980`–`8689`, ex. Precisão de Jan'alai, Maestria Arcana) | **óleo temporário de 120 min** (`8051`–`8056`, `8612`/`8613`) | **coexistem**: 1 de cada. O óleo aparece no export como `enchant_id` do `main_hand` |
| **Elmo** | encantamento de elmo (Evasão, Velocidade, Sorver) | **tinker `R0CKY` (`8702`)** — queda lenta por 2 min | **disputam a mesma linha**: escolher R0CKY remove o encantamento de elmo |
| **Pernas** | **Magilinha** (Intelecto/mana) | **Kit de Armadura** (Agilidade/Força, defesa) | **mutuamente exclusivos**; nenhum é encantamento |

> Consequência prática: ao ler um export, se o `enchant_id` da arma estiver em `8051`–`8613`, **o encantamento permanente não foi registrado** naquele perfil — e não se deve concluir que a arma "não tem encantamento".

## 1.7 Peça craftada: o que é do item e o que é escolha do jogador

O erro mais fácil de cometer neste projeto é tratar uma peça craftada como se ela tivesse atributos e efeito próprios. **Não tem.**

| Elemento | É do item? | Como aparece |
| :--- | :-: | :--- |
| Atributo primário, Vigor, armadura | ✅ fixo | tooltip |
| **Os dois secundários** | ❌ **escolha** | tooltip mostra *“Atributo Aleatório 1 / 2”*; quem define é a **Missiva** na ordem |
| **O embelezamento** | ❌ **escolha** | reagente opcional; o item sai sem efeito se você não aplicar |
| Nível 246 | ✅ piso | sobe com qualidade e cristas até **331** |

**Regras de escrita:**

1. Em ficha de item craftado, liste **apenas os atributos fixos**. Secundários vão como **recomendação**, nunca como dado do item.
2. Ao responder, diga **quais combinações existem** (as 6 missivas para secundários; a lista de embelezamentos válidos para o slot) e **qual você recomenda**, com o motivo.
3. **A combinação real do jogador** (o que veio no print ou no `crafted_stats` do export) é dado **do personagem**, não do item. Registre assim: "sua Lanterna está com Crítico + Aceleração e Pedra Ritual do Caçador".
4. Se o item do jogador contradiz o tooltip (ex.: embelezamento que o tooltip diz ser de outro slot), **o item equipado vence para aquele personagem** e o conflito vai para as pendências. Não generalize a exceção para o catálogo.

> **Frase proibida:** "a Lanterna dá Aceleração e Maestria". **Frase correta:** "a Lanterna dá Int 127 e Vig 692; os secundários vêm da missiva — recomendo Aceleração e Maestria".

---

# PARTE 2 — Motor de decisão

## 2.1 Os cinco eixos que toda escolha move

Toda peça, gema, runa ou consumível move um ou mais destes eixos. **Sempre diga qual eixo a escolha move e qual ela sacrifica.**

| Eixo | Pergunta que responde | Como é medida |
| :--- | :--- | :--- |
| **Dano** | aumenta o dano sustentado ou o pico? | prioridade de atributo da spec + efeitos com número catalogado |
| **Sobrevivência** | reduz a chance de morrer? | Vigor, armadura, Versatilidade (mitigação), escudos/absorção, autocura, Evasão/Sorver |
| **Consistência** | o desempenho depende de sorte ou de execução perfeita? | procs aleatórios, efeitos condicionais (alvo com pouca vida, acima de 80% de vida, mundo aberto) |
| **Execução** | exige mais teclas, posicionamento ou timing? | efeitos on-use, cantrips com ativação, runas dependentes de tomar dano |
| **Aquisição** | quanto custa obter e manter? | Centelhas, cristas, Moxie, drops de raide, extra roll, leilão |

## 2.2 Hierarquia de decisão (ordem de sobreposição)

Quando duas otimizações conflitam, a de cima vence:

1. **Build de talentos coerente com o cenário** — nenhuma peça compensa talento errado.
2. **4 peças de tier** — o bônus de 4 é maior que a soma de qualquer troca de stats isolada.
3. **Nível de item normalizado** — 3 níveis acima costumam vencer 1 secundário "perfeito"; acima de 10 níveis, sempre.
4. **Efeito cantrip / arquétipo de berloque** — efeito único vale mais que stats; arquétipo on-use não se acumula.
5. **Os 2 embelezamentos** — são o maior ganho "fora de stats" do craft.
6. **Runas do Folio** — 72 combinações, todas ativas em qualquer conteúdo; a linha 4 e a linha 5 mudam o perfil.
7. **Encantamentos, gemas e Magilinha** — ganho fixo e barato; nunca é o gargalo.
8. **Consumíveis** — frasco, comida, poção, óleo, runa de aprimoramento; entra por último porque é o mais fácil de trocar.

## 2.3 Perfis de objetivo

O usuário pode pedir três coisas diferentes. **Quando não pedir nada, entregue os três.**

### Perfil A — Dano máximo

| Dimensão | Diretriz |
| :--- | :--- |
| Atributo | empilhar o topo da prioridade da spec naquela situação (ex.: Demo em M+: Aceleração > Crítico > Maestria > Versatilidade) |
| Embelezamento | efeito de dano com maior uptime: **Forro de Arcanotrama** duplo, **Pedra Ritual do Caçador**, **Signo de Negraluna: Caçada** |
| Runas | linha 4 ofensiva (`4A` Crítico / `4B` Aceleração / `4C` Maestria) + capstone `5A` (Sobrecarga) ou `5C` (Ecos) |
| Gema | 1 diamante de primário + gemas de cor do **maior** secundário |
| Custo | ignora mitigações; assume grupo com curador e execução limpa |
| Risco | morrer zera o dano: em M+ alto esse perfil **perde** para o perfil B |

### Perfil B — Equilibrado (padrão recomendado)

| Dimensão | Diretriz |
| :--- | :--- |
| Atributo | mantém a prioridade, mas aceita o 2º secundário quando o ganho do 1º é marginal |
| Embelezamento | **1 peça ofensiva + 1 peça defensiva/utilitária** (ex.: Arcanotrama + Signo de Negraluna: Sangue) |
| Runas | linha 4 `4D` (Versatilidade) quando o conteúdo tem dano de atrito; `2C` (Reflexos de Lince) só se você **toma** dano |
| Gema | diamante **Estoico** (armadura) ou **Telúrico** (mana) quando a morte é o gargalo |
| Custo | peça craftada com missiva certa e um encantamento defensivo (Evasão no elmo, Sorver nos ombros) |

### Perfil C — Sobrevivência pura

| Dimensão | Diretriz |
| :--- | :--- |
| Atributo | Versatilidade sobe de posição; Vigor e armadura passam a contar |
| Embelezamento | dois efeitos defensivos: **Escudo/absorção** e **cura/roubo de vida** |
| Runas | `4D` + `5B` (Energia Residual) com `2B` (Autorrecomposição) no lugar de `2C` |
| Gema | diamante **Estoico**; gemas de Versatilidade |
| Pernas | **Kit de Armadura** defensivo em vez de Magilinha ofensiva |
| Uso típico | imersão Tier 11 solo, mundo aberto de alto risco, chave onde o grupo já tem dano sobrando |

## 2.4 Matriz de cenários

### M+ (Masmorras Mítico+)

| Faixa | Afixo ativo | O que muda na build |
| :-: | :--- | :--- |
| +2 | Orientação de Lindormi | nada relevante; build de dano |
| +5 | Barganha de Xal'atath (Ascendente · Ligado ao Vazio · Devorar · Pulsar) | afixo rotativo: dano de atrito pede **Versatilidade** e cura passiva |
| +7 | Tirânico **ou** Fortificado (alternam por semana) | Tirânico = chefes (dano sustentado em alvo único); Fortificado = trash (dano em área e sobrevida) |
| +10 | Tirânico **e** Fortificado juntos | morte é o gargalo: perfil **B** obrigatório, `4D`, Evasão/Sorver |
| +12 | Astúcia de Xal'atath (substitui o do +5) | pico de execução; build de dano com alta sobrevida |

Prioridades de M+: **1)** sobreviver ao pacote inicial; **2)** dano de prioridade em alvo perigoso; **3)** dano em área; **4)** utilidade (interrupção, controle). Efeitos que dependem de **alvo com pouca vida** (ex.: **Presa Adornada**) rendem menos em trash que morre rápido e mais em chefe.

### Raide

- Alvo único, lutas longas: valoriza **dano sustentado**, uptime alto e efeitos que **acumulam** (ex.: linha 4 do Folio sobreposta, **Ecos** `5C` repetindo 50% do dano das runas após 10 s).
- **4 peças de tier** é a prioridade absoluta; o caminho para fechar é o **Catalyst**, que **preserva atributos e efeito cantrip** do item original.
- **Extra roll** só onde a peça muda a build (ver regra R9 e a prioridade de Núcleo Vazio Nebuloso).
- Efeitos **on-use** não se acumulam: dois berloques on-use dividem recarga (regra R4).
- Cantrips de raide (344) são fortes mas **não** são upgrade de build por si: primeiro garanta 4pc.

### Imersão (*Delve*)

- Conteúdo **solo**, muitas vezes **sem curador**: sobrevivência deixa de ser opcional.
- Tier 11 é o teste real: priorize **autocura**, **absorção**, **Evasão/Sorver** e **Versatilidade**.
- Conjunto **Pisa-piras** do Kindo'jan existe para imersão — vale mais que um item de M+ em alguns slots, pelo efeito, não pelo nível.
- Efeitos que exigem **mundo aberto** (ex.: **Pedra Ritual do Caçador** com bônus de Caça às Presas) **não** funcionam dentro da imersão instanciada. Leia sempre a condição de ativação.
- Runas: use a matriz da §2.7.3. Em Tier 11 a indicação documentada é **`C24`** (`1A-2B-3A-4D-5C`); em Tier 8–10 é **`C26`** (`1A-2C-3A-4A-5B`). Atenção: `2C` dá **velocidade de movimento**, não mitigação — quem defende é `2A` (absorção) e `2B` (autocura).

## 2.5 Sinergias e conflitos catalogados

| Combinação | Efeito | Regra |
| :--- | :--- | :--- |
| **2× Forro de Arcanotrama** em peças diferentes | dois procs independentes de atributo primário para você **e um aliado** | ambos contam no limite de 2 |
| **Loa Worshiper's Band** + **Bandoleira de Gemas Estabilizadora** | amplia embelezamentos de Joalheria | ocupa **os dois** slots de embelezamento (um é embutido) |
| **Berloque on-use + berloque on-use** | dividem recarga | **proibido** pela R4 |
| **Tier 4pc + cantrip no mesmo slot** | Catalyst preserva cantrip | catalisar o cantrip é o caminho ótimo (R12) |
| **Runa `4A/4B/4C` (ofensiva)** | +52,7 de rating e **sobrepõe** a cada proc da runa central | melhor em luta longa de alvo único |
| **Runa `4D` (Versatilidade)** | única com componente defensiva | escolha padrão em +10 ou superior |
| **Runa `5B` sem entender a linha 3** | multiplica a Runa da Perenidade, não o burst | erro clássico de leitura |
| **Óleo da Aurora** | só proca com **feitiço de cura** | **inútil** nas três specs de dano |
| **Embelezamento em mão secundária** | Pedra Ritual do Caçador é só de **arma de Ferraria** | em mão secundária use **Signo de Negraluna** |

## 2.6 Três exemplos de raciocínio (use como molde)

Estes exemplos mostram **como combinar**, não são BiS definitivo. Todo número abaixo está catalogado nos arquivos do projeto.

### Exemplo 1 — Dano em M+, bruxo Demonologia

| Camada | Escolha | Eixo movido |
| :--- | :--- | :--- |
| Talentos | build de M+ da ficha do Demo | base do dano |
| Tier | 4 peças dos Grilhões, fechando por Catalyst nas peças míticas | dano (4p = 350%/315%) |
| Craft | 1 peça de armadura (pulsos) + 1 peça craftada extra **sem** embelezamento | atributo escolhido por missiva |
| Embelezamento | 2× **Forro de Arcanotrama** | dano (primário para você e um aliado) |
| Runas | linha 4 **`4B` Aceleração** + capstone **`5C` Ecos** → código de M+ com `5C` | dano sustentado e replicação |
| Encantamentos | **Encantamento da Marca do Magíster - Torso** (+40 Int), **Encantamento da Maestria Arcana - Arma** (+124 Maestria/15 s), **Encantamento da Aceleração Talassiana - Anel** (+24) nos dois anéis | dano |
| Pernas | **Magilinha de Arcanotrama** (+41 Int e +4% de mana) | dano |
| Gemas | 1× **Diamante do Canto Eterno Poderoso** + gemas de Aceleração/maior secundário | dano |
| Consumíveis | frasco de Intelecto, comida de +65 do maior secundário, poção de combate, óleo de arma | dano |

**Custo:** nos +10, a build perde para a versão equilibrada se você morrer no pacote — troque **um** embelezamento por **Signo de Negraluna: Sangue** e a linha 4 para `4D`.

### Exemplo 2 — Equilibrado em raide, Sacerdote das Sombras

| Camada | Escolha | Eixo movido |
| :--- | :--- | :--- |
| Tier | 4 peças primeiro, sem exceção | dano |
| Embelezamento | 1 peça ofensiva (**Arcanotrama**) + 1 peça de sobrevida/absorção | dano + sobrevivência |
| Runas | linha 4 ofensiva + capstone **`5A` Sobrecarga** ou **`5C` Ecos** | dano em luta longa |
| Encantamentos | elmo com **Runa da Evasão Potencializada** (+37 Evasão) ou ombros com **Recomposição de Luaprata** (+166 Sorver) | sobrevivência |
| Gema | diamante **Estoico** (+23 primário e +13 Armadura) | sobrevivência marginal sem perder primário |
| Risco | berloque on-use + on-use = recarga dividida (R4) | consistência |

### Exemplo 3 — Sobrevivência pura em imersão Tier 11, Druida do Equilíbrio

| Camada | Escolha | Eixo movido |
| :--- | :--- | :--- |
| Runas | `2B` Autorrecomposição + `4D` Versatilidade + `5B` Energia Residual | sobrevivência |
| Embelezamento | 2 efeitos defensivos (absorção + cura/roubo de vida) | sobrevivência |
| Pernas | **Kit de Armadura** defensivo em vez de Magilinha | sobrevivência |
| Encantamentos | Evasão no elmo, Sorver nos ombros, Vigor nas botas | sobrevivência |
| Gemas | diamante **Estoico** + gemas de Versatilidade | sobrevivência |
| Consumíveis | poção de vida + comida defensiva | sobrevivência |
| Sacrifício declarado | perde dano; aceitável porque imersão não tem limite de tempo | — |

## 2.7 Runas do Folio Ômnico — como decidir (e por que não se troca "por segurança")

O Folio tem **5 linhas obrigatórias**, 13 runas e **72 combinações** (`C01`–`C72`). Cada linha muda **um mecanismo diferente**; trocar duas linhas ao mesmo tempo é quase sempre resposta sem diagnóstico.

### 2.7.1 O que cada linha realmente faz

| Linha | Opções | Mecanismo (texto do catálogo) | Quando importa |
| :-: | :--- | :--- | :--- |
| **1** | `1A` Fogo Incontido · `1B` Orbes do Caos | 1A: pilar de fogo, dano **ou cura** a cada proc. 1B: um orbe a cada 10 s, até 5, gastos ao atacar | 1B tem ramp de 40–50 s; 1A entrega desde o primeiro proc |
| **2** | `2A` Concha Maculada · `2B` Autorrecomposição · `2C` Reflexos de Lince | 2A: escudo ao levar golpe **>10% da vida**. 2B: **cura** quando abaixo de 75% de vida. 2C: **+77,5 de velocidade de movimento** por 10 s ao ser atingido | 2A e 2B **defendem**; 2C **reposiciona**. `2C` **não é mitigação** |
| **3** | `3A` Perenidade (única) | Efeito periódico de dano/cura por 8 s | é a base do capstone `5B` |
| **4** | `4A` Crítico · `4B` Aceleração · `4C` Maestria · `4D` Versatilidade | +52,7 do atributo por 10 s a cada ativação da Runa Central, **sobrepondo** | escolha por **prioridade de atributo**, não por gosto |
| **5** | `5A` Sobrecarga · `5B` Energia Residual · `5C` Ecos | 5A: +100% na Runa Central. 5B: +100% na Perenidade. 5C: eco de 50% do dano/cura das runas após 10 s | 5B exige luta longa; 5C premia luta longa de alvo único |

> ⚠️ **Correção de leitura recorrente:** dizer que “`2C` brilha em imersão porque você toma dano” usa o dado certo para a conclusão errada. `2C` concede **velocidade de movimento**; não reduz dano recebido.

### 2.7.2 Ordem de precedência para escolher a runa

1. **Matriz situacional** de [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:1) — tabela das linhas **484–489**, que dá o código por cenário.
2. **Catálogo das 72 combinações** (seção 1.3 do mesmo arquivo) — descrição tática de cada `Cxx`.
3. **Arbitragem externa** em [`rune_ids_s2.md`](rune_ids_s2.md:1): Icy Veins (1A · 2A ou 2B · 3A · 4A · 5A ou 5B) e Method (1A · 2C · 3A · 4A · 5A = `C25`).
4. **Prosa genérica** — só quando as três anteriores não decidem.

**Empate entre documentos do projeto:** vence o **mais específico ao cenário**; se o empate persistir, **declare o conflito** e entregue a principal + a condição de troca. Nunca escolher em silêncio.

### 2.7.3 Padrão por cenário (o que o projeto já decidiu)

| Cenário | Código | Composição | Origem |
| :--- | :-: | :--- | :--- |
| Raide de alvo único | `C13` / `C14` | `1A-2B-3A-4A-5A` / `1A-2B-3A-4A-5B` | matriz |
| Raide ST (variante externa, “não arbitrada”) | `C06` | `1A-2A-3A-4B-5C` | matriz |
| M+ médias (+2 a +9) | `C29` | `1A-2C-3A-4B-5B` | matriz |
| M+ altas (+10 e acima) | linha 4 em **`4D`** | mitigação de dano recebido | guia de consumíveis §1.2 |
| Imersão Tier 8–10 | `C26` | `1A-2C-3A-4A-5B` | matriz |
| **Imersão Tier 11 (chefes)** | **`C24`** | `1A-2B-3A-4D-5C` — defesa máxima | matriz |
| Mundo aberto de alto risco | `C36` / `C72` | `1A-2C-3A-4D-5C` / `1B-2C-3A-4D-5C` | catálogo |
| Crítico > 35% e Maestria negligenciada | `4C` | `1A-2B-3A-4C-5B` = `C20` | regra de troca por atributo |

### 2.7.4 Regras de resposta para runas

1. **Uma linha por recomendação**, no máximo duas com justificativa explícita de cada.
2. Toda troca cita **arquivo + linha** da matriz ou do catálogo, e o **mecanismo** (o que a runa faz).
3. Toda troca declara **o que se perde**: trocar `4A` por `4D` perde rating ofensivo e ganha mitigação.
4. Se o objetivo não foi dito, responda **por cenário** (§2.7.3), não por preferência.
5. **Nunca** diga “deixa como está” sem dizer **para qual cenário** aquilo está bom — e qual cenário exigiria outra combinação.

### 2.7.5 Lacuna de dado na linha 4

`4D` (Guerreiro Versátil) é a **única** runa da linha 4 com `id_buff: null` em [`rune_ids_s2.json`](rune_ids_s2.json:1): só o nó (`1279613`) está confirmado, não o buff. As outras três têm nó **e** buff (`4A` 1279609/1287772, `4B` 1279610/1287774, `4C` 1279612/1287771). Ao conferir num export, `4D` deve aparecer como `1279613`; se não aparecer, a lacuna é do catálogo, não da build.

---

# PARTE 3 — Checklist de análise (execute nesta ordem)

1. **Identificar a pergunta.** É dano, equilíbrio ou sobrevivência? É M+, raide ou imersão? Sem isso, entregue os três perfis.
2. **Identificar a spec e a build ativa.** Usar [`talent_builds_season2.md`](talent_builds_season2.md:1). Talento errado invalida toda a análise de peça.
3. **Normalizar níveis.** Converter todo item para o nível de referência (§1.3). Comparar só depois disso.
4. **Checar o 4pc.** Faltando peça, a resposta começa por "como fechar o 4pc" — Catalyst, Great Vault, qual slot.
5. **Checar arquétipo de berloque.** Dois on-use = conflito. Berloque de Força em conjurador = erro (já removido do banco).
6. **Contar embelezamentos.** Liste os efeitos ativos, não as peças. Se passar de 2, diga qual efeito fica inerte.
7. **Escolher runas pelo cenário.** Use os códigos `Cxx` do Folio; a linha 4 e a linha 5 definem o perfil.
8. **Fechar encantamento/gema/perna.** Cabeça, ombros, peitoral, pés, 2 anéis, arma; 1 diamante; Magilinha ou Kit de Armadura nas pernas.
9. **Fechar consumíveis.** Frasco, comida, poção de combate, óleo de arma, runa de aprimoramento — conferidos em [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:1).
10. **Declarar incerteza.** O que depende de simulação, de drop ou de execução. Sem isso a resposta mente por omissão.

## 3.1 Perguntas de aprofundamento (use quando o pedido for vago)

- **Qual slot dói mais?** O gargalo real quase nunca é o slot mais fraco, é o slot cujo BiS tem efeito.
- **Qual efeito eu perco se trocar?** Efeito > 3 níveis de item, quase sempre.
- **Esse efeito funciona neste cenário?** Mundo aberto, alvo com pouca vida, tomar dano, grupo com curador — leia a condição.
- **Quanto custa e quando chega?** Centelha é semanal: 2 por peça de armadura/1M, 4 por arma 2M.
- **O que faço se não dropar?** Toda recomendação precisa de um plano B craftável ou de leilão.

## 3.2 Protocolo de substituição — quando o usuário traz um export do SimC e um item

Este é o fluxo mais importante na prática: o usuário cola o **export do SimulationCraft AddOn** (`/simc`) e pergunta *"vale trocar meu item X por este item Y?"*. A resposta **não** é "sim/não": é um laudo com portões.

### Passo 1 — Ler o export (o que cada campo entrega)

Formato de linha: `<slot>=,id=<item_id>,enchant_id=<id>,gem_id=<id>,bonus_id=<a>/<b>/<c>,content_tuning=<id>,crafted_stats=<a>/<b>,crafting_quality=<n>,redirected_base_stats=<id>`

| Campo | O que a IA extrai | Cuidado |
| :--- | :--- | :--- |
| Cabeçalho (`# Nome - Spec - data`) | spec, nível, raça, **profissões** | profissão define se a recomendação é "craftar" ou "comprar no leilão" |
| `talents=` | árvore ativa | string de talento **não** é decodificada pelo projeto: comparar por arquétipo, não por nó |
| `omnium_talents=` | 5 pares `rune_id:rank` | **não** contém a escolha da runa — todo personagem com o sistema exporta os mesmos 5 nós. Para avaliar runas é obrigatório pedir o campo `runas_atuais` (formato `1A-2B-3A-4A-5A`) |
| `id=` de cada slot | item equipado | é a base da comparação; sem `id` o slot é ignorado |
| `bonus_id=` | track, tier, terciário, encaixe | **nunca** inferir atributo de `bonus_id` |
| `crafted_stats=a/b` | os dois secundários escolhidos por missiva | ex.: `36/32` = Aceleração + Crítico |
| `crafting_quality=` | 1 a 5 | qualidade baixa = item abaixo do teto 331 |
| `content_tuning=` | origem/escala do item | ajuda a separar drop de M+ de drop de raide |
| `enchant_id=` | **não é o ID do pergaminho**: é a linha de `SpellItemEnchantment`, uma por qualidade | **resolva** com `node tools/mapear_enchant_ids.js <id>` antes de qualquer conclusão. Ex.: `7981` = Precisão de Jan'alai **Tier 2** |
| `gem_id=` | ID da gema (é o ID do item, igual ao catálogo) | ao trocar a peça, encantamento e gema **vão junto** — some os dois no custo |
| `### Gear from Bags` | alternativas na mochila | fonte de plano B sem farmar |
| `### Additional Character Info` | marcas de nível, moedas, extra rolls | alimenta a regra R7 (upgrade barato por crista) |
| `# Checksum` | assinatura | se faltar, o export pode estar truncado: peça de novo |

### Passo 2 — Ler o item candidato

Se o usuário trouxer o nome **em inglês** (print, link ou fala), resolver pela §1.5: nome EN → **ID** → nome oficial **PT-BR**. Se só houver print sem ID, comparar o nome em inglês com o catálogo e dizer qual ID foi assumido.

Se o usuário deu só o nome: pedir o **ID**. Com o ID em mão:

```bash
node tools/consultar_ids.js <id>          # tooltip PT-BR + inglês
```

Depois classificar o candidato em uma destas caixas, porque **cada caixa tem um portão diferente**:

| Caixa | Portões que se aplicam |
| :--- | :--- |
| Armadura comum | nível, atributos, 4pc, encantamento/gema, embelezamento |
| Armadura de tier | risco de **perder o 4pc** ao trocar |
| Armadura craftada | nível 331, missiva, qualidade, **contagem de embelezamento** |
| Arma / mão secundária | tipo (1M/2M/escudo/off-hand) muda **slots ocupados** e aceita embelezamentos diferentes |
| Berloque | arquétipo **on-use vs on-equip** (R4) e se dá primário utilizável |
| Item com cantrip | efeito único: comparar por **efeito**, não por nível (R1 e R12) |
| Item de conjunto de imersão | vale pelo efeito, não pelo nível |

### Passo 3 — Aplicar os portões, na ordem (o primeiro que falha decide)

| # | Portão | Pergunta | Reprova quando |
| :-: | :--- | :--- | :--- |
| **G0** | Compatibilidade | mesmo slot e tipo? | arma 2M no lugar de 1M + off-hand (muda dois slots), ou tipo de armadura errado |
| **G1** | Nível normalizado | o ganho de nível é real depois de normalizar forja/pescoço? | "341 vs 334" que na verdade é "334+7 vs 334" |
| **G2** | Efeito | o item equipado tem efeito que o candidato não tem? | perder cantrip, absorção, proc de conjunto |
| **G3** | Embelezamento | a troca adiciona um 3º efeito ou remove um dos 2? | passar de 2 efeitos ativos |
| **G4** | Tier | a peça trocada é de tier e você está exatamente com 4 peças? | quebra o 4pc |
| **G5** | Berloque | os dois berloques ficam on-use? | R4 |
| **G6** | Atributos | o saldo de secundários continua na prioridade da spec naquela situação? | ganha nível e perde o secundário nº 1/2 |
| **G7** | Estrutura | muda encaixe, mão secundária, requisito de profissão? | perde gema prismática, perde off-hand |
| **G8** | Custo | cristas, centelhas, encantamento, gema, missiva | custo alto para ganho marginal |

### Passo 4 — Veredito em cinco rótulos

| Rótulo | Quando usar |
| :--- | :--- |
| **Vale a troca** | passa em G0–G8 com ganho claro de nível **ou** de efeito |
| **Vale com condição** | só em M+ / só em raide / só se fechar o 4pc / só se pegar a runa `4D` |
| **Empate técnico — simular** | diferença dentro da margem de erro do olho: mandar no Raidbots/SimC |
| **Não vale** | reprova em G2, G3, G4 ou G5 |
| **Falta dado** | sem `runas_atuais`, sem ID do candidato, export truncado |

### Passo 5 — Quando o certo é procurar **outro** item

Diga isso explicitamente quando:

- o candidato resolve nível mas **destrói** o 4pc ou um cantrip;
- o gargalo real é outro slot (ex.: mão secundária vazia com cajado 2M equipado);
- o ganho existe mas o **custo em cristas** entrega mais em outro slot (R7);
- o item é de raide e o mesmo slot já está coberto por M+ (R8).

Nesse caso, a resposta termina com **o alvo correto**: nome do item, origem e por quê.

### Passo 6 — Formato do laudo de substituição

1. **Veredito em uma linha** (um dos cinco rótulos).
2. **Antes × depois**: slot, item, nível normalizado, atributos que mudam.
3. **Portões**: tabela G0–G8 com "passa / reprova / não se aplica" e a razão.
4. **Efeitos e tetos**: embelezamentos (2 de 2?), tier (4pc mantido?), berloque (arquétipo).
5. **Custo real da troca**: encantamento + gema + missiva + centelhas/cristas.
6. **O que ainda precisa de simulação** — e o comando exato para o usuário rodar.
7. **Plano B**: se o candidato não servir, qual item perseguir.

### Passo 7 — Exemplo curto de laudo

> **Veredito: vale com condição (só em raide).**
> Pulsos: `239648` (craftado, Int 47 · Vig 779, 2 de 2 embelezamentos) → candidato `271547` (tier, Int 141 · Vig 2.932 · Crí 45 · Ace 106).
> G1 passa (246 → 334). G2 **atenção**: o craftado carrega **Forro de Arcanotrama**, o tier não — você perde um dos dois efeitos e a vaga fica livre para outra peça. G4 passa: você está com 5 peças de tier, então trocar pulsos **não** quebra o 4pc. G6 passa: Aceleração + Crítico continua dentro da prioridade do Demo.
> Custo: 1 encantamento novo + perda do proc do Forro até realocar a vaga.
> Simular: comparar `271547` contra `239648` mantendo o segundo Forro em outra peça.

## 3.3 Padrão de justificativa — o antídoto contra "sabonete"

Resposta sem mecanismo é opinião. Toda recomendação deve conter **seis campos**, nesta ordem:

| Campo | O que responder | Exemplo |
| :--- | :--- | :--- |
| **1. Tese** | a decisão em uma frase | “Trocar `4A` por `4D` em imersão Tier 11” |
| **2. Evidência** | **arquivo + linha/seção** que sustenta | `consumiveis_e_sistemas_s2.md:489` — matriz marca Tier 11 como `C24` |
| **3. Mecanismo** | **por que** funciona, em termos de jogo | `4D` dá +52,7 de Versatilidade, que reduz dano recebido; `4A` dá Crítico, que só aumenta dano |
| **4. Quantificação** | número catalogado ou “não simulado” | +52,7 de rating por proc, acumulando — **não simulado** |
| **5. Confiança** | alta / média / baixa **+ motivo** | média: efeito confirmado, ganho relativo não |
| **6. Falsificador** | o que faria a resposta mudar | “com Crítico acima de 35%, o `4C` passa na frente” |

### 3.3.1 Frases proibidas

| Proibido | Por quê | Substituto |
| :--- | :--- | :--- |
| “O projeto diz que…” | apelo à autoridade, não evidência | “`arquivo:linha` diz X” |
| “É melhor / é mais forte / brilha” | adjetivo sem mecanismo | “aumenta Y porque faz Z” |
| “Consenso / meta / todo mundo usa” | popularidade não é dado | “Murlok mostra N de 50 com o item” |
| “Deixa como está” | omite para qual cenário está bom | “está bom para A; para B mude para C” |
| “Provavelmente / deve dar uns X%” | número inventado | “não simulado” |
| Trocar duas linhas “por segurança” | esconde qual mecanismo está sendo comprado | troque uma, diga o mecanismo, ofereça a outra como opcional |

### 3.3.2 Regra de conflito entre documentos

1. **Declare o conflito** com as duas citações (`arquivo:linha` de cada).
2. Aplique a **precedência da §1.2**; em empate de nível, use **especificidade ao cenário**.
3. Entregue a escolha principal **e** a condição objetiva de troca.
4. Registre a divergência em [`pendencias.md`](pendencias.md:1) — conflito silencioso é bug do projeto.

### 3.3.3 Teste de honestidade (antes de enviar)

- Cada número tem **arquivo de origem**?
- Cada troca diz **o que se perde**?
- Se o usuário perguntar “por que não a outra opção?”, a resposta já está escrita?
- Alguma frase depende de algo que eu não li? Se sim, virou hipótese declarada.

---

# PARTE 4 — Formato da resposta

Toda resposta de build deve seguir esta estrutura, nesta ordem:

1. **Veredito em uma linha.** "Para M+ +10 com Demo, a build é X; o gargalo é Y."
2. **Tabela da build** — slot, item (nome PT-BR + ID), origem, nível, atributos principais.
3. **Justificativa por camada** — talentos, tier, embelezamentos, runas, encantamentos/gemas, consumíveis. Uma linha por camada, dizendo o eixo que ela move.
4. **Contagem de embelezamentos** — "2 de 2 usados: peça A (efeito) e peça B (efeito)".
5. **O que muda em cada cenário** — M+, raide e imersão, em três linhas.
6. **Alternativas e custo** — o que trocar se faltar peça, se não houver Centelha, se o grupo não tiver curador.
7. **Lacunas** — o que depende de simulação e quais pendências do projeto afetam a resposta.

> **Pedido de substituição** ("vale trocar X por Y?") usa o formato de **laudo** da §3.2, não o formato de build completa. O laudo julga a peça; a build julga o conjunto.

## 4.1 Regras de redação

- Nome PT-BR **primeiro**, inglês em *itálico* ou entre parênteses. Se o pedido chegou em inglês, a resposta continua em PT-BR.
- Número sempre acompanhado da fonte ("Vig 3.910, ficha do Demo").
- Nunca use "provavelmente", "deve dar", "uns 5%" para dano. Use "não simulado".
- Toda afirmação sobre limite, teto ou restrição de slot deve citar a seção do documento.

---

# PARTE 5 — Limites, pendências e manutenção

## 5.1 O que este projeto ainda não sabe

| Lacuna | Impacto na resposta |
| :--- | :--- |
| Runas do Shadow e do Balance sem arbitragem externa | R5 fica **informativo** para essas duas specs |
| Export do SimC não traz a escolha das runas | R5 exige o campo extra `runas_atuais` |
| Mapa de índices de `slot_high_watermarks` incompleto | R7 parcial (só índice 14) |
| Nomes PT-BR de ~45 receitas de craft não auditadas | nomear só em inglês e marcar |
| Tabela de qualidade por rank do craft (318–331) | faixa, não valor exato |
| Encantamento de pulsos/mãos/capa inexistente | confirmar no jogo antes de afirmar |
| Leitura de `talents=` | o projeto não decodifica a import string: comparar por arquétipo, não por nó |
| Runas no export | `omnium_talents` não traz a escolha: pedir `runas_atuais` |
| Magilinha e Kit de Armadura no DB2 | os 3 Spellthreads e os 3 Kits de Midnight **não aparecem** na tabela `SpellItemEnchantment` deste build; se vierem em `enchant_id`, resolver pelo nome em [`encantamentos_e_gemas_s2.md`](encantamentos_e_gemas_s2.md:1) §2.2 |

### 5.1.1 Dados que a IA deve **pedir** quando faltarem

| Situação | Pedir |
| :--- | :--- |
| Export colado, mas sem `runas_atuais` | "quais são as 5 runas? formato `1A-2B-3A-4A-5A` ou os 5 spell IDs" |
| Item candidato só pelo nome | "qual o ID do item? (ou o link do Wowhead)" |
| Export truncado ou sem checksum | "cole de novo a partir da linha `# Nome - Spec`" |
| Comparação entre dois berloques | "qual dos dois está equipado hoje e quais são as recargas" |
| Dúvida de craft | "você tem a profissão? tem Centelha e quantas cristas?" |

Lista viva em [`pendencias.md`](pendencias.md:1).

## 5.2 Como atualizar os dados (nunca à mão)

```bash
node tools/auditar_craft.js                 # embelezamentos, missivas e reagentes (91 IDs)
node tools/auditar_armas_craft.js           # 29 armas craftáveis
node tools/varrer_itens.js --gravar 240840 240990   # descoberta de gemas por faixa de ID
node tools/auditar_encantamentos_gemas.js   # encantamentos, gemas e pernas
node tools/gerar_doc_encantamentos_gemas.js # regenera o .md a partir do .json
node tools/audit_ptbr.js                    # audita nome PT-BR dos itens já catalogados
node tools/consultar_ids.js <id>            # tooltip cru de um ID (PT-BR e texto)
node tools/mapear_enchant_ids.js <enchant_id>  # traduz enchant_id do SimC -> encantamento
node tools/mapear_enchant_ids.js            # reconstrói enchant_ids_s2.json (97 IDs)
node tools/consultar_enchant_id.js <id>     # nome oficial do encantamento + efeito do feitiço
node tools/analisar_enchant_db2.js --midnight  # cruza DB2 x catálogo: o que falta?
node tools/dump_enchant_row.js <id>         # linha crua do DB2, coluna a coluna
node tools/consultar_spells.js <id>         # tooltip de FEITIÇO em PT-BR e EN (404 = não existe)
node tools/listar_faixa.js 273000 273090    # todos os itens de uma faixa, com tipo/slot
node tools/varrer_armas.js 237700 238000    # só armas, por faixa (descobre ID pelo tipo)
node tools/monitorar_upgrades.js --ids tmp_ids.txt --gravar   # monitor de tetos 328/341
node tools/gerar_doc_monitor_upgrades.js    # regenera monitor_upgrades_s2.json/.md
```

Todo script é **idempotente** e usa o endpoint gratuito do Wowhead (`nether.wowhead.com`) quando possível — Firecrawl só para páginas de guia.

## 5.3 Regra de ouro para esta IA

> **Se não está escrito em um arquivo do projeto com fonte declarada, não é dado — é hipótese.** Trate hipótese como hipótese, diga o que ela muda e o que seria preciso para confirmar.

## 5.4 Consumível × insumo de receita — erro que já foi cometido neste projeto

Um item com tooltip de uso **não é automaticamente** um consumível disponível. Antes de colocar qualquer valor de consumível numa conta, verifique **de que receita ele é reagente**.

| Caso concreto | O que parecia | O que é |
| :--- | :--- | :--- |
| **Runa Vantus: Resplandecente** (`245879` / `245880`) | "a outra runa Vantus da temporada, +259/+324 de Versatilidade" | **insumo** da receita da Runa Vantus: Marés (1× por craft). A aura própria dela só vale contra chefes da Temporada 1 |

**Regra:** o número que entra no cálculo é o do **efeito que você recebe**, não o do efeito que o item *teria* se fosse usado. Três perguntas obrigatórias:

1. O item é consumível na temporada corrente, ou é insumo de outro item?
2. O alvo do efeito (raide, chefe, instância) é o da temporada corrente?
3. Qual dos ranks a receita produz de fato?

**Onde isso já custou erro:** a seção 3.5 de [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:465) listava as duas runas como alternativas e o checklist mandava "confirmar no jogo qual das duas a raide aceita". A resposta estava na receita ([`craft_receitas_s2.json`](craft_receitas_s2.json:1), `receitas.escrivania.runas_e_consumiveis`), que não estava no repositório. **Item sem receita registrada no projeto deve ter a receita levantada antes de ser classificado.**

---

# Glossário rápido

| PT-BR (oficial) | Inglês | Observação |
| :--- | :--- | :--- |
| Embelezamento | *Embellishment* | 2 efeitos no máximo |
| Embelezado (2) | *Embellished (2)* | tag de único-equipado |
| Magilinha | *Spellthread* | perna, Alfaiataria |
| Kit de Armadura | *Armor Kit* | perna, Couraria |
| Missiva Talassiana | *Thalassian Missive* | escolhe 2 secundários do craft |
| Centelha de Marés | *Spark of Tides* | reagente de craft da T2 |
| Crista de Névoa | *Mistcrest* | sobe o craft até 318/331 |
| Forjado com Peçonha | *Venomforged* | +7 sobre o teto do track |
| Amaldiçoado com Peçonha | *Venom-Cursed* | 344, cantrip de raide |
| Folio Ômnico | *Omnium Folio* | sistema de runas, 72 combinações |
| Runa Vantus: Marés | *Vantus Rune: Tides* | **único** consumível Vantus da T2 — +162 Vers no Templo de Ula'tek |
| Runa Vantus: Resplandecente | *Vantus Rune: Radiant* | **insumo** do craft da Marés; não é buff da T2 |
| Templo de Ula'tek | *Ula'tek Temple* | nome da instância do Abismo Peçonhento em tooltips de runa |
| Altar da Corrosão | *Altar of Corrosion* | Códice Corrosivo |
| Imersão | *Delve* | conteúdo solo, Tier 11 |
| Barganha de Xal'atath | *Xal'atath's Bargain* | afixo rotativo do +5 |
| Astúcia de Xal'atath | *Xal'atath's Guile* | afixo do +12 |
| Pisa-piras | *Delver's* | conjunto de imersão |
