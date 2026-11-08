# Bruxo Suplício (*Affliction*) — Season 2

> Ficha completa do spec: prioridade de atributos, talentos por cenário, armadura usada pelo top 50, embelezamentos, encantamentos, gemas, Folio Ômnico e Códice Corrosivo (Altar da Corrosão).
>
> **Origem:** [`affliction_warlock.json`](affliction_warlock.json:1) · **Patch:** 12.1.5 · **Atualizado:** 2026-11-06
>
> **Fontes:** Murlok top 50 de M+ do Suplício (`murlok.io/warlock/affliction/m+`, API da Blizzard, 06/11/2026) · Wowhead PT — Talent Builds do Suplício (Kalamazi, 17/10/2026) · Icy Veins e Method (12.1.5) · guias internos [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:1) e [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1)

---

## 1. Prioridade de atributos

| Ordem | Atributo | Valor médio no top 50 | Leitura |
| :-: | :--- | :--- | :--- |
| **1** | **Aceleração** | 28% (+1.123) | Ticks de DoT mais rápidos: é o eixo do spec |
| **2** | **Acerto Crítico** | 27% (+928) | Multa cada tick e alimenta Estilhaço |
| **3** | **Maestria** | 69% (+766) | Amplifica todo o dano periódico |
| **4** | **Versatilidade** | 4% (+204) | Só entra como sobra ou em PvP |

> ⚠️ **Ponto de atenção para o Folio:** o Murlok registra retorno decrescente após **+20% de atributo vindo de gear**. O Suplício do top 50 já está com **28% de Aceleração** — ou seja, **Aceleração já passou do ponto doce** e Crítico (27%) ainda está longe do teto de 35%. Isso decide a linha 4 do Folio na seção 6.

---

## 2. Talentos

### 2.1 Talento heroico por cenário

| Cenário | Talento heroico | Por quê |
| :--- | :--- | :--- |
| **M+** | **Ceifador de Almas** (*Soul Harvester*) | Ceifa Sombria dá Estilhaço e dano extra para Semente da Corrupção. Top 50 do Murlok: **27 Ceifador × 23 Hellcaller** |
| **Delve solo** | **Ceifador de Almas** | É a build que o Wowhead marca como *Best* em Delves, com as defensivas de Haunt |
| **Raide (alvo único)** | **Saqueador do Inferno** (*Hellcaller*) | Única build de raide datada para o Suplício (Wowhead, 17/10/2026) |

> ⚠️ **Conflito de fonte declarado.** O Wowhead, no resumo, diz que o Hellcaller é o mais forte "em alvo único **e** em Mythic+", e na seção de M+ diz que o Ceifador de Almas é a melhor opção. Icy Veins e Method dizem que o Ceifador domina tudo e o Hellcaller está sem sintonia. Detalhamento e resolução em [`talent_builds_season2.md`](talent_builds_season2.md:90).

### 2.2 Códigos de importação

| Uso | Talento heroico | Código |
| :--- | :--- | :--- |
| **M+ (recomendado)** | Ceifador de Almas | `CkQAAAAAAAAAAAAAAAAAAAAAAwMMzoZzMz2MzYWGAAwMmlZZmZWGDAM22GYATwMsFYYbAAAYAAAYmZmZMjNmxMzMzMMDzMzAAMgB` |
| **Delve solo (recomendado)** | Ceifador de Almas | `CkQAAAAAAAAAAAAAAAAAAAAAAwMMzoZzMz2MzYWGAAwMmlZZmZWGDAM22GYATwMsFYYbAAAYAAAYmZmZMjNmxMzMzMMDzMzAAMgB` |
| **Raide (recomendado)** | Hellcaller | `CkQAAAAAAAAAAAAAAAAAAAAAAwMzMzoZhhZmZmlBAAYmZZWmZmlxAAWgBmFjGzAysAWGAAAmBAAmZAzMjxYGmZMzMGMzMzAAmBG` |
| Raide — cleave | Hellcaller | `CkQAAAAAAAAAAAAAAAAAAAAAAwMmZGNbM2mZGzyAAAmZmlZxMzyYAALwAziRjZAZ2ALDAAAzAAAzMYMjZmtxwYmZmZYYmZGAgZgB` |
| Raide — alternativa | Ceifador de Almas | `CkQAAAAAAAAAAAAAAAAAAAAAAwMzMzoZhhZmZmlBAAYmZZ2mZmlxAAjllBGwEMDbBG2GAAAmBAAwMDzMjBzwMzMzMGMzMzAAmBG` |
| Delve — variante | Hellcaller | `CkQAAAAAAAAAAAAAAAAAAAAAAwMmZGNbM2MzMzyAAAmZmlZZmZWGDAYBGYWMaMDIzCYZAAAwAAAzMYMjZmNwMzYmxMDzMzAAMDMA` |

### 2.3 Build de Delve dedicada

O código de Delve do Suplício é **publicado igual por duas fontes independentes** — Icy Veins (seção Delves) e ExpCarry ("Best Affliction Warlock Delve Build") — com Ceifador de Almas. É a recomendação mais sustentada da spec. Vale a pena ter uma build própria em vez de copiar a de M+: conteúdo solo paga defesa e utilidade, não teto de dano.

**Rotina de sobrevivência no Delve (Kindo'jan Tier 11 incluso):**

| Situação | Ação |
| :--- | :--- |
| Antes de puxar um encontro perigoso | Deixar o **Círculo Demoníaco** armado |
| Pacote batendo em você | **Pet** absorvendo: Voidwalker para tanquar, Felhunter quando precisar de interrupção |
| Vida baixa de verdade | **Soulburn + Pedra de Vida** (+30% de cura e +20% de vida máxima por 12 s) e **só depois** Pacto Sombrio, que escala com a vida atual |
| Pet morreu | **Domínio Vil** devolve na hora — guardar para esse momento |
| Sem defesa nenhuma e tomando dano | **Drenar Vida com Soulburn** (dá absorção além da cura) |
| Regra geral | Sobreviver vale mais que terminar um cast extra |

---

## 3. Armadura e joias — o que o top 50 realmente usa

Frequência = quantos dos 50 melhores Suplícios de M+ equipam a peça. Nível máximo do próprio item.

### 3.1 Conjunto de tier — Necrólito Maldito

| Peça | Item | Frequência | Atributos (track máximo) |
| :--- | :--- | :-: | :--- |
| **Cabeça** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_helm_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Crânio do Necrólito Maldito" /> **Crânio do Necrólito Maldito** *Skull of the Damned Necrolyte* `271546` | **44** | Int 189 · Vig 3.910 · Mae 136 · Ver 65 |
| **Ombros** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_shoulder_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Pináculos do Necrólito Maldito" /> **Pináculos do Necrólito Maldito** *Spires of the Damned Necrolyte* `271544` | **42** | Int 141 · Vig 2.932 · Ace 50 · Ver 101 |
| **Peitoral** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_robe_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Vestes Chacoalhantes do Necrólito Maldito" /> **Vestes Chacoalhantes do Necrólito Maldito** *Damned Necrolyte's Rattling Robes* `271549` | **43** | Int 189 · Vig 3.910 · Ace 141 · Mae 60 |
| **Mãos** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_glove_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Agarres Calcinados do Necrólito Maldito" /> **Agarres Calcinados do Necrólito Maldito** *Damned Necrolyte's Charred Grasps* `271547` | **39** | Int 141 · Vig 2.932 · Crí 45 · Ace 106 |
| **Pernas** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_pant_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Amarras de Perna do Necrólito Maldito" /> **Amarras de Perna do Necrólito Maldito** *Damned Necrolyte's Leg Bindings* `271545` | **46** | Int 189 · Vig 3.910 · Ace 141 · Mae 60 |

> O top 50 usa **5 peças** do conjunto — diferente da Demonologia, onde a cabeça cantrip assume o lugar. Alternativa de cabeça: **Capucho Horrendo do Guardião da Peçonha** `271874` (Int 207 · Vig 4.385 · Mae 209, é *cantrip*), usada por **4** jogadores; troca +18 Int e +73 Maestria por perder o bônus de conjunto.

**Bônus de tier do Suplício** (ExpCarry, 11/09/2026):

| Peças | Efeito |
| :-: | :--- |
| **2** | Dano de **Corrupção** (ou Murchar) **+25%** e dano de **Agonia +15%** |
| **4** | Cada **Agonia Instável** ativa dá **+2% de dano** em feitiços e habilidades, até **6%**. **Semente da Corrupção aplica Agonia Instável a 20% de efetividade no alvo principal** |

> O 4 peças é o que liga a rotação de área ao alvo prioritário: dá para gastar Estilhaço em Semente sem abandonar a pressão no alvo que precisa morrer. É o bônus mais importante de perseguir na temporada.

> ✅ **Arbitrado pelo tooltip oficial em 06/11/2026** (conjunto `2066`, spells `1296568` e `1296569` — [Wowhead PT](https://www.wowhead.com/pt/item-set=2066)). Texto oficial do 4 peças: *"Cada **Agonia Instável** ativa aumenta em **2%** o dano causado por seus feitiços e habilidades, até um máximo de **6%**. A **Semente da Corrupção** aplica **Agonia Instável** ao seu alvo com **20% de eficácia**."*
>
> **Quem estava certo: ExpCarry.** O Method descreveu só metade ("a Semente aplica uma carga de Agonia Instável"), sem os 2%/6% e sem os 20% de eficácia — **incompleto**, não errado no que diz.
>
> 📌 **Correção de nome:** o nome PT de *Unstable Affliction* é **Agonia Instável** (não "Ferida Instável", como este projeto vinha escrevendo). "Agonia" sozinho é *Agony*.
>
> **Consequência de talentos (Method):** o 4 peças **removeu Patient Zero e Nocturnal Yield** e adicionou **Impetuous Wrath** e **Hedonic Gorging**. Resultado prático: talentos de Semente viraram build de área pura, e raide pede build de Agonia Instável.

### 3.2 Peças fora do conjunto

| Slot | Item | Frequência | Atributos | Fonte |
| :--- | :--- | :-: | :--- | :--- |
| **Pescoço** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_121_jewelry_neck03_green.jpg" width="20" height="20" alt="Relicário Aqiricida" /> **Relicário Aqiricida** *Aqirbane Reliquary* `268265` | **48** | Vig 2.466 · Crí/Ace/Mae/Ver 107 cada | Ula'tek (raide) |
| **Costas** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_tailoring_spellthread_blue.jpg" width="20" height="20" alt="Mortalha Sedosa do Seguidor" /> **Mortalha Sedosa do Seguidor** *Adherent's Silken Shroud* `239656` | **25** | Int · Vig — craftado | Craft (Alfaiataria) |
| **Pulsos** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_bracer_cloth_questbloodelf_b_01.jpg" width="20" height="20" alt="Braceletes do Mártir" /> **Braceletes do Mártir** *Martyr's Bindings* `239648` | **43** | Int · Vig — craftado | Craft (Alfaiataria) |
| **Cinto** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_belt_cloth_questbloodelf_b_01.jpg" width="20" height="20" alt="Banda do Mártir" /> **Banda do Mártir** *Martyr's Waistwrap* `239649` | **23** | Int · Vig — craftado | Craft (Alfaiataria) |
| **Pés** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_cloth_questbloodelf_b_01.jpg" width="20" height="20" alt="Sapatilhas do Mártir" /> **Sapatilhas do Mártir** *Martyr's Slippers* `239654` | **14** | Int · Vig — craftado | Craft (Alfaiataria) |
| **Anel 1** | <img src="https://wow.zamimg.com/images/wow/icons/medium/8268560.jpg" width="20" height="20" alt="Elo do Chama-enxame" /> **Elo do Chama-enxame** *Band of the Swarmcaller* `281029` | **32** | Vig · Ace 110 · Mae 295 | Kith'ix (raide) |
| **Anel 2** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_ring4_gold.jpg" width="20" height="20" alt="Elo Sin'dorei Magistral" /> **Elo Sin'dorei Magistral** *Masterwork Sin'dorei Band* `240949` | **23** | Anel craftado/joalheria | Craft / Joalheria |
| **Arma** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_ulatekfang_d_01_spirit.jpg" width="20" height="20" alt="Jan'thrazet, a Presa Anímica" /> **Jan'thrazet, a Presa Anímica** *Jan'thrazet, the Soul Fang* `271092` | **49** | Int 603 · Vig 2.192 · Ace 104 | Ula'tek (raide) |
| **Mão secundária** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_offhand_1h_dungeonharronir_c_01.jpg" width="20" height="20" alt="Lanterna de Aln'hara" /> **Lanterna de Aln'hara** *Aln'hara Lantern* `245769` | **31** | Int 127 · Vig 692 | Craft (Escrivania) |

**Alternativas por frequência** (use o que cair primeiro, sem perder o eixo de atributos):

| Slot | Alternativas |
| :--- | :--- |
| Costas | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cape_leather_raidrogueulatek_d_01.jpg" width="20" height="20" alt="Clâmide de Vodu Sedosa" /> **Clâmide de Vodu Sedosa** `268253` (7) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cape_cloth_outdooramaniloa_c_01.jpg" width="20" height="20" alt="Dragonas do Pisa-piras" /> **Dragonas do Pisa-piras** `272225` (6) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cape_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Manto de Elos do Necrólito Maldito" /> **Manto de Elos do Necrólito Maldito** `271541` (4) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cape_plate_outdooramaniloa_c_01.jpg" width="20" height="20" alt="Mortalha do Portador do Juramento" /> **Mortalha do Portador do Juramento** `272230` (4) |
| Cinto | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_belt_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Faixa Cáustica Envolta em Correntes" /> **Faixa Cáustica Envolta em Correntes** `268257` (8) · **Cilha Tilintante do Necrólito Maldito** `271543` (7) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_belt_cloth_dungeonharronir_c_01.jpg" width="20" height="20" alt="Atadura do Éter Etérea" /> **Atadura do Éter Etérea** `251222` (5) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_belt_cloth_raidmageulatek_d_01.jpg" width="20" height="20" alt="Cíngulo da Gruta Abissal" /> **Cíngulo da Gruta Abissal** `268232` (4) |
| Pés | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Solas do Necrólito Maldito" /> **Solas do Necrólito Maldito** `271548` (9) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_cloth_raidmageulatek_d_01.jpg" width="20" height="20" alt="Botinas Anímicas Crepitantes" /> **Botinas Anímicas Crepitantes** `268255` (7) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_cloth_raidpriestulatek_d_01.jpg" width="20" height="20" alt="Andarilhos Espirituais de Nek'zali" /> **Andarilhos Espirituais de Nek'zali** `268218` (6) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_cloth_outdooramaniloa_c_01.jpg" width="20" height="20" alt="Alpargatas do Pisa-piras" /> **Alpargatas do Pisa-piras** `272232` (5) |
| Pernas | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_pant_cloth_raidmageulatek_d_01.jpg" width="20" height="20" alt="Perneiras do Tececaos" /> **Perneiras do Tececaos** `281235` (3) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_pant_cloth_questbloodelf_b_01.jpg" width="20" height="20" alt="Perneiras do Mártir" /> **Perneiras do Mártir** `239651` (1) |
| Peito | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_robe_cloth_questbloodelf_b_01.jpg" width="20" height="20" alt="Vestimenta do Mártir" /> **Vestimenta do Mártir** `239655` (3) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_robe_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Vestes da Feiticeira Marejante" /> **Vestes da Feiticeira Marejante** `268221` (2) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_robe_cloth_outdooramaniloa_c_01.jpg" width="20" height="20" alt="Veste de Ritos Primordial" /> **Veste de Ritos Primordial** `273785` (1) |
| Ombros | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_shoulder_cloth_questbloodelf_b_01.jpg" width="20" height="20" alt="Dragonas do Mártir" /> **Dragonas do Mártir** `239650` (7) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_shoulder_cloth_outdooramaniloa_c_01.jpg" width="20" height="20" alt="Dragonas do Pisa-piras" /> **Dragonas do Pisa-piras** `272236` (1) |
| Cabeça | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_helm_cloth_raidpriestulatek_d_01.jpg" width="20" height="20" alt="Capuz do Sábio dos Pergaminhos Errante" /> **Capuz do Sábio dos Pergaminhos Errante** `268242` (1) · <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_helm_cloth_questbloodelf_b_01.jpg" width="20" height="20" alt="Coroa do Mártir" /> **Coroa do Mártir** `239652` (1) |

### 3.3 Berloques

| Berloque | Frequência | Efeito |
| :--- | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/8268563.jpg" width="20" height="20" alt="Tentáculo do Terror Pervertido" /> **Tentáculo do Terror Pervertido** *Twisted Horror's Tendril* `281215` | **38** | BiS — dano/proc de raide |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_tailoring_bag1_color2.jpg" width="20" height="20" alt="Bolsa sem Fundo de Gebbo" /> **Bolsa sem Fundo de Gebbo** *Gebbo's Bottomless Bag* `270164` | **28** | Saquinho que aprimora secundários de formas variadas |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_121_trinket_dungeon_ulatek_vile.jpg" width="20" height="20" alt="Ampola Torpe de Peçonha Volátil" /> **Ampola Torpe de Peçonha Volátil** `273796` | 15 | +992 de um secundário aleatório por 15 s, −142 de outro |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_archaeology_orcclans_crackedidol.jpg" width="20" height="20" alt="Ídolo da Perdição do Grão-bagateiro" /> **Ídolo da Perdição do Grão-bagateiro** `270169` | 9 | Aceleração 149 + dreno de Intelecto |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_tradeskillitem_sorcererswater.jpg" width="20" height="20" alt="Rocha Marinha do Clamaondas" /> **Rocha Marinha do Clamaondas** `270167` | 6 | Aceleração 148 + Intelecto em pilha |

> Para o Suplício, **Tentáculo + Bolsa** é o par dominante (66 dos 100 slots possíveis). A Ampola entra quando falta o Tentáculo.

### 3.4 BiS sem raide — só M+, Delve, craft e Catalyst

Recorte para quem não entra em raide. **Catalyst** = peça de tier convertida a partir de item de M+; **Craft** = peça fabricada.

| Slot | Item sem raide | Origem | Observação |
| :--- | :--- | :--- | :--- |
| Cabeça | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_helm_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Crânio do Necrólito Maldito" /> **Crânio do Necrólito Maldito** `271546` | **Catalyst** | Mantém o 5 peças do tier |
| Pescoço | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_121_jewelry_neck03_teal.jpg" width="20" height="20" alt="Feixe de Presas Protetoras" /> **Feixe de Presas Protetoras** `273781` | **M+ — Altar das Presas** | 341 · Crí 240 · Ace 182: é o melhor pescoço de Suplício fora da raide |
| Ombros | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_shoulder_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Pináculos do Necrólito Maldito" /> **Pináculos do Necrólito Maldito** `271544` | **Catalyst** | — |
| Costas | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_tailoring_spellthread_blue.jpg" width="20" height="20" alt="Mortalha Sedosa do Seguidor" /> **Mortalha Sedosa do Seguidor** `239656` | **Craft** | Já era a BiS do top 50 |
| Peitoral | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_robe_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Vestes Chacoalhantes do Necrólito Maldito" /> **Vestes Chacoalhantes do Necrólito Maldito** `271549` | **Catalyst** | — |
| Pulsos | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_bracer_cloth_questbloodelf_b_01.jpg" width="20" height="20" alt="Braceletes do Mártir" /> **Braceletes do Mártir** `239648` | **Craft** | Leva o Forro de Arcanotrama |
| Mãos | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_glove_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Agarres Calcinados do Necrólito Maldito" /> **Agarres Calcinados do Necrólito Maldito** `271547` | **Catalyst** | — |
| Cinto | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_belt_cloth_questbloodelf_b_01.jpg" width="20" height="20" alt="Banda do Mártir" /> **Banda do Mártir** `239649` | **Craft** | Alternativa M+: <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_belt_cloth_dungeonharronir_c_01.jpg" width="20" height="20" alt="Atadura do Éter Etérea" /> **Atadura do Éter Etérea** `251222` (Arena da Chaga do Caos) |
| Pernas | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_pant_cloth_raidwarlockulatek_d_01.jpg" width="20" height="20" alt="Amarras de Perna do Necrólito Maldito" /> **Amarras de Perna do Necrólito Maldito** `271545` | **Catalyst** | — |
| Pés | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_cloth_questbloodelf_b_01.jpg" width="20" height="20" alt="Sapatilhas do Mártir" /> **Sapatilhas do Mártir** `239654` | **Craft** | Alternativa M+/Delve: <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_cloth_outdooramaniloa_c_01.jpg" width="20" height="20" alt="Alpargatas do Pisa-piras" /> **Alpargatas do Pisa-piras** `272232` |
| Anel 1 | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_121_jewelry_ring02_green.jpg" width="20" height="20" alt="Elo do Senhor da Guerra Amani" /> **Elo do Senhor da Guerra Amani** `273792` | **M+ — Altar das Presas** | — |
| Anel 2 | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_ring4_gold.jpg" width="20" height="20" alt="Elo Sin'dorei Magistral" /> **Elo Sin'dorei Magistral** `240949` | **Craft / Joalheria** | — |
| Berloques | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_121_trinket_dungeon_ulatek_vile.jpg" width="20" height="20" alt="Ampola Torpe de Peçonha Volátil" /> **Ampola Torpe de Peçonha Volátil** `273796` + <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_tradeskillitem_sorcererswater.jpg" width="20" height="20" alt="Rocha Marinha do Clamaondas" /> **Rocha Marinha do Clamaondas** `270167` | **M+** | Par obtível sem raide |
| **Arma** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_zuljin_d_01.jpg" width="20" height="20" alt="Canalizador de Lumineira Polido" /> **Canalizador de Lumineira Polido** `273778` | **M+ — Altar das Presas** | Ver seção 3.5 |
| Mão secundária | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_offhand_1h_dungeonharronir_c_01.jpg" width="20" height="20" alt="Lanterna de Aln'hara" /> **Lanterna de Aln'hara** `245769` | **Craft (Escrivania)** | Leva a Pedra Ritual do Caçador |

### 3.5 Arma para usar junto com a Lanterna de Aln'hara

A Lanterna ocupa a **mão secundária**, então a arma principal tem de ser **de uma mão** — qualquer cajado fica incompatível (nem o Cetro Cerimonial Consagrado `272273` nem o Cajado-pique de Aln'hara `245771` entram na conta).

| Ordem | Arma | Origem | Nível | Int | Aceleração | Crítico | Maestria | Versatilidade |
| :-: | :--- | :--- | :-: | :-: | :-: | :-: | :-: | :-: |
| **1º** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_zuljin_d_01.jpg" width="20" height="20" alt="Canalizador de Lumineira Polido" /> **Canalizador de Lumineira Polido** `273778` | **M+ — Altar das Presas** | 341 | 586 | **+58** | — | **+46** | — |
| 2º | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_battledungeon_c_01.jpg" width="20" height="20" alt="Dente de Serpente Folheado" /> **Dente de Serpente Folheado** `159137` | M+ — Descanso do Rei | 341 | 586 | +45 | — | — | +58 |
| 3º | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_dungeonharronir_c_02.jpg" width="20" height="20" alt="Presa do Contágio" /> **Presa do Contágio** `251225` | M+ — Arena da Chaga do Caos | 341 | 586 | — | — | +60 | +43 |
| Reserva | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_outdooramaniloa_c_01.jpg" width="20" height="20" alt="Adaga do Eidolon Esquecido" /> **Adaga do Eidolon Esquecido** `272266` | Delve | 328 | 519 | +38 | +60 | — | — |
| Reserva | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_mace_1h_outdooramaniloa_c_01.jpg" width="20" height="20" alt="Pilão de Pó de Osso" /> **Pilão de Pó de Osso** `272270` | Delve | 328 | 519 | +60 | +38 | — | — |

**Por que o Canalizador ganha:** é o único de 341 que combina **Aceleração** (atributo nº 1 do spec) com **Maestria** (nº 3), e ainda traz um proc de dano Sagrado dividido entre inimigos próximos, com +30% por alvo adicional até 150% — ou seja, rende mais quanto mais o pacote está agrupado, que é exatamente o perfil de M+ do Suplício. O Dente de Serpente só vale se você já estiver com Aceleração muito alta e precisar de Versatilidade para sobreviver; a Presa do Contágio é a pior das três porque não tem Aceleração.

**As duas adagas de Delve** (`272266`, `272270`) são as únicas opções viáveis sem M+, mas ficam 13 níveis abaixo: **−67 de Intelecto** e ~6 de secundário por atributo. Servem de ponte, não de destino. Curiosamente o par **Aceleração + Crítico** delas é o encaixe ideal de secundários do Suplício — perde só por nível de item.

**Encantamento da arma:** **Rito dos Hash'ey** (38/50 do topo) ou **Acuidade dos Ren'dorei** (11/50).

> ⚠️ **Fonte:** a BiS do top 50 aponta **Jan'thrazet, a Presa Anímica** `271092` como arma principal (49/50), mas ela é drop de **Ula'tek, na raide** — está fora do seu recorte e não deve entrar na lista.

---

## 4. Embelezamentos

| Ordem | Embelezamento | Frequência |
| :-: | :--- | :-: |
| **1** | **Forro de Arcanotrama** *Arcanoweave Lining* — nos **Braceletes do Mártir** | **70** |
| **2** | **Pedra Ritual do Caçador** *Hunter's Ritual Stone* — na **Lanterna de Aln'hara** | **27** |

> Regra do limite (T2): só existem **2 efeitos** de embelezamento ativos por personagem. Não há limite de peças craftadas — uma terceira peça craftada vale pelos atributos, mas o terceiro efeito não liga. Ver [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1).

---

## 5. Encantamentos e gemas

### 5.1 Encantamentos

| Slot | Encantamento | Frequência |
| :--- | :--- | :-: |
| Cabeça | **Encantamento de Elmo — Runa Empoderada de Evasão** | 41 |
| Ombros | **Encantamento de Ombros — Graça de Amirdrassil** | 46 |
| Peito | **Encantamento de Peito — Marca da Alma-mundo** | 49 |
| Mãos | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_trade_archaeology_apexisscroll_uprez_color3.jpg" width="20" height="20" alt="Arte de Batalha Hash'ey Antiga: Olho do Lince" /> **Antiga Arte de Batalha Hash'ey: Olho do Lince** `283998` | 17 |
| Pernas | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_tailoring_spellthread_orange_spellthread.jpg" width="20" height="20" alt="Magilinha de Seda de Fogo Solar" /> **Fio Mágico de Seda Fogo-solar** `240133` | **50** |
| Pés | **Encantamento de Botas — Destreza do Lince** | 42 |
| Anéis | **Encantamento de Anel — Olhos da Águia** | **91** |
| Arma | **Rito dos Hash'ey** | 38 |

### 5.2 Gemas

| Slot | Gema | Frequência |
| :--- | :--- | :-: |
| **Diamante Eversong** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_epic_gem_cut_green.jpg" width="20" height="20" alt="Diamante do Canto Eterno Indecifrável" /> **Diamante Eversong Indecifrável** `240983` | 42 |
| **Prismática** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_nature_red.jpg" width="20" height="20" alt="Granada Veloz Impecável" /> **Granada Rápida Impecável** `240906` (Aceleração) | **106** |
| Prismática | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_fire_green.jpg" width="20" height="20" alt="Peridoto Mortal Impecável" /> **Peridoto Mortal Impecável** `240890` (Crítico) | 63 |
| Prismática | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_frost_red.jpg" width="20" height="20" alt="Granada Versátil Impecável" /> **Granada Versátil Impecável** `240910` | 9 |
| Prismática | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_void_red.jpg" width="20" height="20" alt="Granada Primorosa Impecável" /> **Granada Primorosa Impecável** `240908` | 7 |

---

## 6. Folio Ômnico

O Folio funciona em **todos** os ambientes (mundo aberto, Delve, M+ e raide). A recomendação **não muda entre specs de Bruxo**: a única arbitragem com fonte publicada é class-wide.

**Arbitragem registrada no projeto** (Icy Veins, guia de Bruxo): *"The default choice for Warlocks is Rune of Critical Power. If you have somehow managed to hit >35% Critical Strike chance and neglected Mastery in the process, consider using Rune of Masterful Cunning."* E: as runas de linha 5 (Sobrecarga e Energia Residual) *"offer similar output"*.

### 6.1 Por cenário

| Cenário | Código | Runas | Por quê |
| :--- | :-: | :--- | :--- |
| **Raide (alvo único)** | **C13** | `1A-2B-3A-4A-5A` | Padrão confirmado do Bruxo: Fogo Incontido + Autorrecomposição + Poder Crítico + Sobrecarga |
| **Raide (grupos densos)** | **C02** | `1A-2A-3A-4A-5B` | Troca a Autorrecomposição por Concha Maculada e a capstone por Energia Residual |
| **M+ (chaves médias)** | **C29** | `1A-2C-3A-4B-5B` | Reflexos de Lince + Aceleração Ardente: sobrevive a dano de atrito e mantém cadência |
| **M+ (+10 ou mais)** | **C10** | `1A-2A-3A-4D-5A` | Guerreiro Versátil é a única linha 4 com mitigação |
| **Delve Tier 11 solo** | **C24** | `1A-2B-3A-4D-5C` | Defesa máxima com eco de 50% |
| **Delve farm rápido** | **C23** | `1A-2B-3A-4D-5B` | Mitigação somada à Perenidade ampliada |

### 6.2 Linha 4 — Crítico (`4A`) ou Aceleração (`4B`)?

| Situação | Escolha | Motivo |
| :--- | :-: | :--- |
| **Padrão do Suplício** (Aceleração 28% · Crítico 27%) | **`4A` Poder Crítico** | Aceleração já passou do ponto doce de +20% e Crítico é o secundário nº 2, longe do teto de 35% |
| Aceleração **abaixo** de ~20% e Crítico acima de 35% | **`4B` Aceleração Ardente** | Caso em que o gargalo de cadência domina |
| Maestria negligenciada com Crítico >35% | **`4C` Astúcia Magistral** | Regra textual da fonte |

> ⚠️ **Divergência aberta no acervo:** [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:1) marca o `C06` (`1A-2A-3A-4B-5C`) como *"não suportado"* por usar Aceleração + Ecos, mas a checklist de raide do mesmo arquivo (linha 568) ainda recomenda **C06** para alvo único. Vale para Bruxo em geral, independente de spec. Precisa ser unificado — está registrado em [`pendencias.md`](pendencias.md:1).
>
> ⚠️ **Segunda divergência:** [`guia_masmorras_e_delves_s2.md`](guia_masmorras_e_delves_s2.md:261) chama o `C23` de `1A-2C-3A-4B-5B`. Pela matriz oficial, `C23` = `1A-2B-3A-4D-5B`, e `1A-2C-3A-4B-5B` é o `C29`. A tag está errada, o código não.

---

## 7. Códice Corrosivo (Altar da Corrosão)

> **Regra estrita:** o Códice funciona **apenas em mundo aberto e Imersões/Delves**. Em raide, M+ e PvP os poderes ficam **inativos**. Nada aqui muda sua build de M+.

### 7.1 Ranking para o Suplício

| Prioridade | Combo | Poderes | Por quê |
| :-: | :-: | :--- | :--- |
| **1º — agressivo seguro** | **P52** | Peçonha Insidiosa + Veneno Amaldiçoado | **+15% de Intelecto permanente** com o custo de vida anulado pela cura do Veneno. O guia interno classifica como "sem desvantagens", e o Suplício ainda cobre com Drenar Vida |
| **2º — dano periódico puro** | **P24** | Praga da Corrosão + Veneno Amaldiçoado | "Máximo dano periódico": +25% de dano de veneno e cada pulso cura você. É o combo com a identidade do spec |
| **3º — farm rápido (Tier 8–10)** | **P01** ou **P12** | Ciclo Ourobórico + Praga · Fauce Ofídica + Praga | Meta absoluto de limpeza; Fauce executa abaixo de 20% |
| **4º — Tier 11 / Kindo'jan solo** | **P39** | Olhar do Gorgoneion + Muco Virulento | 5 camadas de imunidade + petrificação em 50% de vida: a fortaleza do sistema |
| **5º — sobrevivência com dano** | **P41** | Olhar do Gorgoneion + Veneno Amaldiçoado | Petrifica e recupera vida pelos pulsos de veneno |

### 7.2 Combos a evitar no Suplício

| Combo | Por quê |
| :--- | :--- |
| **U11 Plumagem Lítica** / **P37**, **P44**, **P55**, **P59**, **P62**, **P64**, **P66** | +30% de armadura física para um conjurador de alcance: o ganho defensivo só aparece quando algo encosta em você |
| **U09 Aperto Viperino** e derivados | Puxão magnético que traz os inimigos para o seu colo — o oposto do que o Suplício quer |

---

## 8. Consumíveis

| Item | Escolha | Motivo |
| :--- | :--- | :--- |
| **Comida** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_166_bambooshoot02.jpg" width="20" height="20" alt="Costeletas Temperadas com Peçonha" /> **Costeletas Temperadas com Peçonha** `275258` / <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_draenor_saltedskulker_color04.jpg" width="20" height="20" alt="Prato de Baiacu" /> **Prato de Baiacu** `275260` (+65 do maior secundário) | Maior secundário = Aceleração |
| **Comida fixa** | **Lula Carmesim** / **Filé Beijado pela Vileza** (+58 Aceleração) | Só se o maior secundário virar Crítico e você precisar de Aceleração |
| **Frasco** | Frasco dos Cavaleiros Sangrentos · Frasco da Resistência Talassiana (Tier 11) | Dano × sobrevivência |
| **Runa Vantus** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_vantusrune_lightgreen.jpg" width="20" height="20" alt="Runa Vantus: Marés" /> **Runa Vantus: Marés** `272195` (+162 Vers) — única válida na raide da temporada | Ver §3.5 de [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:1) |
| **Óleo** | **Óleo de Fênix Talassiano** | **Não** usar Óleo da Aurora: só funciona com feitiços de cura |

---

## 9. Lacunas e conflitos

| Item | Situação |
| :--- | :--- |
| ~~Bônus de tier do Suplício~~ | **RESOLVIDO em 06/11/2026**: 2 peças = Corrupção +25% e Agonia +15%; 4 peças = +2% de dano por Agonia Instável ativa (até 6%) e Semente aplica Agonia Instável a 20% no alvo principal. Fonte: ExpCarry |
| **Talento heroico em M+** | Wowhead se contradiz; Icy Veins, Method e o top 50 do Murlok apontam Ceifador de Almas |
| **Folio Ômnico por spec** | Não existe fonte que diferencie Spec. A recomendação é class-wide e está marcada como tal |
| **Números de DPS do Suplício** | Nenhuma fonte publica simulação do Suplício em 12.1.5 no acervo — o ranking de raide usado no projeto é tier list, não medição |
| **Itens sem ficha local** | Peças do Mártir e algumas alternativas foram resolvidas via tooltip oficial em 06/11/2026 e gravadas em [`tools/_nomes_faltantes_suplicio.json`](tools/_nomes_faltantes_suplicio.json:1); os campos de atributo ficaram incompletos quando o tooltip não trazia o bloco de stats |
