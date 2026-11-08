# Encantamentos e Gemas da Temporada 2 — catálogo completo com nome oficial

**Expansão:** World of Warcraft: Midnight
**Patch:** 12.1.5 — A Maldição de Ula'tek (*The Curse of Ula'tek*)
**Dados brutos:** [`encantamentos_e_gemas_s2.json`](encantamentos_e_gemas_s2.json:1)
**Descoberta por varredura:** [`tools/varrer_itens.js`](tools/varrer_itens.js:1) → [`varredura_itens.json`](varredura_itens.json:1)
**Geração deste documento:** [`tools/gerar_doc_encantamentos_gemas.js`](tools/gerar_doc_encantamentos_gemas.js:1)

> **Regra de nomenclatura deste documento.** Todo nome em negrito é **cópia literal do tooltip oficial PT-BR** (`nether.wowhead.com/tooltip/item`, `locale=8`), incluindo o sufixo de slot que o cliente imprime — `- Torso`, `- Elmo`, `- Ombros`, `- Botas`, `- Anel`, `- Arma`. Nada aqui é tradução livre do projeto. O nome em inglês aparece em *itálico* apenas como identificador secundário.

---

## 0. Como estes dados foram obtidos (e por que não bastava o guia)

As páginas de guia do Wowhead listam só parte das receitas. A varredura fechou a lacuna consultando **faixas de ID** no tooltip oficial:

| Faixa varrida | O que ela contém | Resultado |
| :--- | :--- | :--- |
| **243700 – 244037** | Encantamentos de Midnight (todas as qualidades) | 38 encantamentos em **76 IDs** (2 qualidades por encantamento) |
| **240860 – 240990** | Gemas lapidadas de Midnight | 72 gemas (inclui as duas qualidades de nível) |
| **273065 – 273080** | Embelezamentos e encantamento novos da T2 | `Rito dos Hash'ey` e reagentes já catalogados |

Total conferido: **38 encantamentos** (76 IDs) e **72 gemas**, com **0 falhas** de consulta. Todas as leituras rodaram no endpoint gratuito — zero crédito de Firecrawl.

> ⚠️ **Por que cada encantamento aparece com dois IDs.** A Temporada 2 mantém a estrutura de **qualidade** do encantamento: a mesma receita existe em duas versões (IDs consecutivos, mesmo nome no tooltip). As duas encantam igual; mudam os materiais e o custo. Quem lista só um ID está listando metade do catálogo — foi exatamente o erro da primeira versão deste documento.

---

## 1. Encantamentos por slot — o catálogo inteiro

### 1.1 Cabeça (`- Elmo`)

| Encantamento (nome oficial PT-BR) | IDs por qualidade | Nome em inglês | Efeito exato do tooltip |
| :--- | :--- | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_green.jpg" width="20" height="20" alt="Encantamento da Bênção da Velocidade - Elmo" /> **Encantamento da Bênção da Velocidade - Elmo** | `243978` · `243979` | *Enchant Helm - Blessing of Speed* | Encanta permanentemente um elmo com a Bênção da Velocidade, aumentando em 13 a Velocidade. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Bênção da Velocidade Potencializada - Elmo" /> **Encantamento da Bênção da Velocidade Potencializada - Elmo** | `243980` · `243981` | *Enchant Helm - Empowered Blessing of Speed* | Encanta permanentemente um elmo com a Bênção da Velocidade Potencializada, aumentando em 22 a Velocidade. Também concede 1 de carga de habilidades de Pilotagem Aérea sempre que você derrota um inimigo em ambientes externos em uma área de Midnight, uma vez a cada 30 s. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_green.jpg" width="20" height="20" alt="Encantamento da Runa da Evasão - Elmo" /> **Encantamento da Runa da Evasão - Elmo** | `244004` · `244005` | *Enchant Helm - Rune of Avoidance* | Encanta permanentemente um elmo com a Runa da Evasão, aumentando em 22 a Evasão. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Runa da Evasão Potencializada - Elmo" /> **Encantamento da Runa da Evasão Potencializada - Elmo** | `244006` · `244007` | *Enchant Helm - Empowered Rune of Avoidance* | Encanta permanentemente um elmo com a Runa da Evasão Potencializada, aumentando em 37 a Evasão. Também concede a você um rompante de Velocidade de Movimento sempre que você derrotar um inimigo a céu aberto em uma área de Midnight, uma vez a cada 60 s. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_green.jpg" width="20" height="20" alt="Encantamento de Bagata Sorvedora - Elmo" /> **Encantamento de Bagata Sorvedora - Elmo** | `243948` · `243949` | *Enchant Helm - Hex of Leeching* | Encanta permanentemente um elmo com a Bagata Sorvedora, aumentando em 33 o Sorver. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento de Bagata Sorvedora Potencializada - Elmo" /> **Encantamento de Bagata Sorvedora Potencializada - Elmo** | `243950` · `243951` | *Enchant Helm - Empowered Hex of Leeching* | Encanta permanentemente um elmo com a Bagata Sorvedora Potencializada, aumentando em 55 o Sorver. Também cura 3% dos seus pontos de vida sempre que você derrotar um inimigo a céu aberto em uma área de Midnight, uma vez a cada 5 s. |

### 1.2 Ombros (`- Ombros`)

| Encantamento (nome oficial PT-BR) | IDs por qualidade | Nome em inglês | Efeito exato do tooltip |
| :--- | :--- | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_green.jpg" width="20" height="20" alt="Encantamento da Graça da Natureza - Ombros" /> **Encantamento da Graça da Natureza - Ombros** | `243988` · `243989` | *Enchant Shoulders - Nature's Grace* | Encanta permanentemente ombreiras com a Graça da Natureza, aumentando em 67 a Evasão. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Graça de Amirdrassil - Ombros" /> **Encantamento da Graça de Amirdrassil - Ombros** | `243990` · `243991` | *Enchant Shoulders - Amirdrassil's Grace* | Encanta permanentemente ombreiras com a Graça de Amirdrassil, aumentando em 111 a Evasão. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Rapidez de Akil'zon - Ombros" /> **Encantamento da Rapidez de Akil'zon - Ombros** | `243962` · `243963` | *Enchant Shoulders - Akil'zon's Swiftness* | Encanta permanentemente ombreiras com a Rapidez de Akil'zon, aumentando em 65 a Velocidade. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Recomposição de Luaprata - Ombros" /> **Encantamento da Recomposição de Luaprata - Ombros** | `244020` · `244021` | *Enchant Shoulders - Silvermoon's Mending* | Encanta permanentemente ombreiras com a Recomposição de Luaprata, aumentando em 166 o Sorver. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_green.jpg" width="20" height="20" alt="Encantamento da Recuperação Talassiana - Ombros" /> **Encantamento da Recuperação Talassiana - Ombros** | `244018` · `244019` | *Enchant Shoulders - Thalassian Recovery* | Encanta permanentemente ombreiras com a Recuperação Talassiana, aumentando em 99 o Sorver. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_green.jpg" width="20" height="20" alt="Encantamento do Voo da Águia - Ombros" /> **Encantamento do Voo da Águia - Ombros** | `243960` · `243961` | *Enchant Shoulders - Flight of the Eagle* | Encanta permanentemente ombreiras com o Voo da Águia, aumentando em 39 a Velocidade. |

### 1.3 Peitoral (`- Torso`)

| Encantamento (nome oficial PT-BR) | IDs por qualidade | Nome em inglês | Efeito exato do tooltip |
| :--- | :--- | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Marca da Alma do Mundo - Torso" /> **Encantamento da Marca da Alma do Mundo - Torso** | `243976` · `243977` | *Enchant Chest - Mark of the Worldsoul* | Encanta permanentemente uma armadura de torso com a Marca da Alma do Mundo, aumentando em 50 seu Atributo Primário. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Marca de Nalorakk - Torso" /> **Encantamento da Marca de Nalorakk - Torso** | `243946` · `243947` | *Enchant Chest - Mark of Nalorakk* | Encanta permanentemente uma armadura de torso com a Marca de Nalorakk, aumentando em 40 a Força e em 116 o Vigor. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Marca do Guardirraiz - Torso" /> **Encantamento da Marca do Guardirraiz - Torso** | `243974` · `243975` | *Enchant Chest - Mark of the Rootwarden* | Encanta permanentemente uma armadura de torso com a Marca do Guardirraiz, aumentando em 40 a Agilidade e em 15 a Velocidade. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Marca do Magíster - Torso" /> **Encantamento da Marca do Magíster - Torso** | `244002` · `244003` | *Enchant Chest - Mark of the Magister* | Encanta permanentemente uma armadura de torso com a Marca do Magíster, aumentando em 40 o Intelecto e em 5 o total de Mana. |

### 1.4 Pés (`- Botas`)

| Encantamento (nome oficial PT-BR) | IDs por qualidade | Nome em inglês | Efeito exato do tooltip |
| :--- | :--- | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Caça do Andarilho - Botas" /> **Encantamento da Caça do Andarilho - Botas** | `244008` · `244009` | *Enchant Boots - Farstrider's Hunt* | Encanta permanentemente um par de botas com a Caça do Andarilho, aumentando em 11 a Velocidade e em 232 o Vigor. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento das Raízes de Shaladrassil - Botas" /> **Encantamento das Raízes de Shaladrassil - Botas** | `243982` · `243983` | *Enchant Boots - Shaladrassil's Roots* | Encanta permanentemente um par de botas com a Raízes de Shaladrassil, aumentando em 28 o Sorver e em 232 o Vigor. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento de Destreza do Lince - Botas" /> **Encantamento de Destreza do Lince - Botas** | `243952` · `243953` | *Enchant Boots - Lynx's Dexterity* | Encanta permanentemente um par de botas com a Destreza do Lince, aumentando em 19 a Evasão e em 232 o Vigor. |

### 1.5 Anel (`- Anel`)

| Encantamento (nome oficial PT-BR) | IDs por qualidade | Nome em inglês | Efeito exato do tooltip |
| :--- | :--- | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_green.jpg" width="20" height="20" alt="Encantamento da Aceleração Talassiana - Anel" /> **Encantamento da Aceleração Talassiana - Anel** | `244010` · `244011` | *Enchant Ring - Thalassian Haste* | Encanta permanentemente um anel com a Aceleração Talassiana, aumentando em 24 a Aceleração. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_green.jpg" width="20" height="20" alt="Encantamento da Cólera da Natureza - Anel" /> **Encantamento da Cólera da Natureza - Anel** | `243984` · `243985` | *Enchant Ring - Nature's Wrath* | Encanta permanentemente um anel com a Cólera da Natureza, aumentando em 24 o Acerto Crítico. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Diligência de Luaprata - Anel" /> **Encantamento da Diligência de Luaprata - Anel** | `244014` · `244015` | *Enchant Ring - Silvermoon's Alacrity* | Encanta permanentemente um anel com a Diligência de Luaprata, aumentando em 29 a Aceleração. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Fúria da Natureza - Anel" /> **Encantamento da Fúria da Natureza - Anel** | `243986` · `243987` | *Enchant Ring - Nature's Fury* | Encanta permanentemente um anel com a Fúria da Natureza, aumentando em 29 o Acerto Crítico. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento da Tenacidade de Luaprata - Anel" /> **Encantamento da Tenacidade de Luaprata - Anel** | `244016` · `244017` | *Enchant Ring - Silvermoon's Tenacity* | Encanta permanentemente um anel com a Tenacidade de Luaprata, aumentando em 29 a Versatilidade. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_green.jpg" width="20" height="20" alt="Encantamento da Versatilidade Talassiana - Anel" /> **Encantamento da Versatilidade Talassiana - Anel** | `244012` · `244013` | *Enchant Ring - Thalassian Versatility* | Encanta permanentemente um anel com a Versatilidade Talassiana, aumentando em 24 a Versatilidade. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_green.jpg" width="20" height="20" alt="Encantamento de Maestria Amani - Anel" /> **Encantamento de Maestria Amani - Anel** | `243954` · `243955` | *Enchant Ring - Amani Mastery* | Encanta permanentemente um anel com Maestria Amani, aumentando em 24 a Maestria. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento de Maestria de Zul'jin - Anel" /> **Encantamento de Maestria de Zul'jin - Anel** | `243958` · `243959` | *Enchant Ring - Zul'jin's Mastery* | Encanta permanentemente um anel com Maestria de Zul'jin, aumentando em 29 a Maestria. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_blue.jpg" width="20" height="20" alt="Encantamento de Olhos da Águia - Anel" /> **Encantamento de Olhos da Águia - Anel** | `243956` · `243957` | *Enchant Ring - Eyes of the Eagle* | Encanta permanentemente um anel com Olhos da Águia, aumentando em 2% a eficácia do Acerto Crítico. |

### 1.6 Arma (`- Arma`)

| Encantamento (nome oficial PT-BR) | IDs por qualidade | Nome em inglês | Efeito exato do tooltip |
| :--- | :--- | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_purple.jpg" width="20" height="20" alt="Encantamento da Acuidade dos Ren'dorei - Arma" /> **Encantamento da Acuidade dos Ren'dorei - Arma** | `244028` · `244029` | *Enchant Weapon - Acuity of the Ren'dorei* | Encanta permanentemente uma arma com a Acuidade dos Ren'dorei, fazendo seus feitiços e habilidades lhe conferirem Poder do Caos, concedendo Atributo primário de 67 por 15 s. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_purple.jpg" width="20" height="20" alt="Encantamento da Maestria Arcana - Arma" /> **Encantamento da Maestria Arcana - Arma** | `244030` · `244031` | *Enchant Weapon - Arcane Mastery* | Encanta permanentemente uma arma com Maestria Arcana, fazendo seus feitiços e habilidades lhe concederem Percepção Genial, aumentando em 124 sua Maestria por 15 s. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_purple.jpg" width="20" height="20" alt="Encantamento das Chamas dos Sin'dorei - Arma" /> **Encantamento das Chamas dos Sin'dorei - Arma** | `244026` · `244027` | *Enchant Weapon - Flames of the Sin'dorei* | Encanta permanentemente uma arma com as Chamas dos Sin'dorei, fazendo seus feitiços e habilidades às vezes queimarem o seu alvo. Isso causa (1 * (2456)) de dano de Fogo ao longo de 10 s e depois detona, causando mais (1 * 5220) de dano de Fogo dividido entre inimigos próximos. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_purple.jpg" width="20" height="20" alt="Encantamento de Berço da Alma do Mundo - Arma" /> **Encantamento de Berço da Alma do Mundo - Arma** | `243996` · `243997` | *Enchant Weapon - Worldsoul Cradle* | Encanta permanentemente uma arma com o Berço da Alma do Mundo. Suas habilidades e feitiços de cura às vezes concedem ao seu alvo uma barreira que absorve os próximos (1 * 12525) de dano. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_purple.jpg" width="20" height="20" alt="Encantamento de Égide da Alma do Mundo - Arma" /> **Encantamento de Égide da Alma do Mundo - Arma** | `243998` · `243999` | *Enchant Weapon - Worldsoul Aegis* | Encanta permanentemente uma arma com a Égide da Alma do Mundo. Ao receber dano, a Égide tem chance de conceder a você uma barreira que protege contra os próximos 14039 de dano. Quando se esgota, a barreira irrompe, causando 2776 de dano de Natureza dividido entre os inimigos próximos. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_purple.jpg" width="20" height="20" alt="Encantamento de Força de Halazzi - Arma" /> **Encantamento de Força de Halazzi - Arma** | `243968` · `243969` | *Enchant Weapon - Strength of Halazzi* | Encanta permanentemente uma arma com a Força de Halazzi. Seus danos às vezes chamam o loa para talhar o seu alvo, fazendo-os sangrar e causando (1 * 1893) de dano ao longo de 18 s. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_purple.jpg" width="20" height="20" alt="Encantamento de Precisão de Jan'alai - Arma" /> **Encantamento de Precisão de Jan'alai - Arma** | `243970` · `243971` | *Enchant Weapon - Jan'alai's Precision* | Encanta permanentemente uma arma com Precisão de Jan'alai, fazendo seus feitiços e habilidades às vezes concederem Precisão do Falcodrago, aumentando em 124 o seu Acerto Crítico por 15 s. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_purple.jpg" width="20" height="20" alt="Encantamento de Raiva Incontrolada - Arma" /> **Encantamento de Raiva Incontrolada - Arma** | `243972` · `243973` | *Enchant Weapon - Berserker's Rage* | Encanta permanentemente uma arma com Raiva Incontrolada, fazendo seus feitiços e habilidades concederem Foco Frenético, aumentando em 124 a sua Aceleração por 15 s. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_purple.jpg" width="20" height="20" alt="Encantamento de Rito dos Hash'ey - Arma" /> **Encantamento de Rito dos Hash'ey - Arma** | `273071` · `273072` | *Enchant Weapon - Rite of the Hash'ey* | Encanta permanentemente uma arma com Rito dos Hash'ey, fazendo seus feitiços e habilidades concederem Poder dos Hash'ey, concedendo 120 de um atributo secundário aleatório por 15 s e favorecendo seu atributo secundário mais alto quando você está com mais de 80% dos pontos de vida. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_enchantedvellum_purple.jpg" width="20" height="20" alt="Encantamento de Tenacidade da Alma do Mundo - Arma" /> **Encantamento de Tenacidade da Alma do Mundo - Arma** | `244000` · `244001` | *Enchant Weapon - Worldsoul Tenacity* | Encanta permanentemente uma arma com a Tenacidade da Alma do Mundo. Seus feitiços e habilidades concedem a você a Tenacidade da Natureza, aumentando em 124 a sua Versatilidade por 15 s. |

---

## 2. Slots que NÃO têm encantamento na temporada

A varredura de 243947 a 244037 **não encontrou** nenhum `Enchant Wrists`, `Enchant Hands`, `Enchant Legs` nem `Enchant Cloak` de Midnight. Na prática, a temporada encanta apenas **cabeça, ombros, peitoral, pés, dois anéis e arma**.

| Slot | Tem encantamento na T2? | Observação |
| :--- | :-: | :--- |
| Cabeça | ✅ | 6 opções |
| Ombros | ✅ | 6 opções |
| Peitoral | ✅ | 4 opções |
| Pés | ✅ | 3 opções |
| Anel | ✅ | 9 opções — vale nos **dois** anéis |
| Arma | ✅ | 10 opções |
| **Pernas** | ❌ encantamento | Mas o slot **não fica vazio**: usa **Spellthread** (Alfaiataria) ou **Kit de Armadura** (Couraria) — ver 2.2 |
| Pulsos, mãos, capa, escudo, mão secundária | ❌ | Nenhuma receita de Midnight na faixa varrida |

> ⚠️ **Pendência registrada:** confirmar no jogo se pulsos, mãos e capa realmente ficaram sem encantamento nesta temporada, ou se existe receita fora da faixa varrida.

### 2.1 Encantamento de ferramenta de profissão

Fora do escopo de combate, mas catalogados: `Encantamento de Percepção Amani - Ferramenta`, `Encantamento de Economia Amani - Ferramenta`, `Encantamento de Finura Haranir - Ferramenta`, `Encantamento de Multicriação Haranir - Ferramenta`, `Encantamento de Destreza Sin'dorei - Ferramenta` e `Encantamento de Engenhosidade Ren'dorei - Ferramenta`.

### 2.2 Aprimoramentos permanentes de perna — não são encantamento

Este é o caso que quase todo guia erra: **pernas não recebem encantamento**, recebem um **aprimoramento permanente** criado por outra profissão. São itens consumíveis com `Use:`, aplicados direto na perna, e **não** passam pela perícia Encantamento. Também existem em duas qualidades.

| Aprimoramento (nome oficial PT-BR) | IDs por qualidade | Profissão | Nome em inglês | Efeito exato do tooltip |
| :--- | :--- | :--- | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_tailoring_spellthread_violet_spellthread.jpg" width="20" height="20" alt="Magilinha de Arcanotrama" /> **Magilinha de Arcanotrama** | `240154` · `240155` | Alfaiataria | *Arcanoweave Spellthread* | Aplica Magilinha de Arcanotrama às suas perneiras, aumentando em 41 o Intelecto delas permanentemente e em 4% o máximo de pontos de mana do usuário. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_tailoring_spellthread_blue_spellthread.jpg" width="20" height="20" alt="Magilinha de Linho Brilhante" /> **Magilinha de Linho Brilhante** | `240156` · `240157` | Alfaiataria | *Bright Linen Spellthread* | Aplica Magilinha de Linho Brilhante às suas perneiras, aumentando em 24 o Intelecto delas permanentemente. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_tailoring_spellthread_orange_spellthread.jpg" width="20" height="20" alt="Magilinha de Seda de Fogo Solar" /> **Magilinha de Seda de Fogo Solar** | `240094` · `240133` | Alfaiataria | *Sunfire Silk Spellthread* | Aplica Magilinha de Seda de Fogo Solar às suas perneiras, aumentando em 41 o Intelecto e em 115 o Vigor delas permanentemente. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_leatherworking_standart_armor_kit.jpg" width="20" height="20" alt="Kit de Armadura do Batedor Talassiano" /> **Kit de Armadura do Batedor Talassiano** | `244644` · `244645` | Couraria | *Thalassian Scout Armor Kit* | Aplica um Kit de Armadura do Batedor Talassiano à sua armadura de perna, concedendo mais 24 de Agilidade ou Força permanentemente. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_leatherworking_amani_armor_kit.jpg" width="20" height="20" alt="Kit de Armadura do Caçador da Floresta" /> **Kit de Armadura do Caçador da Floresta** | `244640` · `244641` | Couraria | *Forest Hunter's Armor Kit* | Aplica um Kit de Armadura do Caçador da Floresta à sua armadura de perna, concedendo mais 41 de Agilidade ou Força permanentemente. Além disso, o item ganha 115 de Vigor. |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_leatherworking_thalassian_amor_kit.jpg" width="20" height="20" alt="Kit de Armadura do Cavaleiro Sangrento" /> **Kit de Armadura do Cavaleiro Sangrento** | `244642` · `244643` | Couraria | *Blood Knight's Armor Kit* | Aplica um Kit de Armadura do Cavaleiro Sangrento à sua armadura de perna, concedendo mais 41 de Agilidade ou Força permanentemente. Além disso, o item ganha 27 de Armadura. |

> **Consequência para o cálculo:** o slot de pernas tem **duas** famílias de aprimoramento — **Magilinha** (Alfaiataria, para conjurador: Intelecto e mana) e **Kit de Armadura** (Couraria, para Agilidade/Força e defesa) — e nenhuma é encantamento. Contar pernas como "slot sem aprimoramento" subestima o personagem.

---

## 3. Gemas — estrutura da temporada

Duas coisas mudam o cálculo em relação a temporadas anteriores:

1. **Cada gema de cor existe em dois níveis:** **278** e **295**. O nível 295 dá mais atributo e é o que interessa em conteúdo endgame.
2. **O prefixo `Impecável`** (`Flawless`) marca a versão de topo: soma **23** pontos de atributo no nível 295 contra **17** da versão comum. Gema pura (um atributo só) dá `+17`; gema dupla dá `+16` no atributo da cor e `+7` no segundo.

### 3.1 Diamante de Eversong (`Unique-Equipped: Thalassian Diamond (1)`)

Só **um** pode ser usado, e ele é prismático (entra em qualquer encaixe). No PT-BR o nome carrega `Diamante do Canto Eterno`.

| Diamante (nome oficial PT-BR) | ID | Nível | Atributos |
| :--- | --: | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_epic_gem_cut_pink.jpg" width="20" height="20" alt="Diamante do Canto Eterno Estoico" /> **Diamante do Canto Eterno Estoico** | `240970` | 278 | +18 de Atributo Primário e +10 de Armadura |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_epic_gem_cut_pink.jpg" width="20" height="20" alt="Diamante do Canto Eterno Estoico" /> **Diamante do Canto Eterno Estoico** | `240971` | 295 | +23 de Atributo Primário e +13 de Armadura |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_epic_gem_cut_green.jpg" width="20" height="20" alt="Diamante do Canto Eterno Indecifrável" /> **Diamante do Canto Eterno Indecifrável** | `240982` | 278 | +26 de Atributo Primário |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_epic_gem_cut_green.jpg" width="20" height="20" alt="Diamante do Canto Eterno Indecifrável" /> **Diamante do Canto Eterno Indecifrável** | `240983` | 295 | +32 de Atributo Primário |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_epic_gem_cut_orange.jpg" width="20" height="20" alt="Diamante do Canto Eterno Poderoso" /> **Diamante do Canto Eterno Poderoso** | `240966` | 278 | +18 de Atributo Primário e +0,15% de eficácia de acerto crítico por cor de gema de Midnight única |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_epic_gem_cut_orange.jpg" width="20" height="20" alt="Diamante do Canto Eterno Poderoso" /> **Diamante do Canto Eterno Poderoso** | `240967` | 295 | +23 de Atributo Primário e +0,15% de eficácia de acerto crítico por cor de gema de Midnight única |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_epic_gem_cut_blue.jpg" width="20" height="20" alt="Diamante do Canto Eterno Telúrico" /> **Diamante do Canto Eterno Telúrico** | `240968` | 278 | +18 de Atributo Primário e +1% de Máximo de Mana por cor de gema de Midnight única |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_epic_gem_cut_blue.jpg" width="20" height="20" alt="Diamante do Canto Eterno Telúrico" /> **Diamante do Canto Eterno Telúrico** | `240969` | 295 | +23 de Atributo Primário e +1% de Máximo de Mana por cor de gema de Midnight única |

> O bônus secundário dos diamantes escala com a **quantidade de cores diferentes de gema de Midnight** que você tem encaixadas. Isso significa que girar as gemas de cor para cobrir as quatro cores aumenta o valor do diamante.

### 3.2 Peridot — a gema cujo atributo de cor é **Aceleração**

| Gema (nome oficial PT-BR) | ID | Nível | Atributos |
| :--- | --: | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_fire_green.jpg" width="20" height="20" alt="Peridoto Mortal" /> **Peridoto Mortal** | `240857` | 278 | +11 de Aceleração e +4 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_fire_green.jpg" width="20" height="20" alt="Peridoto Mortal" /> **Peridoto Mortal** | `240858` | 295 | +12 de Aceleração e +5 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_fire_green.jpg" width="20" height="20" alt="Peridoto Mortal Impecável" /> **Peridoto Mortal Impecável** | `240889` | 278 | +14 de Aceleração e +6 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_fire_green.jpg" width="20" height="20" alt="Peridoto Mortal Impecável" /> **Peridoto Mortal Impecável** | `240890` | 295 | +16 de Aceleração e +7 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_void_green.jpg" width="20" height="20" alt="Peridoto Primoroso" /> **Peridoto Primoroso** | `240859` | 278 | +11 de Aceleração e +4 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_void_green.jpg" width="20" height="20" alt="Peridoto Primoroso" /> **Peridoto Primoroso** | `240860` | 295 | +12 de Aceleração e +5 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_void_green.jpg" width="20" height="20" alt="Peridoto Primoroso Impecável" /> **Peridoto Primoroso Impecável** | `240891` | 278 | +14 de Aceleração e +6 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_void_green.jpg" width="20" height="20" alt="Peridoto Primoroso Impecável" /> **Peridoto Primoroso Impecável** | `240892` | 295 | +16 de Aceleração e +7 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_nature_green.jpg" width="20" height="20" alt="Peridoto Veloz" /> **Peridoto Veloz** | `240855` | 278 | +12 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_nature_green.jpg" width="20" height="20" alt="Peridoto Veloz" /> **Peridoto Veloz** | `240856` | 295 | +13 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_nature_green.jpg" width="20" height="20" alt="Peridoto Veloz Impecável" /> **Peridoto Veloz Impecável** | `240887` | 278 | +15 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_nature_green.jpg" width="20" height="20" alt="Peridoto Veloz Impecável" /> **Peridoto Veloz Impecável** | `240888` | 295 | +17 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_frost_green.jpg" width="20" height="20" alt="Peridoto Versátil" /> **Peridoto Versátil** | `240861` | 278 | +11 de Aceleração e +4 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_frost_green.jpg" width="20" height="20" alt="Peridoto Versátil" /> **Peridoto Versátil** | `240862` | 295 | +12 de Aceleração e +5 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_frost_green.jpg" width="20" height="20" alt="Peridoto Versátil Impecável" /> **Peridoto Versátil Impecável** | `240893` | 278 | +14 de Aceleração e +6 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_frost_green.jpg" width="20" height="20" alt="Peridoto Versátil Impecável" /> **Peridoto Versátil Impecável** | `240894` | 295 | +16 de Aceleração e +7 de Versatilidade |

### 3.3 Garnet — a gema cujo atributo de cor é **Acerto Crítico**

| Gema (nome oficial PT-BR) | ID | Nível | Atributos |
| :--- | --: | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_fire_red.jpg" width="20" height="20" alt="Granada Mortal" /> **Granada Mortal** | `240871` | 278 | +12 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_fire_red.jpg" width="20" height="20" alt="Granada Mortal" /> **Granada Mortal** | `240872` | 295 | +13 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_fire_red.jpg" width="20" height="20" alt="Granada Mortal Impecável" /> **Granada Mortal Impecável** | `240903` | 278 | +15 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_fire_red.jpg" width="20" height="20" alt="Granada Mortal Impecável" /> **Granada Mortal Impecável** | `240904` | 295 | +17 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_void_red.jpg" width="20" height="20" alt="Granada Primorosa" /> **Granada Primorosa** | `240875` | 278 | +11 de Acerto Crítico e +4 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_void_red.jpg" width="20" height="20" alt="Granada Primorosa" /> **Granada Primorosa** | `240876` | 295 | +12 de Acerto Crítico e +5 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_void_red.jpg" width="20" height="20" alt="Granada Primorosa Impecável" /> **Granada Primorosa Impecável** | `240907` | 278 | +14 de Acerto Crítico e +6 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_void_red.jpg" width="20" height="20" alt="Granada Primorosa Impecável" /> **Granada Primorosa Impecável** | `240908` | 295 | +16 de Acerto Crítico e +7 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_nature_red.jpg" width="20" height="20" alt="Granada Veloz" /> **Granada Veloz** | `240873` | 278 | +11 de Acerto Crítico e +4 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_nature_red.jpg" width="20" height="20" alt="Granada Veloz" /> **Granada Veloz** | `240874` | 295 | +12 de Acerto Crítico e +5 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_nature_red.jpg" width="20" height="20" alt="Granada Veloz Impecável" /> **Granada Veloz Impecável** | `240905` | 278 | +14 de Acerto Crítico e +6 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_nature_red.jpg" width="20" height="20" alt="Granada Veloz Impecável" /> **Granada Veloz Impecável** | `240906` | 295 | +16 de Acerto Crítico e +7 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_frost_red.jpg" width="20" height="20" alt="Granada Versátil" /> **Granada Versátil** | `240877` | 278 | +11 de Acerto Crítico e +4 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_frost_red.jpg" width="20" height="20" alt="Granada Versátil" /> **Granada Versátil** | `240878` | 295 | +12 de Acerto Crítico e +5 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_frost_red.jpg" width="20" height="20" alt="Granada Versátil Impecável" /> **Granada Versátil Impecável** | `240909` | 278 | +14 de Acerto Crítico e +6 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_frost_red.jpg" width="20" height="20" alt="Granada Versátil Impecável" /> **Granada Versátil Impecável** | `240910` | 295 | +16 de Acerto Crítico e +7 de Versatilidade |

### 3.4 Amethyst — a gema cujo atributo de cor é **Maestria**

| Gema (nome oficial PT-BR) | ID | Nível | Atributos |
| :--- | --: | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_fire_purple.jpg" width="20" height="20" alt="Ametista Mortal" /> **Ametista Mortal** | `240865` | 278 | +11 de Maestria e +4 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_fire_purple.jpg" width="20" height="20" alt="Ametista Mortal" /> **Ametista Mortal** | `240866` | 295 | +12 de Maestria e +5 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_fire_purple.jpg" width="20" height="20" alt="Ametista Mortal Impecável" /> **Ametista Mortal Impecável** | `240897` | 278 | +14 de Maestria e +6 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_fire_purple.jpg" width="20" height="20" alt="Ametista Mortal Impecável" /> **Ametista Mortal Impecável** | `240898` | 295 | +16 de Maestria e +7 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_void_purple.jpg" width="20" height="20" alt="Ametista Primorosa" /> **Ametista Primorosa** | `240863` | 278 | +12 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_void_purple.jpg" width="20" height="20" alt="Ametista Primorosa" /> **Ametista Primorosa** | `240864` | 295 | +13 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_void_purple.jpg" width="20" height="20" alt="Ametista Primorosa Impecável" /> **Ametista Primorosa Impecável** | `240895` | 278 | +15 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_void_purple.jpg" width="20" height="20" alt="Ametista Primorosa Impecável" /> **Ametista Primorosa Impecável** | `240896` | 295 | +17 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_nature_purple.jpg" width="20" height="20" alt="Ametista Veloz" /> **Ametista Veloz** | `240867` | 278 | +11 de Maestria e +4 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_nature_purple.jpg" width="20" height="20" alt="Ametista Veloz" /> **Ametista Veloz** | `240868` | 295 | +12 de Maestria e +5 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_nature_purple.jpg" width="20" height="20" alt="Ametista Veloz Impecável" /> **Ametista Veloz Impecável** | `240899` | 278 | +14 de Maestria e +6 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_nature_purple.jpg" width="20" height="20" alt="Ametista Veloz Impecável" /> **Ametista Veloz Impecável** | `240900` | 295 | +16 de Maestria e +7 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_frost_purple.jpg" width="20" height="20" alt="Ametista Versátil" /> **Ametista Versátil** | `240869` | 278 | +11 de Maestria e +4 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_frost_purple.jpg" width="20" height="20" alt="Ametista Versátil" /> **Ametista Versátil** | `240870` | 295 | +12 de Maestria e +5 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_frost_purple.jpg" width="20" height="20" alt="Ametista Versátil Impecável" /> **Ametista Versátil Impecável** | `240901` | 278 | +14 de Maestria e +6 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_frost_purple.jpg" width="20" height="20" alt="Ametista Versátil Impecável" /> **Ametista Versátil Impecável** | `240902` | 295 | +16 de Maestria e +7 de Versatilidade |

### 3.5 Lapis — a gema cujo atributo de cor é **Versatilidade**

| Gema (nome oficial PT-BR) | ID | Nível | Atributos |
| :--- | --: | :-: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_fire_blue.jpg" width="20" height="20" alt="Lápis Mortal" /> **Lápis Mortal** | `240881` | 278 | +11 de Versatilidade e +4 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_fire_blue.jpg" width="20" height="20" alt="Lápis Mortal" /> **Lápis Mortal** | `240882` | 295 | +12 de Versatilidade e +5 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_fire_blue.jpg" width="20" height="20" alt="Lápis Mortal Impecável" /> **Lápis Mortal Impecável** | `240913` | 278 | +14 de Versatilidade e +6 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_fire_blue.jpg" width="20" height="20" alt="Lápis Mortal Impecável" /> **Lápis Mortal Impecável** | `240914` | 295 | +16 de Versatilidade e +7 de Acerto Crítico |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_void_blue.jpg" width="20" height="20" alt="Lápis Primoroso" /> **Lápis Primoroso** | `240885` | 278 | +11 de Versatilidade e +4 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_void_blue.jpg" width="20" height="20" alt="Lápis Primoroso" /> **Lápis Primoroso** | `240886` | 295 | +12 de Versatilidade e +5 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_void_blue.jpg" width="20" height="20" alt="Lápis Primoroso Impecável" /> **Lápis Primoroso Impecável** | `240917` | 278 | +14 de Versatilidade e +6 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_void_blue.jpg" width="20" height="20" alt="Lápis Primoroso Impecável" /> **Lápis Primoroso Impecável** | `240918` | 295 | +16 de Versatilidade e +7 de Maestria |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_nature_blue.jpg" width="20" height="20" alt="Lápis Veloz" /> **Lápis Veloz** | `240883` | 278 | +11 de Versatilidade e +4 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_nature_blue.jpg" width="20" height="20" alt="Lápis Veloz" /> **Lápis Veloz** | `240884` | 295 | +12 de Versatilidade e +5 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_nature_blue.jpg" width="20" height="20" alt="Lápis Veloz Impecável" /> **Lápis Veloz Impecável** | `240915` | 278 | +14 de Versatilidade e +6 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_nature_blue.jpg" width="20" height="20" alt="Lápis Veloz Impecável" /> **Lápis Veloz Impecável** | `240916` | 295 | +16 de Versatilidade e +7 de Aceleração |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_frost_blue.jpg" width="20" height="20" alt="Lápis Versátil" /> **Lápis Versátil** | `240879` | 278 | +12 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_uncommon_gem_cut_frost_blue.jpg" width="20" height="20" alt="Lápis Versátil" /> **Lápis Versátil** | `240880` | 295 | +13 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_frost_blue.jpg" width="20" height="20" alt="Lápis Versátil Impecável" /> **Lápis Versátil Impecável** | `240911` | 278 | +15 de Versatilidade |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_jewelcrafting_rare_gem_cut_frost_blue.jpg" width="20" height="20" alt="Lápis Versátil Impecável" /> **Lápis Versátil Impecável** | `240912` | 295 | +17 de Versatilidade |

---

## 4. Como isso entra no cálculo do projeto

Os três specs do projeto são conjuradores de Intelecto, então a leitura por atributo é direta:

| Peça | Encantamento que interessa | Por quê |
| :--- | :--- | :--- |
| Peitoral | **Encantamento da Marca do Magíster - Torso** | +40 de Intelecto e +5 de mana |
| Arma | **Encantamento da Maestria Arcana - Arma** | +124 de Maestria por 15 s, procs em feitiços |
| Arma (alternativa) | **Encantamento da Acuidade dos Ren'dorei - Arma** ou **Encantamento de Rito dos Hash'ey - Arma** | +67 de primário por 15 s, ou +139 de secundário aleatório |
| Anel (2 slots) | **Encantamento da Aceleração Talassiana - Anel** / **Encantamento da Maestria de Zul'jin - Anel** / **Encantamento da Diligência de Luaprata - Anel** | +24 ou +29 no secundário escolhido |
| Cabeça | **Encantamento da Runa da Evasão Potencializada - Elmo** | +37 de Evasão (defensivo) |
| Ombros | **Encantamento da Recomposição de Luaprata - Ombros** | +166 de Sorver (defensivo) |
| Pés | **Encantamento da Caça do Andarilho - Botas** | +11 de Velocidade e +232 de Vigor |
| Gemas | 1× **Diamante do Canto Eterno Indecifrável** + gemas de cor do secundário prioritário | Diamante puro dá +32 de primário; as de cor preenchem os secundários |

> **Regra que o motor deve seguir:** encantamento e gema **não** interagem com o limite de embelezamento (`Único-equipado: Embelezado (2)`). São sistemas independentes. Só embelezamento conta para o limite de 2.

---

## 4.5 O campo `enchant_id` do SimC — por que o encantamento "não aparecia"

O export não traz o ID do pergaminho. Traz `enchant_id`, que é a linha da tabela **`SpellItemEnchantment`** — e existe **uma linha por qualidade** do mesmo encantamento. É por isso que um `enchant_id` como `7981` não aparece em nenhum catálogo de item deste projeto.

| `enchant_id` | O que é | Pergaminho equivalente |
| --: | :--- | :--- |
| `7980` | Enchant Weapon - Jan'alai's Precision, **Tier 1** | `243970` |
| `7981` | Enchant Weapon - Jan'alai's Precision, **Tier 2** | `243971` |
| `7982` | Enchant Weapon - Berserker's Rage, **Tier 1** | `243972` |
| `8688` | Rite of the Hash'ey, **Tier 1** | `273071` |
| `8689` | Rite of the Hash'ey, **Tier 2** | `273072` |

O mapa completo está em [`enchant_ids_s2.json`](enchant_ids_s2.json:1): **97 `enchant_id`** — 76 de equipamento, 8 de óleo, 1 de tinker e 12 de ferramenta — gerado por [`tools/mapear_enchant_ids.js`](tools/mapear_enchant_ids.js:1) a partir do DB2 público `SpellItemEnchantment` (Wago Tools, gratuito).

```bash
node tools/mapear_enchant_ids.js 7981   # 7981 -> Precisao de Jan'alai (Tier 2)
node tools/mapear_enchant_ids.js        # reconstroi o mapa inteiro
```

> **Regra de leitura:** encantamento de arma é fonte de dano relevante — 124 de secundário em proc (Maestria Arcana, Raiva Incontrolada, Precisão de Jan'alai, Tenacidade), 139 de secundário aleatório (Rito dos Hash'ey), 67 de primário (Acuidade dos Ren'dorei). Nenhuma comparação de arma pode ser concluída sem **resolver** o `enchant_id` primeiro. O mapa guarda o nome oficial e o campo `fonte_nome`, que diz se o nome veio do tooltip do item ou do feitiço.

**Limite conhecido:** as 3 **Magilinhas** e os 3 **Kits de Armadura** não aparecem na tabela `SpellItemEnchantment` deste build. Se vierem como `enchant_id`, resolver pelo nome na seção 2.2.

---

## 4.6 Itens que ocupam o mesmo slot do encantamento

Existem aprimoramentos que **não são encantamento de equipamento** mas disputam o mesmo slot. Eles aparecem no export como `enchant_id` normal e precisam ser lidos como tal.

| `enchant_id` | Nome oficial PT-BR | Tipo | Nome em inglês | Observação |
| --: | :--- | :--- | :--- | :--- |
| `8051` | **Óleo de Fênix Talassiano** | óleo de arma | *Thalassian Phoenix Oil* | Tier 1 · ilvl 278 · +13 Crítico e +13 Aceleração |
| `8052` | **Óleo de Fênix Talassiano** | óleo de arma | *Thalassian Phoenix Oil* | Tier 2 · ilvl 295 · +16 Crítico e +16 Aceleração |
| `8053` | **Óleo da Aurora** | óleo de arma | *Oil of Dawn* | Tier 1 · ilvl 278 · barreira 1.503 · só cura |
| `8054` | **Óleo da Aurora** | óleo de arma | *Oil of Dawn* | Tier 2 · ilvl 295 · barreira 1.879 · só cura |
| `8055` | **Gume Encantado do Contrabandista** | óleo de arma | *Smuggler's Enchanted Edge* | Tier 1 · ilvl 278 |
| `8056` | **Gume Encantado do Contrabandista** | óleo de arma | *Smuggler's Enchanted Edge* | Tier 2 · ilvl 295 |
| `8612` | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_engineering_scope_color2.jpg" width="20" height="20" alt="Olho de Lince do Contrabandista" /> **Olho de Lince do Contrabandista** | **mira de arma de longo alcance** | *Smuggler's Lynx Eye* | Tier 1 · item `257747` · **+15 de Maestria** por proc (≈3 procs/min) |
| `8613` | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_engineering_scope_color2.jpg" width="20" height="20" alt="Olho de Lince do Contrabandista" /> **Olho de Lince do Contrabandista** | **mira de arma de longo alcance** | *Smuggler's Lynx Eye* | Tier 2 · mesmo item `257747` · **+15 de Maestria** por proc |
| `8702` | **R0CKY pra Viagem** | tinker de elmo | *R0CKY* | elmo · reduz velocidade de queda por 2 min · Engenharia |

**As duas regras que saem daqui:**

1. **Óleo de arma e encantamento permanente coexistem.** São camadas diferentes: 1 óleo temporário (120 min) **+** 1 encantamento permanente na mesma arma. Maxroll lista os dois no mesmo perfil (Frost Mage 12.1.5: *Enchant Weapon - Arcane Mastery* no item e *Thalassian Phoenix Oil* nos consumíveis).
2. **Tinker de elmo compete com o encantamento de elmo.** `R0CKY` (`8702`) dá **redução de velocidade de queda por 2 min** e ocupa a linha de encantamento do elmo — escolhê-lo significa abrir mão de `Encantamento da Runa da Evasão Potencializada - Elmo` (+37 Evasão) ou `Encantamento da Bênção da Velocidade Potencializada - Elmo` (+22 Velocidade).

---

## 5. Lacunas deste catálogo

| Item | Situação |
| :--- | :--- |
| Encantamentos de pulsos, mãos, pernas e capa | Não existem na faixa varrida; falta confirmação no jogo |
| Nome do efeito de alguns encantamentos de arma | O tooltip traz o dano como fórmula `(1 * N)`; o valor final depende do nível do personagem |
| Gemas `Amani` da página de Joalheria | `Pedra Amani Perfurante`, `Peridoto Amani Opalescente` e `Granada Amani Rugidora` são **decoração de casa**, não gema de combate |
| Encantamento `Rito dos Hash'ey` | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_inscription2_repcontracts_80_scroll_uprez_color1.jpg" width="20" height="20" alt="Fórmula: Rito dos Hash'ey" /> **Resolvido em 2026-11-06**: o 580 é o **nível do pergaminho**, não outra trilha. A receita é a **Fórmula `273073`**, no mesmo bloco 273059–273073 das outras receitas de Midnight, especialização **Aprimoramentos Amani — Zelo de Zul'Aman**. Duas qualidades: `273071` (120) e `273072` (139) |
| **Mira ≠ óleo** | `Olho de Lince do Contrabandista` (`257747`, enchants `8612`/`8613`) **não é óleo**: é **mira** de arma de longo alcance (+15 de Maestria esporádico), fabricada por Engenharia de Midnight. Fica em `mira_de_arma` no JSON — nunca misturar com a camada de óleo (coexistem: óleo em arma corpo a corpo, mira em arma de fogo) |

---

## Fontes

- **Wowhead — tooltips oficiais** (`nether.wowhead.com/tooltip/item`, `locale=8` e `locale=0`): nomes PT-BR, nomes EN, níveis e texto de efeito com os números.
- **Wowhead — Midnight Enchanting / Jewelcrafting Profession Overview**: receitas de referência para montar as faixas de varredura.
- **Wowhead — Gems (`/items/gems`)**: confirmação de que os diamantes são `Prismatic Gem`.
- **Method — List of all Midnight Consumables, Enchants and Gems**: conferência cruzada dos nomes em inglês e do alerta de que o diamante é único-equipado.
- **Auditoria interna:** [`tools/auditar_encantamentos_gemas.js`](tools/auditar_encantamentos_gemas.js:1) — 38 encantamentos em 76 IDs + 72 gemas, 0 falhas.
