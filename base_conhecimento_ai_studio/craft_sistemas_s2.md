# Sistema de Criação (*Craft*) da Temporada 2 — Embelezamentos, Missivas e todas as peças craftáveis

**Expansão:** World of Warcraft: Midnight
**Patch:** 12.1.5 — A Maldição de Ula'tek (*The Curse of Ula'tek*)
**Temporada:** Midnight Season 2 — reagente sazonal **Centelha de Marés** (*Spark of Tides*, `274476`)
**Dados brutos:** [`craft_sistemas_s2.json`](craft_sistemas_s2.json:1) (embelezamentos, missivas, reagentes) e [`craft_receitas_s2.json`](craft_receitas_s2.json:1) (inventário de receitas por profissão)
**Script re-executável:** [`tools/auditar_craft.js`](tools/auditar_craft.js:1)
**Padrão de formatação:** português do Brasil como idioma principal, com o nome em inglês entre parênteses `(*English Name*)` ou em *itálico* quando o nome PT-BR ainda não foi conferido no tooltip.

---

## 0. A regra que faltava — registrada nesta revisão

Três afirmações, que passam a valer como **regra fixa do projeto**:

| # | Regra | Consequência prática |
| :-: | :--- | :--- |
| **1** | Toda peça craftada da temporada tem **teto de nível de item 331** | Craft não substitui o tier mítico (334) nem os itens *Amaldiçoado com Peçonha* (344) por nível puro. Ele ganha por **atributo escolhido + embelezamento**. |
| **2** | Só é possível carregar **2 efeitos de embelezamento** ao mesmo tempo | A tag oficial no tooltip é **“Único-equipado: Embelezado (2)”** (*Unique-Equipped: Embellished 2*). Vale igual para efeito **embutido** na peça e para **reagente opcional** aplicado. |
| **3** | **Não existe limite de peças craftadas equipadas** | Um terceiro item craftado **pode ser equipado e continua valendo pelos atributos**. O que não funciona é o **terceiro efeito de embelezamento**. |

**Correção de leitura que o projeto passa a adotar:**

> “Forja normal sem embelezamento” **não** é uma categoria separada de item — é a mesma peça craftada **sem** o reagente de embelezamento aplicado (ou com o efeito removido por Chaveiro da Sorte). Ela **não** entra na conta dos dois.

| Situação | Conta para o limite de 2? | Efeito funciona? |
| :--- | :-: | :-: |
| Craftada **com** reagente de embelezamento | **Sim** | Sim |
| Craftada **sem** reagente (forja normal) | Não | — (não tem efeito) |
| Peça com embelezamento **embutido** (ex.: Elo do Adorador dos Loas) | **Sim** | Sim |
| Peça craftada que **teve o efeito removido** por Chaveiro da Sorte | Não | — |
| Terceira peça embelezada equipada | Sim, mas **estoura o limite** | **Não** — equipa, atributos valem, efeito fica inerte |

**Exemplo concreto de build válida:** 4 peças craftadas em 331 — pulsos com Forro de Arcanotrama, capa com Forro de Arcanotrama, e **mais duas** peças craftadas sem reagente de embelezamento. Total de efeitos ativos: **2**. Total de peças craftadas: **4**. Isso é legal.

### 0.1 Onde essa regra já foi aplicada

- [`season2_context.md`](season2_context.md:1) — seção 11, resumo do sistema e do teto 331.
- [`pendencias.md`](pendencias.md:1) — seção 3.10, com as pendências abertas desta rodada.
- Fichas de spec: [`demonology_warlock.md`](demonology_warlock.md:1), [`balance_druid.md`](balance_druid.md:1) e [`shadow_priest.md`](shadow_priest.md:1) receberam a nota de limite e a correção da profissão da Lanterna.

---

## 1. Níveis de item do craft

| Reagente na ordem de criação | Faixa de nível | Rótulo |
| :--- | :-: | :--- |
| Só **Centelha de Marés** | 292 – 305 | Craft base (a qualidade 1–5 define o topo da faixa) |
| Centelha + **80 Cristas de Névoa Heroicas** (*Hero Mistcrest*, `3445`) | 305 – 318 | Herói |
| Centelha + **80 Cristas de Névoa Míticas** (*Myth Mistcrest*, `3446`) | 318 – **331** | Mítico |

- **331 é o teto absoluto** do craft na temporada. Confirmação cruzada em duas fontes independentes: a página de criação da temporada e o próprio tooltip da Centelha de Marés, que fixa “nível inicial pela qualidade da criação (292–305)”.
- **Custo em Centelhas:** armadura, escudo, mão secundária e armas de uma mão = **2 Centelhas**; armas de duas mãos = **4 Centelhas**.
- **80 cristas = 4 ranks de melhoria** (20 por rank). Um craft mítico consome quase todo o teto semanal de cristas míticas.
- Cristas e Centelhas são **da temporada**: cristas de temporada anterior não sobem item da temporada atual.

### 1.1 Como o craft se encaixa no mapa de níveis do projeto

| Nível | Origem | Comparação com o craft |
| :-: | :--- | :--- |
| **344** | Mítico · Amaldiçoado com Peçonha | 13 acima do craft |
| **341** | Mítico+ · Forjado com Peçonha: Mito | 10 acima do craft |
| **334** | Mítico 6/6 (tier de raide) | 3 acima do craft |
| **331** | **Craft com cristas míticas (topo)** | — |
| **321** | Herói 6/6 | 10 abaixo do topo do craft |

> O craft de 331 não é upgrade cego. Ele é **a única forma de escolher os dois secundários e de escolher o embelezamento**. É por isso que ele aparece em BiS mesmo quando existe drop de 334 naquele slot.

---

## 2. Embelezamento (*Embellishment*) — o que é e como se comporta

| Forma | Como entra no item | Pode ser trocado? | Conta no limite? |
| :--- | :--- | :--- | :-: |
| **Reagente opcional** | Inserido na ordem de criação ou em *recraft* | Sim, recraftando | Sim |
| **Embutido** (*built-in*) | A peça já vem com o efeito; não aceita outro | **Não** | Sim |

### 2.1 Remoção do efeito — Chaveiro da Sorte

**Chaveiro da Sorte** (*Lucky Keychain*, `248130`) é um reagente opcional de Engenharia. Ao recraftar com ele, o efeito de embelezamento é substituído por **+1 de Brilho** (*Sparkle*) e o item **deixa de contar** para o limite, **sem gastar nova Centelha**.

- Funciona em **ordem pessoal** (ordem pública não permite a remoção).
- Também serve para trocar o efeito quando aparece um drop melhor no slot.

### 2.2 Onde o craft acontece

Ordens de criação com **Mar'nah** em Luaprata (`/way #2393 45.16 55.62`). Ordem **pessoal** para peça caras; ordem pública serve para preenchimento barato.

---

## 3. Catálogo de embelezamentos embutidos (peças que já vêm com efeito)

Todas as peças abaixo têm, no tooltip PT-BR, a linha **“Único-equipado: Embelezado (2)”**.

### 3.1 Tecido (Alfaiataria)

| Ícone | Item | ID | Slot | Nível | Efeito |
| :---: | :--- | :-: | :--- | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_cloth_questbloodelf_b_01.jpg" width="24" height="24" alt="Botinas de Fogo Solar" /> | **Botinas de Fogo Solar** *Sunfire Treads* | `239659` | pés | 246 | Conjunto **Ornamentos de Seda de Fogo Solar** (2 pç): acima de 80% de vida, +103 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_bracer_cloth_questbloodelf_b_01.jpg" width="24" height="24" alt="Braçadeiras de Fogo Solar" /> | **Braçadeiras de Fogo Solar** *Sunfire Bracers* | `239657` | pulsos | 246 | Idem (conjunto de 3 peças: braçadeiras, botinas, manto) |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cape_firelands_fireset_d_01.jpg" width="24" height="24" alt="Manto de Fogo Solar" /> | **Manto de Fogo Solar** *Sunfire Cloak* | `239658` | costas | 246 | Idem |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_belt_cloth_questbloodelf_b_01.jpg" width="24" height="24" alt="Faixa de Fogo Solar" /> | **Faixa de Fogo Solar** *Sunfire Sash* | `239663` | cinto | 246 | **Equipar:** chance de causar dano Radiante (3.707) ao alvo atual |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_cloth_questbloodelf_b_01.jpg" width="24" height="24" alt="Botinas de Arcanotrama" /> | **Botinas de Arcanotrama** *Arcanoweave Treads* | `239662` | pés | 246 | Conjunto **Ornamentos de Arcanotrama** (2 pç): acima de 80% de vida, +103 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_bracer_cloth_questbloodelf_b_01.jpg" width="24" height="24" alt="Braçadeiras de Arcanotrama" /> | **Braçadeiras de Arcanotrama** *Arcanoweave Bracers* | `239660` | pulsos | 246 | Idem |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cape_cloth_questbloodelf_b_01.jpg" width="24" height="24" alt="Manto de Arcanotrama" /> | **Manto de Arcanotrama** *Arcanoweave Cloak* | `239661` | costas | 246 | Idem |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_belt_cloth_questbloodelf_b_01.jpg" width="24" height="24" alt="Cordão de Arcanotrama" /> | **Cordão de Arcanotrama** *Arcanoweave Cord* | `239664` | cinto | 246 | **Equipar:** feitiços de cura e dano têm chance de +136 de Maestria por 12 s |

### 3.2 Couro (Couraria)

| Ícone | Item | ID | Slot | Nível | Efeito |
| :---: | :--- | :-: | :--- | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_leather_questbloodelf_b_01.jpg" width="24" height="24" alt="Ataduras de Raiz da Árvore do Mundo" /> | **Ataduras de Raiz da Árvore do Mundo** *World Tree Rootwraps* | `244601` | pés | 246 | Chance de criar um **Orbe de Poder Azerothiano**; coletar concede 75 do maior secundário por 15 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_belt_leather_questbloodelf_b_01.jpg" width="24" height="24" alt="Faixa de Bagatame" /> | **Faixa de Bagatame** *Hexwoven Strand* | `244606` | cinto | 246 | **Bagata Necrótica**: 161 de dano de Natureza a cada 1 s por 10 s, espalhando para inimigos próximos (até 5 vezes) |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_bracer_leather_questbloodelf_b_01.jpg" width="24" height="24" alt="Defletores do Andarilho das Fileiras" /> | **Defletores do Andarilho das Fileiras** *Row Walker's Deflectors* | `244612` | pulsos | 246 | Conjunto **Materiais da Travessa do Assassino** (2 pç): a cada 30 s, o próximo crítico concede **Vantagem** (efeito aleatório) |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_chest_leather_questbloodelf_b_01.jpg" width="24" height="24" alt="Segurança do Andarilho das Fileiras" /> | **Segurança do Andarilho das Fileiras** *Row Walker's Insurance* | `244613` | peitoral | 246 | Idem |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_glove_leather_questbloodelf_b_01.jpg" width="24" height="24" alt="Guantes Velozes do Andarilho das Fileiras" /> | **Guantes Velozes do Andarilho das Fileiras** *Row Walker's Swiftgrips* | `244614` | mãos | 246 | Idem |

### 3.3 Malha (Couraria)

| Ícone | Item | ID | Slot | Nível | Efeito |
| :---: | :--- | :-: | :--- | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_chest_mail_questbloodelf_b_01.jpg" width="24" height="24" alt="Guarda-tronco do Conservador de Mundos" /> | **Guarda-tronco do Conservador de Mundos** *World Tender's Trunkplate* | `244609` | peitoral | 246 | Conjunto **Paramentos do Guardirraiz** (2 pç): chance de conceder **159 de secundário aleatório** por 15 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_boot_mail_questbloodelf_b_01.jpg" width="24" height="24" alt="Sapatiraiz do Conservador de Mundos" /> | **Sapatiraiz do Conservador de Mundos** *World Tender's Rootslippers* | `244610` | pés | 246 | Idem |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_belt_mail_questbloodelf_b_01.jpg" width="24" height="24" alt="Arvofecho do Conservador de Mundos" /> | **Arvofecho do Conservador de Mundos** *World Tender's Barkclasp* | `244611` | cinto | 246 | Idem |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_glove_mail_questbloodelf_b_01.jpg" width="24" height="24" alt="Guantes da General-patrulheira" /> | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_skinning_thalassianscale_violet.jpg" width="20" height="20" alt="Guantes da General-patrulheira" /> **Guantes da General-patrulheira** *Ranger-General's Grips* | `244602` | mãos | 246 | Chance de marcar o alvo; um **Patrulheiro Élfico** desfere Ataque Surpresa (6.531 de dano Físico) |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_bracer_mail_questbloodelf_b_01.jpg" width="24" height="24" alt="Embraces Lançadores de Machado" /> | **Embraces Lançadores de Machado** *Axe-Flingin' Bands* | `244605` | pulsos | 246 | **Fervor da Batalha**: +11 de Aceleração por 15 s, até 5 acúmulos |

### 3.4 Placa, arma e escudo (Ferraria)

| Ícone | Item | ID | Slot | Nível | Efeito |
| :---: | :--- | :-: | :--- | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_plate_questbloodelf_b_01_boot.jpg" width="24" height="24" alt="Pés Ligeiros da Travessa do Assassino" /> | **Pés Ligeiros da Travessa do Assassino** *Murder Row Fleet Feet* | `244463` | pés | 246 | Chance de +80 de Aceleração por 10 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_questbloodelf_b_02.jpg" width="24" height="24" alt="Anzol da Travessa do Assassino" /> | **Anzol da Travessa do Assassino** *Murder Row Fishhook* | `244679` | adaga 1M | 246 | Chance de sangrar o alvo: 846 de dano Físico a cada 2 s por 10 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_shield_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Paliçada do Cavaleiro Comandante" /> | **Paliçada do Cavaleiro Comandante** *Knight-Commander's Palisade* | `244472` | escudo | 246 | Escudo de 1.192 de absorção por 6 s; se rompido, explode em 1.192 de dano Sagrado (Penitência da Paliçada) |

### 3.5 Acessórios, capa e berloques

| Ícone | Item | ID | Slot | Nível | Efeito |
| :---: | :--- | :-: | :--- | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_necklace1_gold.jpg" width="24" height="24" alt="Torque de Fênix Talassiana" /> | **Torque de Fênix Talassiana** *Thalassian Phoenix Torque* | `241139` | pescoço | 246 | Chamas da Fênix: cura 5.848 em 10 s em aliado ou 4.675 de Fogo em 10 s em inimigo |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_ring1_gold.jpg" width="24" height="24" alt="Sinete das Bênçãos Azerothianas" /> | **Sinete das Bênçãos Azerothianas** *Signet of Azerothian Blessings* | `241140` | anel | 246 | Ressonância com a Alma do Mundo: +23 em **todos** os secundários por 15 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_ring3_silver.jpg" width="24" height="24" alt="Elo do Adorador dos Loas" /> | **Elo do Adorador dos Loas** *Loa Worshiper's Band* | `251513` | anel | 246 | Evoca o avatar de um **loa** para ajudar em combate |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_necklace3_silver.jpg" width="24" height="24" alt="Matriz de Proteção de Pedra do Caos" /> | **Matriz de Proteção de Pedra do Caos** *Voidstone Shielding Array* | `251073` | pescoço | 246 | **Uso:** Barreira de 71.597 de absorção por 10 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_alchemists_stone.jpg" width="24" height="24" alt="Pedra do Alquimista do Magíster" /> | **Pedra do Alquimista do Magíster** *Magister's Alchemist Stone* | `241340` | berloque | 246 | +40% nos efeitos de poções de cura e de mana |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_darkmoondominions_bloom.jpg" width="24" height="24" alt="Domínio de Negraluna: Caçada" /> | **Domínio de Negraluna: Caçada** *Darkmoon Dominion: Hunt* | `246304` | berloque | 246 | +144 de secundários por 15 s conforme o tipo da criatura |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_darkmoondominions_hunt.jpg" width="24" height="24" alt="Domínio de Negraluna: Sangue" /> | **Domínio de Negraluna: Sangue** *Darkmoon Dominion: Blood* | `246305` | berloque | 246 | Astúcia do Andarilho: +379 no **segundo** secundário mais baixo por 15 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_darkmoondominions_rot.jpg" width="24" height="24" alt="Domínio de Negraluna: Podridão" /> | **Domínio de Negraluna: Podridão** *Darkmoon Dominion: Rot* | `246306` | berloque | 246 | Raízes Pútridas: 214 de Natureza a cada 2 s por 6 s, até 10 acúmulos |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_darkmoondominions_void.jpg" width="24" height="24" alt="Domínio de Negraluna: Caos" /> | **Domínio de Negraluna: Caos** *Darkmoon Dominion: Void* | `246307` | berloque | 246 | Vidro Caótico: +105 de Versatilidade por 15 s, acumulável |

---

## 4. Reagentes opcionais de embelezamento — o catálogo completo

A coluna **“Usável com”** é a linha literal do tooltip oficial. Ela é a **única** fonte aceitável para dizer que um embelezamento cabe em um slot. Nenhum guia de terceiro sobrepõe essa linha.

| Embelezamento | ID | Profissão | “Usável com” (tooltip PT-BR) | Efeito |
| :--- | --: | :--- | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_tailoring_rare_cloth_violet_rare.jpg" width="20" height="20" alt="Forro de Arcanotrama" /> **Forro de Arcanotrama** *Arcanoweave Lining* | `240167` | Alfaiataria | maior parte das **armaduras** não embelezadas | Moreia de mana concede **Percepção da Arcanotrama**: atributo primário para você **e um aliado** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_tailoring_rare_cloth_orange-_rare-cloth.jpg" width="20" height="20" alt="Forro de Seda de Fogo Solar" /> **Forro de Seda de Fogo Solar** *Sunfire Silk Lining* | `240165` | Alfaiataria | maior parte das **armaduras** não embelezadas | Cura/dano periódico concede +5 de primário por 15 s, até 5 acúmulos |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_121_professions_fishing_curseworm_red.jpg" width="20" height="20" alt="Forro de Couro de Cobra" /> **Forro de Couro de Cobra** *Snakeskin Lining* | `270898` | Couraria | maior parte das **armaduras** não embelezadas | Ácido Corrosivo; dano repetido tem chance de detonar e espalhar |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_leatherworking_armor_banding_green.jpg" width="20" height="20" alt="Vínculo de Esporos Primevos" /> **Vínculo de Esporos Primevos** *Primal Spore Binding* | `244608` | Couraria | **armas e armaduras** não embelezadas | Esporos Explosivos: cura aliados ou fere inimigos conforme o alvo |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_leatherworking_armor_banding_brown.jpg" width="20" height="20" alt="Elo Devorador" /> **Elo Devorador** *Devouring Banding* | `244675` | Couraria | **armas e armaduras** não embelezadas | Setas Devoradoras: dano + aumenta o maior secundário |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_jewelry_necklace_139.jpg" width="20" height="20" alt="Patuá de Pango Abençoado" /> **Patuá de Pango Abençoado** *Blessed Pango Charm* | `244604` | Couraria | maioria dos **equipamentos** não embelezados | Loa Kurzi concede **Versatilidade ao alvo** (cura) |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_darkmoonsigil_hunt.jpg" width="20" height="20" alt="Signo de Negraluna: Sangue" /> **Signo de Negraluna: Sangue** *Darkmoon Sigil: Blood* | `245872` | Escrivania | **armas e mão secundária** não embelezadas | Astúcia do Andarilho: +76 no segundo secundário mais baixo por 15 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_darkmoonsigil_bloom.jpg" width="20" height="20" alt="Signo de Negraluna: Caçada" /> **Signo de Negraluna: Caçada** *Darkmoon Sigil: Hunt* | `245876` | Escrivania | **armas e mão secundária** não embelezadas | +56 de secundários por 15 s conforme o tipo da criatura |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_darkmoonsigil_rot.jpg" width="20" height="20" alt="Signo de Negraluna: Podridão" /> **Signo de Negraluna: Podridão** *Darkmoon Sigil: Rot* | `245878` | Escrivania | **armas e mão secundária** não embelezadas | Raízes Pútridas: 113 de Natureza a cada 2 s por 6 s, até 10 acúmulos |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_darkmoonsigil_void.jpg" width="20" height="20" alt="Signo de Negraluna: Caos" /> **Signo de Negraluna: Caos** *Darkmoon Sigil: Void* | `245874` | Escrivania | **armas e mão secundária** não embelezadas | Vidro Caótico: +40 de Versatilidade por 15 s, acumulável |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/item_cutmetagem.jpg" width="20" height="20" alt="Íris Focalizadora Prismática" /> **Íris Focalizadora Prismática** *Prismatic Focusing Iris* | `251488` | Joalheria | maioria dos **equipamentos** não embelezados | Feixe de 1.102 de dano Arcano por segundo por 4 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_jewelry_ring_77.jpg" width="20" height="20" alt="Bandoleira de Gemas Estabilizadora" /> **Bandoleira de Gemas Estabilizadora** *Stabilizing Gemstone Bandolier* | `251490` | Joalheria | maioria dos **equipamentos** não embelezados | Amplia embelezamentos de Joalheria no personagem |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_111_goblintrikekeychain_ventureco.jpg" width="20" height="20" alt="Chaveiro da Sorte" /> **Chaveiro da Sorte** *Lucky Keychain* | `248130` | Engenharia | maioria dos **equipamentos** não embelezados | **Não é embelezamento**: remove o efeito e devolve +1 de Brilho |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_pet_futurebotpet_orange.jpg" width="20" height="20" alt="M3D1 de Bolso" /> **M3D1 de Bolso** *M3DDY, Travel-Sized* | `248136` | Engenharia | maioria dos **equipamentos** não embelezados | Revive o jogador no mundo aberto |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_engineering_manufacturedparts_electricalparts_color1.jpg" width="20" height="20" alt="Detonadores de Tornozelo Cinéticos" /> **Detonadores de Tornozelo Cinéticos** *Kinetic Ankle Primers* | `248133` | Engenharia | **botas de Engenharia** | Lança o jogador no ar e derruba inimigos na queda |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_robotpet.jpg" width="20" height="20" alt="B1P, Calcinador de Almas" /> **B1P, Calcinador de Almas** *B1P, Scorcher of Souls* | `248592` | Engenharia | equipamentos criados de **Engenharia** | Cone de dano de Fogo por 6 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_pet_futurebotpet.jpg" width="20" height="20" alt="B0P, Seletor de Cabuns" /> **B0P, Seletor de Cabuns** *B0P, Curator of Booms* | `257741` | Engenharia | equipamentos criados de **Engenharia** | Até 5 explosões de dano/cura |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/creatureportrait_robot_bulldog.jpg" width="20" height="20" alt="P51U, Filhotinho Sossegado" /> **P51U, Filhotinho Sossegado** *HU5H, Nonchalant Pup* | `255844` | Engenharia | equipamentos criados de **Engenharia** | Invisibilidade de 4–18 s no mundo aberto |

> ⚠️ **Observação de tooltip:** apenas cinco reagentes mostram a linha “Único-equipado: Embelezado (2)” **no próprio tooltip** (`244604`, `244608`, `244675`, `245872`, `245874`, `245876`, `245878`). Nos demais a restrição aparece na peça final. Isso é comportamento de exibição, **não** dispensa do limite.

---

## 5. Embelezamentos novos da Temporada 2

Introduzidos com a Centelha de Marés. **Não substituem** os da temporada anterior — os antigos continuam valendo e continuam contando no mesmo limite de 2.

| Embelezamento | ID | “Usável com” | Efeito |
| :--- | --: | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_blacksmithing_weightstone_green.jpg" width="20" height="20" alt="Pedra Ritual do Caçador" /> **Pedra Ritual do Caçador** *Hunter's Ritual Stone* | `273060` (e `273059`) | **Armas de Ferraria de Midnight** | Chance de **101 de secundário aleatório** por 15 s; **+50% durante Caça às Presas**, só no mundo aberto |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_ulatek_d_01.jpg" width="20" height="20" alt="Presa Adornada" /> **Presa Adornada** *Adorned Fang* | `273069` (e `273068`) | maioria dos **equipamentos** não embelezados | Chance de **Aceleração**, com chance maior contra alvos com pouca vida |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_jewelcrafting_cut-epic-gem_color1.jpg" width="20" height="20" alt="Amolita Polida" /> **Amolita Polida** *Polished Ammolite* | `273066` (e `273065`) | maioria dos **acessórios** não embelezados | Crítico acumulativo; no máximo de acúmulos, o crítico causa explosão de dano |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_engineering_scope_color3.jpg" width="20" height="20" alt="Olho de Cobra Enrolado" /> **Olho de Cobra Enrolado** *Coiled Snake-Eye* | `273062` | **Armas de Fogo de Engenharia de Midnight** | +82 de secundário aleatório; se o gatilho for crítico, vira o **maior** secundário |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_121_professions_fishing_curseworm_red.jpg" width="20" height="20" alt="Forro de Couro de Cobra" /> **Forro de Couro de Cobra** *Snakeskin Lining* | `270898` | maior parte das **armaduras** não embelezadas | Ácido Corrosivo com detonação em área |

### 5.1 O que a restrição de slot muda para este projeto

| Embelezamento | Onde a comunidade usa | O que o tooltip permite | Decisão do projeto |
| :--- | :--- | :--- | :--- |
| **Pedra Ritual do Caçador** | arma de Ferraria **e** Lanterna de Aln'hara (mão secundária) | **somente armas de Ferraria** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_darkmoonsigil_hunt.jpg" width="20" height="20" alt="Signo de Negraluna: Sangue" /> **Divergência aberta.** Há Lanternas de Escrivania rodando com esse proc (101 de secundário e +50% em Caça às Presas, confirmado em item de jogador). O tooltip diz uma coisa, o item de jogo mostra outra: **vale o texto do item equipado**; para o catálogo, a recomendação segue sendo **Signo de Negraluna** (`245872`/`245874`/`245876`/`245878`) em mão secundária |
| **Amolita Polida** | anel do Cavaleiro da Morte Sangue | **acessórios** | Válido em anel/pescoço craftado |
| **Olho de Cobra Enrolado** | arma de fogo do Caçador | **armas de fogo de Engenharia** | Fora do escopo dos três specs do projeto |
| **Forro de Arcanotrama** | pulsos, capa, cinto, botas | **armaduras** | Válido em qualquer armadura craftada, inclusive tecido e couro |

---

## 6. Missivas — escolher os atributos secundários

As missivas são feitas por **Escrivania** ou compradas na Casa de Leilões. Entram na janela de criação (ou de ordem) e definem **dois** secundários.

> 🔧 **Consequência para qualquer ficha de item:** peça craftada **não tem secundário fixo**. O tooltip oficial mostra *“Atributo Aleatório 1 / 2”* justamente porque a escolha é da missiva. Em documento de build, registre **só os atributos fixos** (primário, Vigor, armadura) e trate a dupla de secundários e o embelezamento como **opções recomendadas**, não como propriedade do item.

### 6.1 Missivas de equipamento (armadura e arma)

| Missiva (PT-BR oficial) | Nome em inglês | ID | Atributos |
| :--- | :--- | --: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_scroll_02_uprez.jpg" width="20" height="20" alt="Missiva Talassiana da Aurora" /> **Missiva Talassiana da Aurora** | *Thalassian Missive of the Aurora* | `245781` | Versatilidade + Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_scroll_02_uprez_color2.jpg" width="20" height="20" alt="Missiva Talassiana da Febre Ardente" /> **Missiva Talassiana da Febre Ardente** | *Thalassian Missive of the Feverflare* | `245783` | Maestria + Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_scroll_02_uprez_color3.jpg" width="20" height="20" alt="Missiva Talassiana do Clarão de Fogo" /> **Missiva Talassiana do Clarão de Fogo** | *Thalassian Missive of the Fireflash* | `245785` | Crítico + Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_scroll_02_uprez_color4.jpg" width="20" height="20" alt="Missiva Talassiana do Harmonioso" /> **Missiva Talassiana do Harmonioso** | *Thalassian Missive of the Harmonious* | `245787` | Versatilidade + Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_scroll_02_uprez_color2.jpg" width="20" height="20" alt="Missiva Talassiana do Inigualável" /> **Missiva Talassiana do Inigualável** | *Thalassian Missive of the Peerless* | `245789` | Crítico + Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_scroll_02_uprez_color5.jpg" width="20" height="20" alt="Missiva Talassiana do Gumepresto" /> **Missiva Talassiana do Gumepresto** | *Thalassian Missive of the Quickblade* | `245791` | Versatilidade + Crítico |

> São **6 combinações** — todas as duplas de quatro secundários, menos os pares “dobrados”. Não existe missiva que dê o mesmo atributo duas vezes, nem missiva com três atributos.
> **“Gumepresto”** é o nome oficial PT-BR de *Quickblade*; a tradução “Lâmina Veloz” que circula em guias **não** é a do cliente.

### 6.2 Missivas de equipamento de profissão

Só valem para ferramentas e equipamentos de profissão — **não** para armadura, arma ou acessório de combate.

| Missiva | ID | Atributo de profissão |
| :--- | --: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_80_warscroll_fortitude_uprez.jpg" width="20" height="20" alt="Missiva Talassiana da Velocidade de Criação" /> **Missiva Talassiana da Velocidade de Criação** | `245820` | Velocidade de Criação |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_80_scroll_uprez.jpg" width="20" height="20" alt="Missiva Talassiana da Engenhosidade" /> **Missiva Talassiana da Engenhosidade** | `245814` | Engenhosidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_80_scroll_uprez_color2.jpg" width="20" height="20" alt="Missiva Talassiana da Multicriação" /> **Missiva Talassiana da Multicriação** | `245818` | Multicriação |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_80_scroll_uprez_color1.jpg" width="20" height="20" alt="Missiva Talassiana da Desenvoltura" /> **Missiva Talassiana da Desenvoltura** | `245816` | Economia |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_80_warscroll_fortitude_uprez_color5.jpg" width="20" height="20" alt="Missiva Talassiana da Destreza" /> **Missiva Talassiana da Destreza** | `245826` | Destreza |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_80_warscroll_fortitude_uprez_color2.jpg" width="20" height="20" alt="Missiva Talassiana da Finesse" /> **Missiva Talassiana da Finesse** | `245822` | Finura |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_80_warscroll_fortitude_uprez_color3.jpg" width="20" height="20" alt="Missiva Talassiana da Percepção" /> **Missiva Talassiana da Percepção** | `245824` | Percepção |

### 6.3 Como a missiva aparece no export do SimC

O campo `crafted_stats` guarda dois IDs numéricos na ordem escolhida. Exemplo real do projeto: `239648` com `crafted_stats=36/32` = **Aceleração + Crítico** = Missiva do Clarão de Fogo (`245785`). A tabela de decodificação está em [`import_e_interpretacao_s2.md`](import_e_interpretacao_s2.md:214).

---

## 7. Matriz de slots craftáveis por profissão

Cada célula é um slot em que existe receita de equipamento na temporada. Base de dados completa (nome a nome) em [`craft_receitas_s2.json`](craft_receitas_s2.json:1).

| Profissão | Cabeça | Ombros | Peitoral | Pulsos | Mãos | Cinto | Pernas | Pés | Costas | Pescoço | Anel | Berloque | Arma | Mão sec. |
| :--- | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: |
| **Ferraria** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — | ✅ 1M e 2M | ✅ escudo |
| **Couraria** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — | — | — |
| **Alfaiataria** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | — | — |
| **Joalheria** | — | — | — | — | — | — | — | — | — | ✅ | ✅ | — | — | — |
| **Escrivania** | — | — | — | — | — | — | — | — | — | — | — | ✅ PvP | ✅ cajado/arco | ✅ |
| **Engenharia** | ✅ | — | — | ✅ | — | — | — | ✅ | — | — | — | — | ✅ arma de fogo | — |
| **Alquimia** | — | — | — | — | — | — | — | — | — | — | — | ✅ | — | — |

**Leitura prática para os três specs do projeto (tecido, couro e malha):**

| Slot desejado | Profissão que cobre | Famílias craftáveis |
| :--- | :--- | :--- |
| Pulsos | Alfaiataria / Couraria / Engenharia | Mártir, Arcanoweave/Sunfire (embutido), Agente de Luaprata, Andarilho das Fileiras (embutido), Thalassian Competitor's |
| Cinto | Alfaiataria / Couraria | Mártir, Arcanoweave/Sunfire (embutido), Agente de Luaprata, Bagatame (embutido) |
| Pés | Alfaiataria / Couraria / Engenharia | Mártir, Fogo Solar/Arcanotrama (embutido), Agente de Luaprata, Andarilho (embutido) |
| Capa | Alfaiataria | Seguidor, Cortesão, Arcanoweave/Sunfire (embutido) |
| Ombros / Mãos | Couraria (couro e malha) | Agente de Luaprata, Andarilho, Ranger-General (embutido) |
| Peitoral | Couraria | Andarilho das Fileiras (embutido), Conservador de Mundos (embutido) |
| Anel / Pescoço | Joalheria | Sin'dorei Magistral, Adorador dos Loas (embutido), Bênçãos Azerothianas (embutido), Fênix Talassiana (embutido), Pedra do Caos (embutido) |
| Mão secundária | Escrivania | Lanterna de Aln'hara, Rootwarden's Lamp |

### 7.1 Armas craftáveis — catálogo completo com nome oficial

Nomes copiados do tooltip PT-BR. Dados completos (atributos, dano por segundo e texto) em [`craft_armas_s2.json`](craft_armas_s2.json:1).

| Ícone | Arma (nome oficial PT-BR) | ID | Tipo | Nível | Profissão / família |
| :---: | :--- | :-: | :--- | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_questbloodelf_b_02.jpg" width="24" height="24" alt="Misericórdia do Andarilho" /> | **Misericórdia do Andarilho** *Farstrider's Mercy* | `237837` | adaga 1M | 246 | Ferraria · Andarilho |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_axe_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Picador do Andarilho" /> | **Picador do Andarilho** *Farstrider's Chopper* | `237850` | machado 1M | 246 | Ferraria · Andarilho |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_questbloodelf_b_02.jpg" width="24" height="24" alt="Anzol da Travessa do Assassino" /> | **Anzol da Travessa do Assassino** *Murder Row Fishhook* | `244679` | adaga 1M | 246 | Ferraria · Travessa do Assassino · **embelezado embutido** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Faca Ritualística do Magíster" /> | **Faca Ritualística do Magíster** *Magister's Ritual Knife* | `237838` | adaga 1M | 246 | Ferraria · Magíster |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_sword_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Espada de Mana do Magíster" /> | **Espada de Mana do Magíster** *Magister's Mana Sword* | `237843` | espada 1M | 246 | Ferraria · Magíster |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_axe_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Cutelo do Magíster" /> | **Cutelo do Magíster** *Magister's Cleaver* | `237844` | machado 1M | 246 | Ferraria · Magíster |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/mace_2h_blacksmithing_d_04_icon.jpg" width="24" height="24" alt="Despedida do Magíster" /> | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_blacksmithing_blacksmithingalloys_gloaming.jpg" width="20" height="20" alt="Despedida do Magíster" /> **Despedida do Magíster** *Magister's Valediction* | `237849` | maça 2M | 246 | Ferraria · Magíster |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_sword_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Lâmina do Quebra-feitiço" /> | **Lâmina do Quebra-feitiço** *Spellbreaker's Blade* | `237839` | espada 1M | 246 | Ferraria · Quebra-feitiço |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_mace_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Ultimato do Quebra-feitiço" /> | **Ultimato do Quebra-feitiço** *Spellbreaker's Ultimatum* | `237841` | maça 1M | 246 | Ferraria · Quebra-feitiço |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_glaive_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Glaive de Guerra do Quebra-feitiço" /> | **Glaive de Guerra do Quebra-feitiço** *Spellbreaker's Warglaive* | `237840` | glaive 1M | 246 | Ferraria · Quebra-feitiço |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_shield_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Repreensão do Quebra-feitiço" /> | **Repreensão do Quebra-feitiço** *Spellbreaker's Rebuke* | `237831` | escudo | 246 | Ferraria · Quebra-feitiço |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_shield_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Paliçada do Cavaleiro Comandante" /> | **Paliçada do Cavaleiro Comandante** *Knight-Commander's Palisade* | `244472` | escudo | 246 | Ferraria · Cavaleiro Comandante · **embelezado embutido** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_hand_1h_dungeonharronir_c_01.jpg" width="24" height="24" alt="Garra de Floraforja" /> | **Garra de Floraforja** *Bloomforged Claw* | `237845` | arma de punho 1M | 246 | Ferraria · Floraforja |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_axe_2h_dungeonharronir_c_01.jpg" width="24" height="24" alt="Machadão de Floraforja" /> | **Machadão de Floraforja** *Bloomforged Greataxe* | `237842` | machado 2M | 246 | Ferraria · Floraforja |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_sword_2h_questbloodelf_b_01.jpg" width="24" height="24" alt="Lâmina de Guerra do Cavaleiro Sangrento" /> | **Lâmina de Guerra do Cavaleiro Sangrento** *Blood Knight's Warblade* | `237846` | espada 2M | 246 | Ferraria · Cavaleiro Sangrento |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_polearm_2h_questbloodelf_b_01.jpg" width="24" height="24" alt="Ímpeto do Cavaleiro Sangrento" /> | **Ímpeto do Cavaleiro Sangrento** *Blood Knight's Impetus* | `237847` | alabarda 2M | 246 | Ferraria · Cavaleiro Sangrento |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/mace_2h_blacksmithing_d_04_icon.jpg" width="24" height="24" alt="Misericórdia do Cavaleiro Sangrento" /> | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_blacksmithing_craftedoptional_reinforcedmetalplating_color01.jpg" width="20" height="20" alt="Misericórdia do Cavaleiro Sangrento" /> **Misericórdia do Cavaleiro Sangrento** *Blood Knight's Mercy* | `237848` | maça 2M | 246 | Ferraria · Cavaleiro Sangrento |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_axe_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Picareta do Competidor Talassiano" /> | **Picareta do Competidor Talassiano** *Thalassian Competitor's Pickaxe* | `237909` | machado 1M | 263 | Ferraria PvP |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_questbloodelf_b_02.jpg" width="24" height="24" alt="Faca do Competidor Talassiano" /> | **Faca do Competidor Talassiano** *Thalassian Competitor's Knife* | `237910` | adaga 1M | 263 | Ferraria PvP |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_mace_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Máxima do Competidor Talassiano" /> | **Máxima do Competidor Talassiano** *Thalassian Competitor's Maxim* | `237911` | maça 1M | 263 | Ferraria PvP |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_shield_1h_questbloodelf_b_01.jpg" width="24" height="24" alt="Baluarte do Competidor Talassiano" /> | **Baluarte do Competidor Talassiano** *Thalassian Competitor's Bulwark* | `237912` | escudo | 263 | Ferraria PvP |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_sword_2h_questbloodelf_b_01.jpg" width="24" height="24" alt="Montante do Competidor Talassiano" /> | **Montante do Competidor Talassiano** *Thalassian Competitor's Greatsword* | `237915` | espada 2M | 263 | Ferraria PvP |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_staff_2h_dungeonharronir_c_01.jpg" width="24" height="24" alt="Cajado-pique de Aln'hara" /> | **Cajado-pique de Aln'hara** *Aln'hara Pikestaff* | `245771` | cajado 2M | 246 | Escrivania · Aln'hara |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_offhand_1h_dungeonharronir_c_01.jpg" width="24" height="24" alt="Lanterna de Aln'hara" /> | **Lanterna de Aln'hara** *Aln'hara Lantern* | `245769` | mão secundária | 246 | **Escrivania** · Aln'hara |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_wand_1h_outdoorvoidelf_c_01.jpg" width="24" height="24" alt="Varinha do Tecencantos Talassiano" /> | **Varinha do Tecencantos Talassiano** *Thalassian Spellweaver's Wand* | `244178` | varinha | 201 | Encantamento |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_wand_24.jpg" width="24" height="24" alt="Grande Foco do Magíster" /> | **Grande Foco do Magíster** *Magister's Grand Focus* | `244179` | varinha | 246 | Encantamento |

> ✅ **Resolvido em 2026-11-06:** as famílias foram abertas no tooltip PT-BR e agora têm nome oficial e ID em [`craft_armas_s2.json`](craft_armas_s2.json:1) → `familias_ptbr_confirmadas_2026_11_06`.
>
> | Família EN | Nome PT-BR oficial | IDs |
> | :--- | :--- | :--- |
> | **Blood-Tempered** | Temperado em Sangue | `237917`–`237925` (armadura) + escudo `237920` |
> | **Dawnforged** | Albaforjado | `237926`, `237927`, `237928`, `237930`, `237931` |
> | **Primalforged** | Primeforjado | `237929`, `237932` |
> | **Thalassian Competitor's** | Competidor Talassiano | `237909`–`237916` (PvP, sobe a 263 em arena/BG/Modo de Guerra) |
> | **Aetherlume** | Aeterlúmen | `244744`–`244773` (Engenharia: cabeça, pulsos, pés) |
>
> **Ressalva importante:** essas peças são o **craft de entrada** (ilvl 165–263, "Vincula-se quando equipado"), não o craft com Centelha de Marés (246 → 331). Não somar as duas coisas na mesma conta.

### 7.2 Quais embelezamentos cabem em arma (e em qual arma)

| Embelezamento | "Usável com" (tooltip) | Cabe em |
| :--- | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_blacksmithing_weightstone_green.jpg" width="20" height="20" alt="Pedra Ritual do Caçador" /> **Pedra Ritual do Caçador** `273060` | Armas de **Ferraria** de Midnight | Todas as armas de Ferraria acima — **não** cabe no cajado de Escrivania nem na Lanterna |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_darkmoonsigil_hunt.jpg" width="20" height="20" alt="Signo de Negraluna: Sangue" /> **Signo de Negraluna: Sangue / Caçada / Podridão / Caos** `245872` `245876` `245878` `245874` | Armas **e** itens de mão secundária não embelezados | Qualquer arma da tabela, mais **Lanterna de Aln'hara** e escudos |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_leatherworking_armor_banding_green.jpg" width="20" height="20" alt="Vínculo de Esporos Primevos" /> **Vínculo de Esporos Primevos** `244608` | Armas e armaduras não embelezadas | Qualquer arma; também armadura |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_leatherworking_armor_banding_brown.jpg" width="20" height="20" alt="Elo Devorador" /> **Elo Devorador** `244675` | Armas e armaduras não embelezadas | Qualquer arma; também armadura |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_knife_1h_ulatek_d_01.jpg" width="20" height="20" alt="Presa Adornada" /> **Presa Adornada** `273069` | Maioria dos equipamentos não embelezados | Qualquer arma |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_111_goblintrikekeychain_ventureco.jpg" width="20" height="20" alt="Chaveiro da Sorte" /> **Chaveiro da Sorte** `248130` | Maioria dos equipamentos não embelezados | Remove o efeito de qualquer arma embelezada |

**Consequência direta:** a arma é o slot mais versátil para gastar um dos dois embelezamentos, porque aceita **todos** os reagentes de arma. Uma arma de Ferraria aceita 6 opções; a Lanterna de Escrivania aceita 6 menos a Pedra Ritual.

### 7.3 Encantamentos e gemas — documento separado

Encantamento e gema **não** interagem com o limite de embelezamento. Os catálogos completos estão em [`encantamentos_e_gemas_s2.md`](encantamentos_e_gemas_s2.md:1) e [`encantamentos_e_gemas_s2.json`](encantamentos_e_gemas_s2.json:1):

| Grupo | Quantidade | Observação |
| :--- | :-: | :--- |
| Encantamentos | **38 nomes / 76 IDs** | Cada encantamento existe em **duas qualidades** (dois IDs, mesmo nome no tooltip). Listar um ID só cobre metade do catálogo |
| Gemas | **72** | 4 famílias de cor × 2 níveis (278/295) + 4 diamantes em 2 níveis |
| **Aprimoramentos de perna** | **6 nomes / 12 IDs** | **Não são encantamento**: **Magilinha** (*Spellthread*, Alfaiataria) e **Kit de Armadura** (*Armor Kit*, Couraria) — ver seção 2.2 daquele documento |

> 📌 **Pernas não é slot vazio.** Ele usa **Magilinha de Arcanotrama** (`240154`/`240155` — +41 Intelecto e +4% de mana, Alfaiataria) ou **Magilinha de Seda de Fogo Solar** (`240094`/`240133`) ou um **Kit de Armadura** de Couraria. Nenhum deles é encantamento e nenhum conta no limite de embelezamento.

---

## 8. Aplicação ao projeto — o que os três specs craftam

| Spec | Peças craftadas usadas | Embelezamento recomendado | Cabe no limite de 2? |
| :--- | :--- | :--- | :-: |
| **Bruxo Demonologia** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_bracer_cloth_questbloodelf_b_01.jpg" width="18" height="18" alt="Braceletes do Mártir" /> Braceletes do Mártir `239648` + <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_offhand_1h_dungeonharronir_c_01.jpg" width="18" height="18" alt="Lanterna de Aln'hara" /> Lanterna de Aln'hara `245769` | 2× **Forro de Arcanotrama** nos pulsos | ✅ (1 efeito) |
| **Sacerdote das Sombras** | Braceletes do Mártir `239648` + Banda do Mártir `239649` + Lanterna `245769` | Forro de Arcanotrama nos pulsos | ✅ (1 efeito) |
| **Druida do Equilíbrio** | Defletores `244576` + Calçados `244569` + Lanterna `245769` | Forro de Arcanotrama nos pulsos + Forro nos pés | ✅ (2 efeitos) |

> **Regra de ouro para montar a build:** conte **efeitos**, não peças. Duas peças com Forro de Arcanotrama esgotam o limite; toda peça craftada adicional precisa entrar **sem** reagente de embelezamento — e continua valendo integralmente pelos atributos.

---

## 9. Divergências encontradas nesta rodada (corrigidas ou registradas)

| # | Divergência | Evidência | Ação |
| :-: | :--- | :--- | :--- |
| 1 | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_offhand_1h_dungeonharronir_c_01.jpg" width="20" height="20" alt="Lanterna de Aln'hara" /> **Lanterna de Aln'hara** estava marcada como `Craft (Alfaiataria)` nas três fichas de spec | Página do item `245769` no Wowhead: *“Midnight Inscription”*; a receita aparece na visão geral de **Escrivania** | **Corrigido** para Escrivania nas três fichas |
| 2 | **Pedra Ritual do Caçador** recomendada em mão secundária | Tooltip: “Usável com: **Armas de Ferraria** de Midnight” | Registrado em §5.1: só arma de Ferraria. Para a Lanterna, usar Signo de Negraluna |
| 3 | Nome PT da missiva de *Quickblade* | Tooltip PT-BR: **Gumepresto** | Guias que dizem “Lâmina Veloz” estão errados |
| 4 | “Não pode usar mais de 2 peças craftadas” | Tooltip: “Único-equipado: **Embelezado** (2)”; guias de craft confirmam que não há limite de peças | **Corrigido** — a regra é sobre efeitos |
| 5 | Duplicidade de IDs nos embelezamentos S2 (`273059`/`273060`, `273068`/`273069`, `273065`/`273066`) | Ambos os IDs respondem no tooltip com o mesmo nome | Registrado; diferença aparente é a dificuldade de receita (+15 vs +5) |

---

## 10. Pendências deste documento

| Item | Situação |
| :--- | :--- |
| **Nomes PT-BR das famílias de receita** | **RESOLVIDO**: *Blood-Tempered* = Temperado em Sangue, *Dawnforged* = Albaforjado, *Primalforged* = Primeforjado, *Courtly* = **Cortesão** (IDs 239668–239676), *Aetherlume* = Aeterlúmen. Todos auditados e confirmados no cliente oficial PT-BR |
| **Lista nominal de armas de fogo de Engenharia** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_engineering_scope_color3.jpg" width="20" height="20" alt="Olho de Cobra Enrolado" /> **RESOLVIDO em 2026-11-06**: A seção "Reagente para (3)" do `273062` (Olho de Cobra Enrolado) foi raspada com sucesso via Firecrawl. As 3 armas fabricadas por Engenharia são: `268475` <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_firearm_2h_engineering_c_01_blue.jpg" width="20" height="20" alt="Quebra-coco Evinúcleo" /> **Quebra-coco Evinúcleo** (201, Azul, Eng 35), `268477` <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_firearm_2h_raidmidnight_d_01.jpg" width="20" height="20" alt="P.O.U. x3" /> **P.O.U. x3** (246, Épica com Centelha, teto 331, Eng 90) e `268479` <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_firearm_2h_undergroundquest_b_01.jpg" width="20" height="20" alt="Rifle do Competidor Talassiano" /> **Rifle do Competidor Talassiano** (263, Verde PvP, Eng 60). |
| **Duplicidade de IDs de embelezamento S2** | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_blacksmithing_weightstone_green.jpg" width="20" height="20" alt="Pedra Ritual do Caçador" /> **Resolvido em 2026-11-06**: os pares têm efeito **idêntico** e diferem só na dificuldade da receita — `273059`/`273065`/`273068` = **+15**; `273060`/`273066`/`273069` = **+5**. São o par de dificuldade do mesmo reagente |
| **Chaveiro da Sorte: “+1 de Brilho”** | Efeito confirmado em guia de craft, não em tooltip — conferir no jogo |
| **Teto 318 vs 331 por qualidade** | A faixa “318–331” do craft mítico depende da qualidade 1–5; falta a tabela de qualidade por rank |

---

## Fontes

- **Wowhead — Professions System Overview** (patch 12.1.5): tag `Unique-Equipped: Embellished (2)`, tabela de embelezamentos por profissão e por slot, cristas e centelhas.
- **Wowhead — Midnight Profession Overview** de Ferraria, Couraria, Alfaiataria, Joalheria, Escrivania e Engenharia: inventário de receitas por slot.
- **Wowhead — tooltips oficiais** (`nether.wowhead.com/tooltip/item`, `locale=8`): nomes PT-BR, níveis, linha “Usável com”, linha “Único-equipado: Embelezado (2)” e efeitos numéricos.
- **Method — List of All Midnight Embellishments** e **Midnight Missives for Crafted Gear**: catálogo cruzado de embelezamentos e missivas.
- **LevelUpper — Crafted Gear Guide** e **Best Crafted Gear & Embellishments (S2)**: teto 331, custo em Centelhas e a confirmação de que não existe limite de peças craftadas.
- **Auditoria interna:** [`tools/auditar_craft.js`](tools/auditar_craft.js:1) consultou **91 IDs** em dois locales e gravou [`craft_sistemas_s2.json`](craft_sistemas_s2.json:1) com **91 acertos e 0 falhas**.
