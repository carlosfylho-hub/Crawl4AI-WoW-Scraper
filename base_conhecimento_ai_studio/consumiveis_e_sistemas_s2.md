# Guia Definitivo: Todas as Combinações do Folio Ômnico (*Omnium Folio*), Altar da Corrosão (*Altar of Corrosion*) e Consumíveis — Série 2 (*Season 2*, Patch 12.1.5)

**Expansão:** World of Warcraft: Midnight
**Patch:** 12.1.5 — A Maldição de Ula'tek (*The Curse of Ula'tek*)
**Sistema do Folio introduzido em:** 12.0.7
**Classes Analisadas:** Druida do Equilíbrio (*Balance Druid*), Sacerdote das Sombras (*Shadow Priest*), Bruxo Demonologia (*Demonology Warlock*)
**Padrão de Formatação:** Português do Brasil (PT-BR) como foco principal absoluto com terminologia oficial do Wowhead PT-BR, acompanhado pelo nome em Inglês entre parênteses `(*English Name*)` para identificação de telas do jogo em inglês.

---

## Correção aplicada em 2026-11-05

Esta versão corrige um erro estrutural da versão anterior, que afirmava existirem **54 combinações** e listava apenas **3 opções na linha 4**.

| Item | Versão anterior | Versão atual | Fonte |
|---|---|---|---|
| Total de runas | 12 | **13** | Guia oficial do Omnium Folio no Wowhead |
| Opções na linha 4 | 3 | **4** | Idem |
| Total de combinações | 54 | **72** | `2 × 3 × 1 × 4 × 3 = 72` |
| Nome da opção 4B | Aceleração Ardente (*Focused Haste*) | **Aceleração Ardente (*Rune of Burning Haste*)** | Idem |
| Nome da opção 4C | Astúcia Magistral (*Mastery Resonance*) | **Astúcia Magistral (*Rune of Masterful Cunning*)** | Idem |
| Opção 4D | Não existia no documento | **Guerreiro Versátil (*Rune of The Versatile Warrior*)** | Idem |

**Consequência numérica:** todos os códigos `Cxx` acima de `C09` mudaram de significado nesta revisão. A nova fórmula está documentada na seção 1.4. Mapa completo de-para, spell IDs e efeitos oficiais em [`rune_ids_s2.json`](rune_ids_s2.json:1).

## Correção de nomes de consumíveis aplicada em 2026-11-05

Os nomes de consumíveis da versão anterior eram **traduções inventadas**, não os nomes oficiais do cliente PT-BR. Todos foram reescritos contra o tooltip do Wowhead em português (`locale=8`). O de-para completo:

<!-- NAO-CORRIGIR -->
| O guia dizia | Nome oficial PT-BR | Nome em inglês | ID |
| :--- | :--- | :--- | ---: |
| Nostrum Deslumbrante | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_121_professions_alchemy_potion_amani_purple.jpg" width="20" height="20" alt="Pancresto Tentador" /> **Pancresto Tentador** | *Alluring Nostrum* | `271889` |
| Poção de Cura de Luaprata Concentrada | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_lightpotion_purple.jpg" width="20" height="20" alt="Poção de Vida de Luaprata Concentrada" /> **Poção de Vida de Luaprata Concentrada** | *Concentrated Silvermoon Health Potion* | `271883` |
| Frasco dos Cavaleiros de Sangue | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_flask_sindoreipotion_white-.jpg" width="20" height="20" alt="Frasco dos Cavaleiros Sangrentos" /> **Frasco dos Cavaleiros Sangrentos** | *Flask of the Blood Knights* | `241325` |
| Frasco dos Magistrados | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_flask_sindoreipotion_black.jpg" width="20" height="20" alt="Frasco dos Magísteres" /> **Frasco dos Magísteres** | *Flask of the Magisters* | `241323` |
| Frasco do Sol Despedaçado | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_flask_sindoreipotion_red--.jpg" width="20" height="20" alt="Frasco do Sol Partido" /> **Frasco do Sol Partido** | *Flask of the Shattered Sun* | `241327` |
| Desfile de Luaprata | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_tradeskill_cooking_feastofblood.jpg" width="20" height="20" alt="Parada de Luaprata" /> **Parada de Luaprata** | *Silvermoon Parade* | `255845` |
| Mistura Quel'dorei | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_10_draconicdelicacies.jpg" width="20" height="20" alt="Mix Quel'dorei" /> **Mix Quel'dorei** | *Quel'dorei Medley* | `242272` |
| Banquete Florescente | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_cooked_greatpabanquet_wok.jpg" width="20" height="20" alt="Banquete Desabrochante" /> **Banquete Desabrochante** | *Blooming Feast* | `242273` |
| Celebração de Harandar | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_1h_soup_b_01_misc_1h_soup_b_01.jpg" width="20" height="20" alt="Comemoração de Harandar" /> **Comemoração de Harandar** | *Harandar Celebration* | `255846` |
| Filé Beijado pelo Caos | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_100_revengeservedcold_color02.jpg" width="20" height="20" alt="Filé Beijado pela Vileza" /> **Filé Beijado pela Vileza** | *Fel-Kissed Filet* | `242286` |
| Espetinhos Cintilantes | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_160_fish_87.jpg" width="20" height="20" alt="Espetinhos Brilhantes" /> **Espetinhos Brilhantes** | *Glitter Skewers* | `242281` |
| Asas Sábias Distorcidas | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_10_grandbanquet.jpg" width="20" height="20" alt="Cortes de Sábio da Distorção" /> **Cortes de Sábio da Distorção** | *Warped Wise Wings* | `242285` |
| Luminbar Tostado pelo Sol | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_cooked_wildfowlroast.jpg" width="20" height="20" alt="Lumitana Dourado ao Sol" /> **Lumitana Dourado ao Sol** | *Sun-Seared Lumifin* | `242283` |
| Óleo de Fênix Talassiana | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_manaoil_red.jpg" width="20" height="20" alt="Óleo de Fênix Talassiano" /> **Óleo de Fênix Talassiano** | *Thalassian Phoenix Oil* | `243733` / `243734` |
| Runa de Aprimoramento Cristalizada | <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_10_enchanting_crystal_color2.jpg" width="20" height="20" alt="Runa de Aprimoramento Tocada pelo Caos" /> **Runa de Aprimoramento Tocada pelo Caos** | *Void-Touched Augment Rune* | `259085` |
<!-- FIM-NAO-CORRIGIR -->

Nomes que **já estavam corretos**: Potencial da Luz (*Light's Potential*), Esplendor Líquido (*Liquid Luster*), Frasco da Resistência Talassiana (*Flask of Thalassian Resistance*), Lula Carmesim (*Crimson Calamari*), Costeletas Arcanas (*Arcano Cutlets*), Óleo da Aurora (*Oil of Dawn*).

Além dos nomes, três **erros de conteúdo** foram corrigidos:

1. **Faltavam duas poções de combate** — a **Poção da Imprudência** (*Potion of Recklessness*, `241289`) e o **Grogue da Impulsividade Desenfreada** (*Draught of Rampant Abandon*, `241293`). A primeira é a poção de maior número isolado do jogo (+1.725 de secundário) e era citada pelo MaxRoll sem constar no guia.
2. **O Óleo da Aurora estava recomendado para DPS.** Ele só proca com **feitiços de cura** — é inútil para as três specs deste projeto.
3. **As comidas de "maior secundário" não estavam listadas.** Elas dão +65 contra +58 das comidas fixas e passam a ser a recomendação padrão.

---

# PARTE 1: FOLIO ÔMNICO (*OMNIUM FOLIO*) — TODAS AS 72 COMBINAÇÕES

## 1.1 Arquitetura e Cálculo Combinatório

O **Folio Ômnico (*Omnium Folio*)** é o sistema rúnico de poder de jogador (*player power*) que funciona em **todas as instâncias do jogo** (Mundo Aberto, Imersões / *Delves*, Masmorras Mítico+ e Raides). Foi introduzido no patch 12.0.7 e é desbloqueado por uma curta cadeia de missões no Sunstrider Omnium, dentro do Magisters' Terrace na Ilha de Quel'Danas.

A árvore rúnica é composta por **5 linhas**, cada uma com um número diferente de opções, totalizando **13 runas** e **72 configurações exclusivas**:

- **Linha 1 (Runa Central / *Core*):** 2 opções — obrigatória
  - `1A` **Runa do Fogo Incontido (*Rune of Unleashed Fire*)** — spell `1279599`
  - `1B` **Runa dos Orbes Tocados pelo Caos (*Rune of Void-Touched Orbs*)** — spell `1279596`
- **Linha 2 (Suporte Defensivo e Mobilidade):** 3 opções — obrigatória
  - `2A` **Concha Maculada de Caos (*Rune of Void-Tainted Shell*)** — spell `1279604`
  - `2B` **Runa de Autorrecomposição (*Rune of Self-Mending*)** — spell `1279603`
  - `2C` **Reflexos de Lince (*Rune of Lynxlike Reflexes*)** — spell `1279605`
- **Linha 3 (Poder Remanescente / *Lingering*):** 1 opção — obrigatória
  - `3A` **Runa da Perenidade (*Rune of Lingering*)** — spell `1287555` (alias `1287663`)
- **Linha 4 (Atributo Secundário Focado):** **4 opções** — obrigatória
  - `4A` **Poder Crítico (*Rune of Critical Power*)** — spell `1287772` — +52,7 de Acerto Crítico
  - `4B` **Aceleração Ardente (*Rune of Burning Haste*)** — spell `1287774` — +52,7 de Aceleração
  - `4C` **Astúcia Magistral (*Rune of Masterful Cunning*)** — spell `1287771` — +52,7 de Maestria
  - `4D` **Guerreiro Versátil (*Rune of The Versatile Warrior*)** — spell `1279613` — +52,7 de Versatilidade
- **Linha 5 (Talento Ápice / *Capstone*):** 3 opções — obrigatória
  - `5A` **Runa de Sobrecarga (*Rune of Overload*)** — spell `1279614` — +100% de eficácia da Runa Central
  - `5B` **Runa de Energia Residual (*Rune of Residual Energy*)** — spell `1279615` — +100% de eficácia da Runa da Perenidade
  - `5C` **Runa dos Ecos (*Rune of Echoes*)** — spell `1279616` — repete dano e cura das runas em 50% após 10s

$$\text{Total de Combinações Possíveis} = 2 \times 3 \times 1 \times 4 \times 3 = \mathbf{72\text{ Combinações Únicas}}$$

**Efeito acumulativo da linha 4:** o bônus de atributo concede 52,7 de rating e **pode se sobrepor**, ou seja, empilha a cada proc da Runa Central. Em lutas longas de alvo único, a sobreposição faz da linha 4 a maior fonte individual de atributo secundário do sistema.

## 1.2 Regra de sinergia entre linhas

Antes de escolher qualquer combinação, três relações mecânicas determinam o resultado:

1. **`5A` amplifica a Runa Central, `5B` amplifica a Runa da Perenidade.** Escolher `5B` sem entender que ele multiplica a linha 3 significa pagar o custo de uma runa capstone para reforçar o efeito periódico, não o burst.
2. **`4D` (Versatilidade) é a única opção da linha 4 com componente defensiva**, somando mitigação de dano recebido à amplificação de dano e cura. É a escolha correta em chaves +10 ou superior, onde sobreviver vale mais que qualquer atributo ofensivo.
3. **`2C` (Reflexos de Lince) depende de ser atingido.** Em encontros onde o jogador não toma dano direto, a runa fica inerte — o que a torna uma escolha ruim para raide de alvo único bem posicionado e boa para Imersões solo e M+ com dano de atrito.

## 1.3 Catálogo Sistemático das 72 Combinações

### Bloco A: Variantes com Runa do Fogo Incontido (*Rune of Unleashed Fire* — 1A)
*Foco: dano direto de Fogo, pilares de chama por proc, pressão sustentada.*

#### Família 1A + 2A — Concha Maculada de Caos (*Void-Tainted Shell*) — C01 a C12
| ID | Código Rúnico | Linha 4 | Linha 5 | Perfil Tático e Situação de Uso |
| :-: | :--- | :--- | :--- | :--- |
| **C01** | `1A-2A-3A-4A-5A` | Poder Crítico | Sobrecarga | **Impacto explosivo com proteção.** Pilares de fogo críticos ampliados em 100%, com escudo de absorção contra golpes inevitáveis de chefe. |
| **C02** | `1A-2A-3A-4A-5B` | Poder Crítico | Energia Residual | **Dano múltiplo contínuo e seguro.** Ideal para grupos densos em M+ sob afixos de dano de atrito contínuo. |
| **C03** | `1A-2A-3A-4A-5C` | Poder Crítico | Ecos | **Alvo único de raide com mitigação.** Eco de 50% reforça o dano total em lutas longas com pulsos periódicos. |
| **C04** | `1A-2A-3A-4B-5A` | Aceleração Ardente | Sobrecarga | **Aceleração máxima com escudo.** Para conjuradores que dependem de lançamentos acelerados e precisam resistir a projéteis teleguiados. |
| **C05** | `1A-2A-3A-4B-5B` | Aceleração Ardente | Energia Residual | **Dano sustentado de M+.** Aceleração empilhada com o efeito periódico da linha 3 ampliado em 100%. |
| **C06** | `1A-2A-3A-4B-5C` | Aceleração Ardente | Ecos | **Cadência máxima em raide.** A melhor combinação de alvo único puro: aceleração empilhável mais eco de 50% de todo o dano das runas. |
| **C07** | `1A-2A-3A-4C-5A` | Astúcia Magistral | Sobrecarga | **Explosão mágica com absorção.** Maestria empilhada para specs que escalam por efeito periódico, com pilar de fogo dobrado. |
| **C08** | `1A-2A-3A-4C-5B` | Astúcia Magistral | Energia Residual | **Multiplicação periódica.** Maestria somada ao reforço de 100% na Runa da Perenidade; ideal para lutas de dano em área contínuo. |
| **C09** | `1A-2A-3A-4C-5C` | Astúcia Magistral | Ecos | **Eco prolongado de Maestria.** Maximiza o retorno passivo em lutas prolongadas. |
| **C10** | `1A-2A-3A-4D-5A` | Guerreiro Versátil | Sobrecarga | **Sobrevivência ofensiva.** Versatilidade empilhada reduz dano recebido; escolha recomendada para chaves +10 onde a morte custa mais que o dano perdido. |
| **C11** | `1A-2A-3A-4D-5B` | Guerreiro Versátil | Energia Residual | **Mitigação com desgaste.** Versatilidade mais Runa da Perenidade ampliada para conteúdo de dano contínuo e alto risco. |
| **C12** | `1A-2A-3A-4D-5C` | Guerreiro Versátil | Ecos | **Resiliência com eco.** Defesa máxima do sistema mantendo o eco de 50%; para Delve Tier 11 solo sem curador. |

#### Família 1A + 2B — Autorrecomposição (*Rune of Self-Mending*) — C13 a C24
| ID | Código Rúnico | Linha 4 | Linha 5 | Perfil Tático e Situação de Uso |
| :-: | :--- | :--- | :--- | :--- |
| **C13** | `1A-2B-3A-4A-5A` | Poder Crítico | Sobrecarga | **Explosão crítica com cura passiva.** Indicado para encontros com dano de desgaste moderado (*rot damage*). |
| **C14** | `1A-2B-3A-4A-5B` | Poder Crítico | Energia Residual | **Desgaste balanceado.** Eficiente contra sangramento ou veneno de longa duração. |
| **C15** | `1A-2B-3A-4A-5C` | Poder Crítico | Ecos | **Recombinação contínua.** Mantém a vida estabilizada enquanto replica o dano das runas. |
| **C16** | `1A-2B-3A-4B-5A` | Aceleração Ardente | Sobrecarga | **Ciclo acelerado de cura e dano.** Alta frequência de procs convertida em pulsos mais frequentes de autocura. |
| **C17** | `1A-2B-3A-4B-5B` | Aceleração Ardente | Energia Residual | **Sustento em masmorras com DoTs.** Contrapõe penalidades contínuas sem abrir mão da cadência. |
| **C18** | `1A-2B-3A-4B-5C` | Aceleração Ardente | Ecos | **Fluidez e autonomia.** Rotações dinâmicas com alta mobilidade e absorção passiva de atrito. |
| **C19** | `1A-2B-3A-4C-5A` | Astúcia Magistral | Sobrecarga | **Pico elemental com regeneração.** Maestria alta combinada com autocura e pilar de fogo dobrado. |
| **C20** | `1A-2B-3A-4C-5B` | Astúcia Magistral | Energia Residual | **Sustento de área mágico.** Para lutas de longo desgaste com foco em amplificação elemental. |
| **C21** | `1A-2B-3A-4C-5C` | Astúcia Magistral | Ecos | **Geração estável.** Estabilidade defensiva total em combates de cerco prolongado. |
| **C22** | `1A-2B-3A-4D-5A` | Guerreiro Versátil | Sobrecarga | **Tanque improvisado.** Autocura mais Versatilidade: a combinação mais resistente do Bloco A com capstone ofensiva. |
| **C23** | `1A-2B-3A-4D-5B` | Guerreiro Versátil | Energia Residual | **Solo de alto risco.** Para Delves onde parar de atacar significa morrer; mitigação somada a desgaste ampliado. |
| **C24** | `1A-2B-3A-4D-5C` | Guerreiro Versátil | Ecos | **Resiliência absoluta.** Defesa máxima com eco; recomendada para solar chefes de Delve Tier 11. |

#### Família 1A + 2C — Reflexos de Lince (*Lynxlike Reflexes*) — C25 a C36
| ID | Código Rúnico | Linha 4 | Linha 5 | Perfil Tático e Situação de Uso |
| :-: | :--- | :--- | :--- | :--- |
| **C25** | `1A-2C-3A-4A-5A` | Poder Crítico | Sobrecarga | **Disparo rápido em movimento.** Ideal para mecânicas que exigem reposicionamento sem perder dano explosivo. |
| **C26** | `1A-2C-3A-4A-5B` | Poder Crítico | Energia Residual | **Velocidade de avanço em Imersões.** Corrida entre salas com limpeza imediata de grupos. |
| **C27** | `1A-2C-3A-4A-5C` | Poder Crítico | Ecos | **Cleave móvel de raide.** Para encontros com poças no chão que forçam movimentação constante. |
| **C28** | `1A-2C-3A-4B-5A` | Aceleração Ardente | Sobrecarga | **Combate dinâmico de lançamento.** Essencial para conjuradores em lutas com interrupções frequentes de terreno. |
| **C29** | `1A-2C-3A-4B-5B` | Aceleração Ardente | Energia Residual | **Ritmo acelerado de M+.** Recomendada para chaves de velocidade onde o tempo de travessia dita o fechamento. |
| **C30** | `1A-2C-3A-4B-5C` | Aceleração Ardente | Ecos | **Reposicionamento fluido de raide.** Evita quedas acentuadas de dano em encontros dinâmicos. |
| **C31** | `1A-2C-3A-4C-5A` | Astúcia Magistral | Sobrecarga | **Golpe rápido fortalecido.** Maestria máxima alinhada a esquiva ágil de habilidades teleguiadas. |
| **C32** | `1A-2C-3A-4C-5B` | Astúcia Magistral | Energia Residual | **Controle territorial.** Mantém dano elevado enquanto se esquiva de áreas perigosas. |
| **C33** | `1A-2C-3A-4C-5C` | Astúcia Magistral | Ecos | **Consistência em movimento.** Distribuição contínua de dano periódico em deslocamento constante. |
| **C34** | `1A-2C-3A-4D-5A` | Guerreiro Versátil | Sobrecarga | **Kiting com defesa.** Mobilidade de 2C somada à mitigação de 4D: a combinação mais evasiva do Bloco A. |
| **C35** | `1A-2C-3A-4D-5B` | Guerreiro Versátil | Energia Residual | **Fuga sustentada.** Para Imersões com patrulhas agressivas e dano contínuo. |
| **C36** | `1A-2C-3A-4D-5C` | Guerreiro Versátil | Ecos | **Movimento protegido.** Defesa alta mantendo eco de dano; boa para mundo aberto de alto risco. |

---

### Bloco B: Variantes com Runa dos Orbes Tocados pelo Caos (*Rune of Void-Touched Orbs* — 1B)
*Foco: esferas de energia cósmica acumuladas, dano por projétil e multiplicação em múltiplos alvos.*

#### Família 1B + 2A — Concha Maculada de Caos (*Void-Tainted Shell*) — C37 a C48
| ID | Código Rúnico | Linha 4 | Linha 5 | Perfil Tático e Situação de Uso |
| :-: | :--- | :--- | :--- | :--- |
| **C37** | `1B-2A-3A-4A-5A` | Poder Crítico | Sobrecarga | **Detonação de esferas com escudo.** Coleta esferas para descarregar dano massivo sob proteção total. |
| **C38** | `1B-2A-3A-4A-5B` | Poder Crítico | Energia Residual | **Multiplicação do Vazio.** Explosões encadeadas contra grupos numerosos. |
| **C39** | `1B-2A-3A-4A-5C` | Poder Crítico | Ecos | **Recomendada para Sacerdote Sombra em raide.** As esferas replicam feitiços sombrios mantendo absorção estável. |
| **C40** | `1B-2A-3A-4B-5A` | Aceleração Ardente | Sobrecarga | **Geração rápida de esferas.** Encurta o intervalo de acumulação para consumo durante janelas de *burst*. |
| **C41** | `1B-2A-3A-4B-5B` | Aceleração Ardente | Energia Residual | **Pressão contínua multi-alvo.** Direciona esferas a alvos adicionais sem perder o foco no chefe. |
| **C42** | `1B-2A-3A-4B-5C` | Aceleração Ardente | Ecos | **Replicação sombria sustentada.** Mantém cadência fluida de canalização com dano protegido. |
| **C43** | `1B-2A-3A-4C-5A` | Astúcia Magistral | Sobrecarga | **Amplificação máxima de Sombra.** Maestria convertida em detonações de altíssimo impacto. |
| **C44** | `1B-2A-3A-4C-5B` | Astúcia Magistral | Energia Residual | **Dano residual cósmico.** Esferas deixam rastro periódico ampliado pela Runa da Perenidade. |
| **C45** | `1B-2A-3A-4C-5C` | Astúcia Magistral | Ecos | **Cascata periódica.** Padrão de Maestria replicado ciclicamente com escudo sempre recarregado. |
| **C46** | `1B-2A-3A-4D-5A` | Guerreiro Versátil | Sobrecarga | **Esferas com blindagem.** Mitigação máxima para conjuradores expostos a dano mágico em área. |
| **C47** | `1B-2A-3A-4D-5B` | Guerreiro Versátil | Energia Residual | **Defesa sustentada.** Para raides com pulsos de dano mágico em área contínuo. |
| **C48** | `1B-2A-3A-4D-5C` | Guerreiro Versátil | Ecos | **Fortaleza cósmica.** Defesa máxima mantendo replicação; para chaves altas sem curador dedicado. |

#### Família 1B + 2B — Autorrecomposição (*Rune of Self-Mending*) — C49 a C60
| ID | Código Rúnico | Linha 4 | Linha 5 | Perfil Tático e Situação de Uso |
| :-: | :--- | :--- | :--- | :--- |
| **C49** | `1B-2B-3A-4A-5A` | Poder Crítico | Sobrecarga | **Vampirismo de esferas.** Detonação crítica converte parte do dano em autocura imediata. |
| **C50** | `1B-2B-3A-4A-5B` | Poder Crítico | Energia Residual | **Auto-sustentação prolongada.** Para puxadas perigosas em Imersões sem curador dedicado. |
| **C51** | `1B-2B-3A-4A-5C` | Poder Crítico | Ecos | **Regeneração cíclica.** Cada esfera replicada renova o pulso de recuperação passiva. |
| **C52** | `1B-2B-3A-4B-5A` | Aceleração Ardente | Sobrecarga | **Disparo veloz com autocura.** Aumenta a cadência das esferas enquanto estabiliza a vida. |
| **C53** | `1B-2B-3A-4B-5B` | Aceleração Ardente | Energia Residual | **Atrito seguro.** Recomendada para semanas de M+ com afixos de dano contínuo onde parar de bater significa morrer. |
| **C54** | `1B-2B-3A-4B-5C` | Aceleração Ardente | Ecos | **Ritmo estável de suporte.** Reduz a pressão sobre os curadores em lutas longas. |
| **C55** | `1B-2B-3A-4C-5A` | Astúcia Magistral | Sobrecarga | **Autocura elemental.** Maestria convertida em explosões fortes com cura própria proporcional. |
| **C56** | `1B-2B-3A-4C-5B` | Astúcia Magistral | Energia Residual | **Defesa residual.** Área de solo seguro que queima inimigos e cura o conjurador gradativamente. |
| **C57** | `1B-2B-3A-4C-5C` | Astúcia Magistral | Ecos | **Resiliência absoluta.** Recomendada para solar chefes em Imersões Tier 11 com pouca margem para erro. |
| **C58** | `1B-2B-3A-4D-5A` | Guerreiro Versátil | Sobrecarga | **Máxima resistência ofensiva.** Autocura mais Versatilidade; a combinação mais durável com capstone de dano. |
| **C59** | `1B-2B-3A-4D-5B` | Guerreiro Versátil | Energia Residual | **Sobrevivência passiva total.** Para conteúdo solo de alto risco com dano contínuo. |
| **C60** | `1B-2B-3A-4D-5C` | Guerreiro Versátil | Ecos | **Inquebrável.** Defesa máxima com eco de cura; para progressão solo de Delve Tier 11. |

#### Família 1B + 2C — Reflexos de Lince (*Lynxlike Reflexes*) — C61 a C72
| ID | Código Rúnico | Linha 4 | Linha 5 | Perfil Tático e Situação de Uso |
| :-: | :--- | :--- | :--- | :--- |
| **C61** | `1B-2C-3A-4A-5A` | Poder Crítico | Sobrecarga | **Bombardeio móvel de esferas.** Coleta esferas em alta velocidade e detona em movimento; recomendada para Shadow Priest em M+ e Delves. |
| **C62** | `1B-2C-3A-4A-5B` | Poder Crítico | Energia Residual | **Kiting agressivo em área.** Recuo de monstros rápidos mantendo trilhas de Vazio no chão. |
| **C63** | `1B-2C-3A-4A-5C` | Poder Crítico | Ecos | **Eco em movimento.** Dano sustentado alto mesmo em combates que forçam corridas frequentes. |
| **C64** | `1B-2C-3A-4B-5A` | Aceleração Ardente | Sobrecarga | **Disparo contínuo com mobilidade.** Alta frequência de esferas com bônus de velocidade para esquivar de áreas frontais. |
| **C65** | `1B-2C-3A-4B-5B` | Aceleração Ardente | Energia Residual | **Varredura veloz de caçadas (*Prey*).** Limpeza acelerada de mapas abertos e eventos dinâmicos. |
| **C66** | `1B-2C-3A-4B-5C` | Aceleração Ardente | Ecos | **Fluidez de raide.** Para chefes com mecânicas de perseguição que exigem manobras evasivas. |
| **C67** | `1B-2C-3A-4C-5A` | Astúcia Magistral | Sobrecarga | **Pico de Maestria móvel.** Descarga de dano explosivo sem ficar enraizado em ponto fixo. |
| **C68** | `1B-2C-3A-4C-5B` | Astúcia Magistral | Energia Residual | **Controle territorial dinâmico.** Resíduos de Maestria enquanto reposiciona o grupo de monstros. |
| **C69** | `1B-2C-3A-4C-5C` | Astúcia Magistral | Ecos | **Maestria sustentada em marcha.** Para encontros com deslocamento constante de longa distância. |
| **C70** | `1B-2C-3A-4D-5A` | Guerreiro Versátil | Sobrecarga | **Evasão blindada.** Mobilidade e mitigação juntas; excelente para mundo aberto com agressão constante. |
| **C71** | `1B-2C-3A-4D-5B` | Guerreiro Versátil | Energia Residual | **Travessia segura.** Para Delves com muitas salas e patrulhas. |
| **C72** | `1B-2C-3A-4D-5C` | Guerreiro Versátil | Ecos | **Marcha protegida.** A combinação mais segura do sistema; defesa máxima com replicação. |

## 1.4 Fórmula de Numeração

Para converter uma combinação no seu código `Cxx` sem consultar a tabela:

$$C = 36 \times (bloco - 1) + 12 \times (familia_2 - 1) + 3 \times (linha_4 - 1) + (linha_5 - 1) + 1$$

Onde `bloco` = 1 para `1A` e 2 para `1B`; `familia_2` = 1 para `2A`, 2 para `2B`, 3 para `2C`; `linha_4` = 1 a 4 conforme `4A` a `4D`; `linha_5` = 1 a 3 conforme `5A` a `5C`.

**Conferência:** `1A-2A-3A-4B-5C` → `36×0 + 12×0 + 3×1 + 2 + 1 = 6` → **C06**. ✓

## 1.5 Sinergia Direta com as Árvores de Talentos das Classes

### 1. Bruxo Demonologia (*Demonology Warlock*)
- **Diabolista (*Diabolist*):**
  - *Combinações Recomendadas:* **`C06`** (`1A-2A-3A-4B-5C`) para Raide; **`C04`** (`1A-2A-3A-4B-5A`) para Míticas+.
  - *Mecânica:* alinha com *Grimório: Guarda Vil* (*Grimoire: Felguard*) e *Tirano Demoníaco* (*Demonic Tyrant*). A Aceleração Ardente reduz o tempo de lançamento de *Mão de Gul'dan* (*Hand of Gul'dan*) e acelera os ataques dos demônios maiores.
- **Ceifador de Almas (*Soul Harvester*):**
  - *Combinações Recomendadas:* **`C05`** (`1A-2A-3A-4B-5B`) para Míticas+; **`C02`** (`1A-2A-3A-4A-5B`) para grupos densos.
  - *Mecânica:* explora a Runa de Energia Residual para multiplicar os efeitos periódicos e acelerar o ciclo de fragmentos de alma.

### 2. Sacerdote das Sombras (*Shadow Priest*)
- **Tecelão do Vazio (*Voidweaver*):**
  - *Combinações Recomendadas:* **`C39`** (`1B-2A-3A-4A-5C`) para Raide; **`C37`** (`1B-2A-3A-4A-5A`) para dano explosivo de M+.
  - *Mecânica:* a *Fenda Entrópica* (*Entropic Rift*) absorve e potencializa as *Orbes Tocados pelo Caos*, disparando rajadas em cascata.
- **Arconte (*Archon*):**
  - *Combinações Recomendadas:* **`C06`** (`1A-2A-3A-4B-5C`) ou **`C42`** (`1B-2A-3A-4B-5C`).
  - *Mecânica:* estende a duração de *Erupção do Vazio* (*Void Eruption*) / *Forma do Vazio* (*Voidform*), permitindo que os Ecos repliquem *Impacto Mental* (*Mind Blast*) continuamente.

### 3. Druida do Equilíbrio (*Balance Druid*)
- **Escolhido de Eluna (*Elune's Chosen*):**
  - *Combinações Recomendadas:* **`C06`** (`1A-2A-3A-4B-5C`) para Alvo Único; **`C08`** (`1A-2A-3A-4C-5B`) para Dano em Área (*AoE*).
  - *Mecânica:* acelera as canalizações de *Fogo Estelar* (*Starfire*) e *Ira* (*Wrath*). O bônus arcano massivo é replicado pela Runa dos Ecos.
- **Guardião do Bosque (*Keeper of the Grove*):**
  - *Combinações Recomendadas:* **`C05`** (`1A-2A-3A-4B-5B`) ou **`C29`** (`1A-2C-3A-4B-5B`).
  - *Mecânica:* os *Ents* invocados por *Força da Natureza* (*Force of Nature*) ganham cadência agressiva com a Aceleração Ardente.

### 4. Escolhas defensivas por contexto
- **Chaves +10 ou superior:** **`C10`** (`1A-2A-3A-4D-5A`) — única combinação que soma mitigação de dano por Versatilidade mantendo capstone ofensiva.
- **Imersões Tier 11 solo:** **`C24`** (`1A-2B-3A-4D-5C`) ou **`C60`** (`1B-2B-3A-4D-5C`) — autocura, Versatilidade e eco de cura.
- **Imersões Tier 8 a 10:** **`C26`** (`1A-2C-3A-4A-5B`) ou **`C61`** (`1B-2C-3A-4A-5A`) — mobilidade com dano.

---

# PARTE 2: ALTAR DA CORROSÃO (*ALTAR OF CORROSION*) & CÓDICE CORROSIVO — TODAS AS COMBINAÇÕES

## 2.1 Matemática e Regras de Ativação do Códice

O **Códice Corrosivo (*Corrosive Codex*)** é alimentado pelas energias venenosas do **Altar da Corrosão (*Altar of Corrosion*)** e possui **12 poderes distintos**.

- **Regra Estrita de Localização:** o Códice Corrosivo opera **exclusivamente no Mundo Aberto e em Imersões (*Delves*)**. Em Raides e Masmorras Mítico+, os seus poderes permanecem **inativos**.
- **Fase Inicial (1 Engaste):** 12 opções individuais possíveis.
- **Fase Avançada (2 Engastes — ao desbloquear 8 poderes com Almas Corrosivas):**

$$\text{Combinações de 2 Poderes Simultâneos} = \binom{12}{2} = \frac{12 \times 11}{2} = \mathbf{66\text{ Combinações Únicas}}$$

## 2.2 Catálogo dos 12 Poderes Individuais (Engaste Único Inicial)

| ID | Nome em Português / Nome em Inglês | Função Mecânica Principal | Melhor Aplicação Tática |
| :-: | :--- | :--- | :--- |
| **U01** | **Dádiva de Ula'tek (*Ula'tek's Gift*)** | Amplificação passiva geral (+7% de dano bruto). | A escolha universal para começar; funciona com qualquer classe sem exigência mecânica. |
| **U02** | **Fauce Ofídica (*Ophidian Maw*)** | Dano em área e execução imediata para monstros com vida abaixo de 20%. | Ideal para eliminar monstros de elite perigosos em Imersões e Caçadas abertas. |
| **U03** | **Ciclo Ourobórico (*Ouroboric Cycle*)** | Rotação cíclica de Atributos Primários e Secundários. | Excelente para classes que causam dano periódico constante ou enfrentam monstros venenosos. |
| **U04** | **Praga da Corrosão (*Plague of Corrosion*)** | Veneno contagioso em área que pula para alvos próximos ao morrer. | Limpeza acelerada de grupos com muitos monstros fracos agrupados. |
| **U05** | **Olhar do Gorgoneion (*Gorgoneion Gaze*)** | Petrificação em pedra de emergência ao atingir menos de 50% de vida. | Rede de segurança indispensável para jogar solo sem curador em Imersões difíceis. |
| **U06** | **Muco Virulento (*Virulent Mucus*)** | 5 cargas de anulação total de ataques por combate. | Permite que conjuradores frágeis façam puxadas agressivas sem sofrer o dano de abertura. |
| **U07** | **Peçonha Insidiosa (*Insidious Venom*)** | +15% de Atributo Primário ao custo de dano periódico em si próprio. | Para maximizar dano bruto quando o jogador tem formas confiáveis de autocura. |
| **U08** | **Veneno Amaldiçoado (*Accursed Poison*)** | +25% de dano de veneno recebido pelos inimigos e conversão em cura. | Muito eficiente para especializações que exploram habilidades periódicas de Natureza/Sombra. |
| **U09** | **Aperto Viperino (*Viperine Grasp*)** | Lentidão de 50% e puxão magnético para o centro. | Controle de multidão em Imersões para agrupar conjuradores e impedir patrulhas de fugir. |
| **U10** | **Gêiser de Miasma (*Miasma Geyser*)** | Erupções periódicas que lançam inimigos para o ar e causam cegueira por 3s. | Interrupção passiva em área contra monstros com lançamentos de feitiços perigosos. |
| **U11** | **Plumagem Lítica (*Lithic Plumage*)** | +30% de armadura física e reflexão de dano de volta aos agressores. | Proteção contra dano físico para quando o ajudante (*pet*) perde a ameaça (*aggro*). |
| **U12** | **Nuvem Mefítica (*Mephitic Cloud*)** | Reduz em 10% a chance de acerto dos inimigos e causa dano contínuo. | Redução passiva contínua de dano recebido em combates com muitos inimigos corpo a corpo. |

## 2.3 Matriz Completa das 66 Combinações de Dois Poderes do Códice

### Família 1: Sinergias do Ciclo Ourobórico (*Ouroboric Cycle*) [P01 a P11]
- **P01 (`Ciclo Ourobórico + Praga da Corrosão`):** **META ABSOLUTO DE IMERSÕES.** A Praga espalha veneno contínuo nos inimigos, travando o Ciclo em seu ápice de atributos bônus.
- **P02 (`Ciclo Ourobórico + Peçonha Insidiosa`):** **BURST MASSIVO DE ATRIBUTO PRIMÁRIO.** A Peçonha envenena o conjurador ativando +15% de Intelecto contínuo enquanto o Ciclo estende o efeito.
- **P03 (`Ciclo Ourobórico + Fauce Ofídica`):** Atributos elevados que aumentam a força dos ataques e aceleram o gatilho de execução em 20% de vida.
- **P04 (`Ciclo Ourobórico + Dádiva de Ula'tek`):** Dano bruto direto; +7% de dano base somado à rotação ininterrupta de atributos.
- **P05 (`Ciclo Ourobórico + Olhar do Gorgoneion`):** Rotação agressiva com proteção automática caso a vida caia abaixo de 50%.
- **P06 (`Ciclo Ourobórico + Veneno Amaldiçoado`):** Sustentação de vida contínua enquanto o ciclo amplifica a taxa de autocura.
- **P07 (`Ciclo Ourobórico + Muco Virulento`):** Segurança total na abertura: inicia o combate imune a 5 golpes e escala os atributos sem risco.
- **P08 (`Ciclo Ourobórico + Aperto Viperino`):** Agrupa os inimigos no centro sob lentidão, facilitando abates rápidos para renovar o ciclo.
- **P09 (`Ciclo Ourobórico + Gêiser de Miasma`):** Interrupção em área por erupção enquanto os atributos aumentados eliminam os monstros no ar.
- **P10 (`Ciclo Ourobórico + Plumagem Lítica`):** Alta resistência física contra monstros pesados enquanto escala o poder mágico.
- **P11 (`Ciclo Ourobórico + Nuvem Mefítica`):** Dano contínuo de proximidade enquanto o ciclo amplifica os pulsos da nuvem.

### Família 2: Sinergias da Fauce Ofídica (*Ophidian Maw*) [P12 a P21]
- **P12 (`Fauce Ofídica + Praga da Corrosão`):** **ELIMINAÇÃO EM CASCATA.** A Praga envenena todos os monstros da sala, fazendo a Fauce devorar instantaneamente qualquer monstro abaixo de 20% de vida.
- **P13 (`Fauce Ofídica + Dádiva de Ula'tek`):** Aumento de 7% no dano total para empurrar a vida dos monstros de elite até a marca de execução rapidamente.
- **P14 (`Fauce Ofídica + Peçonha Insidiosa`):** Pico avassalador de Intelecto que drena a vida do alvo até o ponto de execução imediata.
- **P15 (`Fauce Ofídica + Olhar do Gorgoneion`):** Monstros petrificados em 50% de vida são golpeados com segurança até entrarem na faixa de 20% para a execução.
- **P16 (`Fauce Ofídica + Veneno Amaldiçoado`):** Amplia o dano de veneno sofrido pelos monstros em 25%, acelerando o gatilho de morte.
- **P17 (`Fauce Ofídica + Muco Virulento`):** Permite focar na execução de alvos prioritários sem sofrer dano de monstros secundários.
- **P18 (`Fauce Ofídica + Aperto Viperino`):** Puxa monstros em fuga de volta ao combate para finalizá-los com a mordida executora.
- **P19 (`Fauce Ofídica + Gêiser de Miasma`):** Lança monstros de elite para o alto e os finaliza antes que toquem o chão.
- **P20 (`Fauce Ofídica + Plumagem Lítica`):** Execução segura em combate corpo a corpo com alta mitigação de armadura física.
- **P21 (`Fauce Ofídica + Nuvem Mefítica`):** Enfraquece a precisão dos inimigos enquanto a serpente finaliza os feridos.

### Família 3: Sinergias da Praga da Corrosão (*Plague of Corrosion*) [P22 a P30]
- **P22 (`Praga da Corrosão + Dádiva de Ula'tek`):** Aumenta o dano de todos os pulsos periódicos de veneno espalhados pela sala em +7%.
- **P23 (`Praga da Corrosão + Peçonha Insidiosa`):** Multiplica o dano de veneno em área ao custo de sofrer dano periódico próprio.
- **P24 (`Praga da Corrosão + Veneno Amaldiçoado`):** **MÁXIMO DANO PERIÓDICO.** Os monstros recebem +25% de dano de veneno e cada pulso restaura vida do conjurador.
- **P25 (`Praga da Corrosão + Olhar do Gorgoneion`):** Congela monstros em pedra enquanto a praga continua drenando suas vidas.
- **P26 (`Praga da Corrosão + Muco Virulento`):** Segurança ao puxar salas inteiras em Imersões: 5 camadas protetoras enquanto a praga contagia a todos.
- **P27 (`Praga da Corrosão + Aperto Viperino`):** Puxa todos os alvos para o foco central onde a praga atinge sua maior densidade de dano.
- **P28 (`Praga da Corrosão + Gêiser de Miasma`):** Desorienta os monstros e espalha a praga em múltiplos alvos simultaneamente.
- **P29 (`Praga da Corrosão + Plumagem Lítica`):** Proteção reforçada para suportar múltiplos agressores enquanto o veneno os consome.
- **P30 (`Praga da Corrosão + Nuvem Mefítica`):** Zona de destruição: duas nuvens venenosas ativas ao mesmo tempo ao redor do jogador.

### Família 4: Sinergias da Dádiva de Ula'tek (*Ula'tek's Gift*) [P31 a P38]
- **P31 (`Dádiva de Ula'tek + Peçonha Insidiosa`):** Bônus multiplicativo de dano bruto (+7% total somado a +15% de Intelecto).
- **P32 (`Dádiva de Ula'tek + Olhar do Gorgoneion`):** Dano aumentado consistente com recurso de emergência para sobrevivência.
- **P33 (`Dádiva de Ula'tek + Veneno Amaldiçoado`):** Amplificação de dano geral acompanhada de sustentação contínua de vida.
- **P34 (`Dádiva de Ula'tek + Muco Virulento`):** Aumento direto de poder ofensivo com imunidade a 5 ataques físicos ou mágicos.
- **P35 (`Dádiva de Ula'tek + Aperto Viperino`):** Dano amplificado aplicado em alvos agrupados sob controle de grupo.
- **P36 (`Dádiva de Ula'tek + Gêiser de Miasma`):** Controle de área frequente com amplificação passiva de dano.
- **P37 (`Dádiva de Ula'tek + Plumagem Lítica`):** Equilíbrio sólido entre dano puro (+7%) e proteção corporal (+30% armadura).
- **P38 (`Dádiva de Ula'tek + Nuvem Mefítica`):** Desgaste contínuo aumentado para enfrentar grupos no mundo aberto.

### Família 5: Sinergias do Olhar do Gorgoneion (*Gorgoneion Gaze*) [P39 a P45]
- **P39 (`Olhar do Gorgoneion + Muco Virulento`):** **A FORTALEZA DEFINITIVA.** Combina 5 camadas de imunidade inicial com petrificação em 50% de vida. Excelente para Imersões Tier 11.
- **P40 (`Olhar do Gorgoneion + Peçonha Insidiosa`):** Permite usar o bônus agressivo de Intelecto com a garantia de congelar os monstros se a vida baixar muito.
- **P41 (`Olhar do Gorgoneion + Veneno Amaldiçoado`):** Congela os monstros em pedra e recupera toda a vida através de habilidades periódicas de veneno.
- **P42 (`Olhar do Gorgoneion + Aperto Viperino`):** Agrupa os monstros e os petrifica juntos, permitindo fuga tática ou finalização segura.
- **P43 (`Olhar do Gorgoneion + Gêiser de Miasma`):** Sequência contínua de controle: erupções aéreas seguidas de petrificação em pedra.
- **P44 (`Olhar do Gorgoneion + Plumagem Lítica`):** Mitigação física extrema que previne mortes acidentais por picos de dano.
- **P45 (`Olhar do Gorgoneion + Nuvem Mefítica`):** Reduz o acerto dos monstros e os congela assim que rompem a barreira de 50% de vida.

### Família 6: Sinergias do Muco Virulento (*Virulent Mucus*) [P46 a P51]
- **P46 (`Muco Virulento + Peçonha Insidiosa`):** Anula os primeiros 5 golpes enquanto o conjurador descarrega seu dano máximo com Intelecto ampliado.
- **P47 (`Muco Virulento + Veneno Amaldiçoado`):** Proteção inicial completa que concede tempo hábil para aplicar habilidades de regeneração de vida.
- **P48 (`Muco Virulento + Aperto Viperino`):** Puxa os inimigos para perto com segurança sem sofrer dano de retaliação imediata.
- **P49 (`Muco Virulento + Gêiser de Miasma`):** Neutralização total de perigo nos primeiros 10 segundos de combate contra grupos perigosos.
- **P50 (`Muco Virulento + Plumagem Lítica`):** Excelente para situações em que conjuradores precisam atuar como tanques solo em Imersões.
- **P51 (`Muco Virulento + Nuvem Mefítica`):** Combina imunidade a 5 ataques com névoa que faz os inimigos errarem golpes futuros.

### Família 7: Sinergias de Peçonha Insidiosa, Veneno Amaldiçoado e Utilitários [P52 a P66]
- **P52 (`Peçonha Insidiosa + Veneno Amaldiçoado`):** A autocura do *Veneno Amaldiçoado* anula completamente o dano causado pela *Peçonha Insidiosa*, garantindo +15% de Intelecto permanente sem desvantagens.
- **P53 (`Peçonha Insidiosa + Aperto Viperino`):** Agrupa os inimigos sob lentidão para destruí-los com feitiços potencializados por Intelecto massivo.
- **P54 (`Peçonha Insidiosa + Gêiser de Miasma`):** Interrompe lançamentos inimigos enquanto o bônus de Intelecto finaliza o combate.
- **P55 (`Peçonha Insidiosa + Plumagem Lítica`):** Compensa o atrito sofrido pela peçonha com blindagem reforçada contra golpes corporais.
- **P56 (`Peçonha Insidiosa + Nuvem Mefítica`):** Mitigação passiva que reduz a precisão dos agressores durante janelas de dano máximo.
- **P57 (`Veneno Amaldiçoado + Aperto Viperino`):** Puxa os monstros para dentro do foco de veneno contagioso e maximiza a regeneração.
- **P58 (`Veneno Amaldiçoado + Gêiser de Miasma`):** Arremessa os alvos e os mantém envenenados enquanto recupera a vida do conjurador.
- **P59 (`Veneno Amaldiçoado + Plumagem Lítica`):** Excelente sustentação híbrida para lutas prolongadas contra elites de Imersões.
- **P60 (`Veneno Amaldiçoado + Nuvem Mefítica`):** Desgaste contínuo com geração estável de cura própria a cada pulso de veneno.
- **P61 (`Aperto Viperino + Gêiser de Miasma`):** Combo de controle em área: puxa todos os monstros para o centro e os lança para o ar.
- **P62 (`Aperto Viperino + Plumagem Lítica`):** Puxa os alvos para perto com segurança garantida pelo bônus de armadura física.
- **P63 (`Aperto Viperino + Nuvem Mefítica`):** Mantém os monstros presos dentro da área tóxica de redução de acerto.
- **P64 (`Gêiser de Miasma + Plumagem Lítica`):** Interrupção passiva contra lançadores combinada com proteção física contra lacaios corporais.
- **P65 (`Gêiser de Miasma + Nuvem Mefítica`):** Cegueira temporária acompanhada de névoa constante de erro de ataques.
- **P66 (`Plumagem Lítica + Nuvem Mefítica`):** O combo supremo de mitigação física e passiva para solar conteúdos difíceis no mapa.

---

# PARTE 3: CATÁLOGO OFICIAL DE CONSUMÍVEIS DA SÉRIE 2 (PATCH 12.1)

## 3.1 Comidas e Banquetes (*Food & Feasts*) [Culinária / Cooking]

Todas duram 1 hora, **persistem após a morte** e exigem 10 s sentado comendo para ativar o bônus *Bem Alimentado*.

### Banquetes Coletivos (*Feasts*)

| Item PT-BR | Nome em inglês | ID | Bônus de *Bem Alimentado* |
| :--- | :--- | ---: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_tradeskill_cooking_feastofblood.jpg" width="20" height="20" alt="Parada de Luaprata" /> **Parada de Luaprata** | *Silvermoon Parade* | `255845` | 98 Vigor + **50 de Atributo Primário** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_1h_soup_b_01_misc_1h_soup_b_01.jpg" width="20" height="20" alt="Comemoração de Harandar" /> **Comemoração de Harandar** (vegetariano) | *Harandar Celebration* | `255846` | 98 Vigor + **50 de Atributo Primário** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_10_draconicdelicacies.jpg" width="20" height="20" alt="Mix Quel'dorei" /> **Mix Quel'dorei** | *Quel'dorei Medley* | `242272` | 98 Vigor + **64 do secundário mais alto** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_cooked_greatpabanquet_wok.jpg" width="20" height="20" alt="Banquete Desabrochante" /> **Banquete Desabrochante** (vegetariano) | *Blooming Feast* | `242273` | 98 Vigor + **64 do secundário mais alto** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_legion_heartyfeast.jpg" width="20" height="20" alt="Cornucópia Amani" /> **Cornucópia Amani** | *Amani Cornucopia* | `275264` | (98 × 1,1) Vigor + **(65 × 1,1) do secundário mais alto** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_10_grandbanquet.jpg" width="20" height="20" alt="Coleta dos Loas" /> **Coleta dos Loas** | *Loa's Gathering* | `275265` | (98 × 1,1) Vigor + **(65 × 1,1) do secundário mais alto** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_80_minorfeast.jpg" width="20" height="20" alt="Banquete de Conhecimento" /> **Banquete de Conhecimento** | *Feast of Knowledge* | `275266` | (98 × 1,1) Vigor + **(65 × 1,1) do secundário mais alto** |

**Qual escolher:** para as três specs do projeto, o ganho de Intelecto de um banquete de Atributo Primário já não compensa a perda de secundário — a conclusão é a mesma que o Wowhead registra para magos em Midnight (*"the large item level jump has reduced the value of Intellect relative to Secondary stats"*). Prefira **Mix Quel'dorei / Banquete Desabrochante** (98 + 64) e, quando disponíveis na guilda, **Cornucópia Amani / Coleta dos Loas / Banquete de Conhecimento**, que são os banquetes de qualidade ilvl 90 da Série 2 e escalam ~10% acima dos anteriores.

### Comidas Individuais (*Personal Foods*)

| Item PT-BR | Nome em inglês | ID | Bônus de *Bem Alimentado* |
| :--- | :--- | ---: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_166_bambooshoot02.jpg" width="20" height="20" alt="Costeletas Temperadas com Peçonha" /> **Costeletas Temperadas com Peçonha** | *Venom-Spiced Cutlets* | `275258` | +65 do **secundário mais alto** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_draenor_saltedskulker_color04.jpg" width="20" height="20" alt="Prato de Baiacu" /> **Prato de Baiacu** | *Puffer Plate* | `275260` | +65 do **secundário mais alto** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_draenor_grilledgulper.jpg" width="20" height="20" alt="Espetinhos Agridoces" /> **Espetinhos Agridoces** | *Sweet-And-Sour Skewers* | `275261` | +65 do **secundário mais alto** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_100_sidesalad_color04.jpg" width="20" height="20" alt="Frenesi da Flora" /> **Frenesi da Flora** (vegetariano) | *Flora Frenzy* | `255848` | +64 do **secundário mais alto** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_vendor_poundedricecake_1.jpg" width="20" height="20" alt="Marmita do Campeão" /> **Marmita do Campeão** | *Champion's Bento* | `242274` | +64 do **secundário mais alto** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_100_roastduck.jpg" width="20" height="20" alt="Assado Real" /> **Assado Real** / **Assado Real Impossível** | *Royal Roast* / *Impossibly Royal Roast* | `242275` / `255847` | +50 de **Atributo Primário** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_cooked_valleystirfry.jpg" width="20" height="20" alt="Lula Carmesim" /> **Lula Carmesim** / <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_100_revengeservedcold_color02.jpg" width="20" height="20" alt="Filé Beijado pela Vileza" /> **Filé Beijado pela Vileza** | *Crimson Calamari* / *Fel-Kissed Filet* | `242277` / `242286` | +58 de **Aceleração** *(64 × 0,9)* |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_160_fish_87.jpg" width="20" height="20" alt="Espetinhos Brilhantes" /> **Espetinhos Brilhantes** / <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_10_grandbanquet.jpg" width="20" height="20" alt="Cortes de Sábio da Distorção" /> **Cortes de Sábio da Distorção** | *Glitter Skewers* / *Warped Wise Wings* | `242281` / `242285` | +58 de **Maestria** *(64 × 0,9)* |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_misc_food_cooked_wildfowlroast.jpg" width="20" height="20" alt="Lumitana Dourado ao Sol" /> **Lumitana Dourado ao Sol** / <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_cooking_81_paleosteakandpotatoes_color04.jpg" width="20" height="20" alt="Costeletas Arcanas" /> **Costeletas Arcanas** | *Sun-Seared Lumifin* / *Arcano Cutlets* | `242283` / `242287` | +58 de **Acerto Crítico** *(64 × 0,9)* |

**Regra de decisão:**

1. **Padrão (as três specs):** comida de **maior secundário** (`275258`, `275260`, `275261` = +65). Se o seu maior secundário já é o que você quer empilhar, ela é estritamente melhor que qualquer comida fixa.
2. **Comida fixa** (+58) só entra quando o seu maior secundário **não** é o que você quer — exemplo: Bruxo com Crítico acima de 35% que precisa de Aceleração usa **Lula Carmesim** / **Filé Beijado pela Vileza** mesmo tendo Crítico como maior secundário.
3. Druida do Equilíbrio em dano de área contínuo: **Espetinhos Brilhantes** / **Cortes de Sábio da Distorção** (Maestria).

## 3.2 Frascos de Combate (*Flasks*) [Alquimia / Alchemy]

Duração de 1 hora, **persistem após a morte**. Consumir um frasco idêntico **soma mais 1 hora** (3 s de recarga), então é possível empilhar duração antes da raide.

| Item PT-BR | Nome em inglês | ID | Bônus (+152) |
| :--- | :--- | ---: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_flask_sindoreipotion_white-.jpg" width="20" height="20" alt="Frasco dos Cavaleiros Sangrentos" /> **Frasco dos Cavaleiros Sangrentos** | *Flask of the Blood Knights* | `241325` | **Aceleração** — padrão ofensivo das três specs |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_flask_sindoreipotion_black.jpg" width="20" height="20" alt="Frasco dos Magísteres" /> **Frasco dos Magísteres** | *Flask of the Magisters* | `241323` | **Maestria** — Druida do Equilíbrio e Bruxo com Maestria alta |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_flask_sindoreipotion_red--.jpg" width="20" height="20" alt="Frasco do Sol Partido" /> **Frasco do Sol Partido** | *Flask of the Shattered Sun* | `241327` | **Acerto Crítico** — builds de janela curta e Sacerdote Sombra |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_flask_sindoreipotion_yellow.jpg" width="20" height="20" alt="Frasco da Resistência Talassiana" /> **Frasco da Resistência Talassiana** | *Flask of Thalassian Resistance* | `241321` | **Versatilidade** — chaves +10 ou superior e chefes de dano mágico em área |

**Nota:** os quatro frascos concedem exatamente o mesmo valor (**+152**) do atributo escolhido. A escolha é 100% sobre qual secundário o seu personagem quer, nunca sobre "qual frasco é mais forte".

## 3.3 Poções Ofensivas e de Sobrevivência (*Potions*) [Alquimia / Alchemy]

### Poções de Combate (*Combat Potions*)

| Item PT-BR | Nome em inglês | ID | Efeito oficial (PT-BR) |
| :--- | :--- | ---: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_lightpotion_yellow.jpg" width="20" height="20" alt="Potencial da Luz" /> **Potencial da Luz** | *Light's Potential* | `241309` | +**593 de atributo primário** por 30 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_voidpotion_red.jpg" width="20" height="20" alt="Poção da Imprudência" /> **Poção da Imprudência** | *Potion of Recklessness* | `241289` | +**1.725 do maior secundário** e − **232 do menor secundário** por 30 s |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_voidpotion_purple.jpg" width="20" height="20" alt="Grogue da Impulsividade Desenfreada" /> **Grogue da Impulsividade Desenfreada** | *Draught of Rampant Abandon* | `241293` | +**661 de atributo primário** por 30 s; enquanto durar, *o Caos pode cobrar seu preço, abrindo uma Área de Caos aos seus pés* |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_121_professions_alchemy_potion_amani_blue.jpg" width="20" height="20" alt="Esplendor Líquido" /> **Esplendor Líquido** | *Liquid Luster* | `271886` | aplica **Brilho Lustroso** a cada 6 s por 30 s, +**358 de Versatilidade**; acumula **até 5 vezes** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_121_professions_alchemy_potion_amani_purple.jpg" width="20" height="20" alt="Pancresto Tentador" /> **Pancresto Tentador** | *Alluring Nostrum* | `271889` | por 30 s, suas habilidades de dano têm chance de causar **10.724 de dano de Sombra** no alvo atual **e em até 4 inimigos próximos**; cada acúmulo reduz **15% da velocidade de movimento** (até 5) |

**Qual usar:**

- **Raide de alvo único:** **Potencial da Luz**. É a poção que os guias de classe do Wowhead listam como padrão em raide para conjuradores em Midnight S2.
- **Míticas+ e puxadas grandes:** **Pancresto Tentador**. É a única poção de combate com dano em área embutido — o preço é a perda de mobilidade acumulativa, que em chave alta pode matar.
- **Alternativa de dano puro:** **Poção da Imprudência** (+1.725 de secundário é o maior número isolado da lista). A penalidade de −232 é desprezível quando o seu menor secundário é justamente o que você não quer.
- **Antes do *pull* / fases finais:** **Esplendor Líquido**, se você conseguir manter os 5 acúmulos (são 30 s, um acúmulo a cada 6 s).
- **Grogue da Impulsividade Desenfreada:** **não usar sem coordenação**. A Área de Caos abre no chão sob o seu personagem e é dano evitável que você mesmo cria.

### Poções de Vida (*Health Potions*)

| Item PT-BR | Nome em inglês | ID | Efeito oficial (PT-BR) |
| :--- | :--- | ---: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_alchemy_lightpotion_purple.jpg" width="20" height="20" alt="Poção de Vida de Luaprata Concentrada" /> **Poção de Vida de Luaprata Concentrada** | *Concentrated Silvermoon Health Potion* | `271883` | Restaura **359.499 pontos de vida** (instantâneo) |

O tooltip oficial **não informa a recarga** desta poção. Trate-a como consumível de emergência e não conte com ela como recurso rotineiro de sobrevivência.

## 3.4 Aprimoramentos para Armas / Óleos (*Weapon Enhancements*) [Encantamento / Enchanting]

Duração de 120 minutos, permanecem na arma após a morte:

| Item PT-BR | Nome em inglês | ID | `enchant_id` | Efeito oficial (PT-BR) |
| :--- | :--- | ---: | :--- | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_manaoil_red.jpg" width="20" height="20" alt="Óleo de Fênix Talassiano" /> **Óleo de Fênix Talassiano** (ilvl 278) | *Thalassian Phoenix Oil* | `243733` | `8051` | +**13 de Acerto Crítico** e +**13 de Aceleração** por 120 min |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_manaoil_red.jpg" width="20" height="20" alt="Óleo de Fênix Talassiano" /> **Óleo de Fênix Talassiano** (ilvl 295) | *Thalassian Phoenix Oil* | `243734` | `8052` | +**16 de Acerto Crítico** e +**16 de Aceleração** por 120 min — **óleo de dano, as três specs** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_manaoil_purple.jpg" width="20" height="20" alt="Gume Encantado do Contrabandista" /> **Gume Encantado do Contrabandista** | *Smuggler's Enchanted Edge* | `243737` (278) / `243738` (295) | `8055`/`8056` | O óleo tem chance de ressoar com seu dano, causando **1.002** (278) ou **1.253** (295) de dano Arcano; dura 120 min |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_manaoil_orange.jpg" width="20" height="20" alt="Óleo da Aurora" /> **Óleo da Aurora** (ilvl 278) | *Oil of Dawn* | `243735` | `8053` | Seus **feitiços e habilidades de cura** têm chance de conceder ao alvo uma barreira que absorve **1.503** de dano |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_enchanting_manaoil_orange.jpg" width="20" height="20" alt="Óleo da Aurora" /> **Óleo da Aurora** (ilvl 295) | *Oil of Dawn* | `243736` | `8054` | Mesma barreira, **1.879** de dano absorvido |
| **Olho de Lince do Contrabandista** | *Smuggler's Lynxeye* | a confirmar | `8612`/`8613` | Tooltip do feitiço só informa **~3 procs/min**; efeito não confirmado — ver pendências |

**Correções relevantes desta revisão:**

1. O **Óleo da Aurora** só funciona com **feitiços de cura** — é inútil para Bruxo Demonologia, Sacerdote Sombra e Druida do Equilíbrio em spec de dano. **Correção de uma correção errada:** os itens `243735` (ilvl 278, barreira 1.503) e `243736` (ilvl 295, barreira 1.879) são **duas qualidades do mesmo óleo**, não um ID certo e outro errado. A versão anterior deste guia estava correta ao citar `243736`/1.879.
2. **Óleo e encantamento permanente coexistem.** São camadas diferentes: 1 óleo temporário de 120 min **+** 1 encantamento permanente na mesma arma. O perfil de Mago Gélido 12.1.5 do Maxroll lista os dois juntos (*Enchant Weapon - Arcane Mastery* no item e *Thalassian Phoenix Oil* nos consumíveis). O export do SimC mostra o óleo como `enchant_id` do slot `main_hand`.
3. **Gume Encantado do Contrabandista** é a terceira opção de óleo e faltava neste guia: dano Arcano por proc, sem atributo. Para as três specs, **Óleo de Fênix Talassiano continua sendo a escolha** (+16 Crítico e +16 Aceleração são atributo fixo, não proc).

## 3.5 Runas de Aprimoramento e Runas Vantus [Escrivania / Inscription]

- **Runa de Aprimoramento Tocada pelo Caos (*Void-Touched Augment Rune*, ID `259085`):** +**25 de atributo primário** por 1 hora. É a única runa de aprimoramento de Midnight — o nome "Runa de Aprimoramento Tocada pelo Caos" usado na versão anterior deste guia não existe no jogo. Usar junto do banquete e do frasco.

### Runas Vantus — consumível, insumo e valores oficiais (verificado no tooltip e na receita)

> ⚠️ **Não são duas runas alternativas.** Na Temporada 2 existe **uma única runa Vantus consumível**: a **Runa Vantus: Marés**. A **Runa Vantus: Resplandecente** é **reagente da receita** da Marés — ela é gasta no craft, não concedida como buff.

**1. Consumível de raide da Temporada 2 — Runa Vantus: Marés**

| Runa (PT-BR oficial) | Item | Nível | Bônus de Versatilidade | Alvo do efeito |
| :--- | --: | :-: | --: | :--- |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_vantusrune_lightgreen.jpg" width="20" height="20" alt="Runa Vantus: Marés" /> **Runa Vantus: Marés** (rank 1) | `272194` | 278 | **+130** | chefe selecionado no **Templo de Ula'tek** |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_vantusrune_lightgreen.jpg" width="20" height="20" alt="Runa Vantus: Marés" /> **Runa Vantus: Marés** (rank 2) | `272195` | 278 | **+162** | idem (qualidade superior da criação) |

- O rank é definido pela **qualidade da criação**: qualidade 1 gera `272194`; qualidade 2 gera `272195`.
- **Templo de Ula'tek** é o nome da instância que o projeto chama de **Abismo Peçonhento** (*The Venomous Abyss*) — é a mesma raide, a da Temporada 2.
- Efeito: **uma vez por semana**, harmoniza com o chefe escolhido e o bônus de Versatilidade dura a semana toda.
- **Uso tático:** a runa é **+Versatilidade contra um chefe específico** — não é ganho geral. Vale escolher o chefe onde o grupo tem mais dificuldade, não onde o seu dano é maior.

**2. Insumo de craft — Runa Vantus: Resplandecente**

| Item | ID | Nível | Papel real na Temporada 2 |
| :--- | --: | :-: | :--- |
| Runa Vantus: Resplandecente | `245879` | 278 | **reagente da receita da Marés (1× por craft)** |
| Runa Vantus: Resplandecente | `245880` | 295 | versão de qualidade superior da mesma runa; **não consta como reagente** |

- A Resplandecente tem tooltip de uso próprio, mas os alvos declarados nele são instâncias da **Temporada 1**: Marcha em Quel'Danas, Fenda Onírica, Torre do Caos e Esporasca. **Ela não serve para chefe do Templo de Ula'tek.**
- **Portanto: ignore o "+259 / +324" em qualquer cálculo de raide da Temporada 2.** Esses números nunca entram na conta — o que entra é o **+162** da Marés.
- **Correção:** o nome *Runa Vantus: O Abismo Venenoso* não existe no cliente PT-BR. A runa da raide da temporada é **Runa Vantus: Marés**.
- Receita completa, reagentes e requisitos: [`craft_receitas_s2.json`](craft_receitas_s2.json:1), em `receitas.escrivania.runas_e_consumiveis`.

**3. Receita da Runa Vantus: Marés (Escrivania de Midnight)**

| Reagente | ID | Qtd | Origem |
| :--- | --: | :-: | :--- |
| Água Musical Talassiana (*Thalassian Songwater*) | `245882` | 1 | comerciante |
| Velino do Lexicólogo (*Lexicologist's Vellum*) | `245881` | 1 | comerciante |
| Raiz Petrificada (*Petrified Root*) | `251285` | 2 | Casa de Leilões |
| Globo Pragatado (*Cursebound Globe*) | `274781` | 2 | Casa de Leilões |
| Código de Alma (*Soul Cipher*) | `245766` | 1 | produzido por Escrivania |
| <img src="https://wow.zamimg.com/images/wow/icons/medium/inv_12_profession_inscriptions_vantusrune_gold.jpg" width="20" height="20" alt="Runa Vantus: Resplandecente" /> **Runa Vantus: Resplandecente** | `245879` | 1 | produzido por Escrivania |

- Reagente opcional: **Autenticidade do Artesão** (índice `396`).
- Técnica: [`272196`](https://www.wowhead.com/item=272196/technique-vantus-rune-tides) — exige **Escrivania de Midnight (50)** e **Ranque de Renome 5 com as Forças de Zul'jarra**. Vendida por **Jan'sari, a Vigilante** na Ilha Enrolada por **150 Moxie do Escriba Artesão**.
- ⚠️ **Gargalo de temporada:** o Renome 5 com as Forças de Zul'jarra é o que decide se você tem a runa nas primeiras semanas. Sem ele não há craft, e não há substituto — a Marés é a única runa Vantus válida na raide.

---

# PARTE 4: GUIA DE SITUAÇÕES E VARIANTES ADAPTATIVAS (RAIDE vs MÍTICAS+ vs IMERSÕES / DELVES)

A tabela cruza cada situação de jogo com a combinação recomendada de sistemas rúnicos e consumíveis para as 3 classes. **Todos os códigos `Cxx` desta tabela seguem a numeração de 72 combinações** definida na seção 1.4.

| Situação de Jogo | Druida do Equilíbrio (*Boomkin*) | Sacerdote das Sombras (*Spriest*) | Bruxo Demonologia (*Demo Lock*) |
| :--- | :--- | :--- | :--- |
| **Raide: Chefe de Alvo Único Puro** *(ex: Ula'tek, Nek'zali)* | **Folio:** `C06` (`1A-2A-3A-4B-5C`) — *não arbitrado*<br>**Códice:** Inativo<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Mix Quel'dorei (+64 do secundário mais alto)<br>**Óleo:** Fênix Talassiano<br>**Poção:** Potencial da Luz | **Folio:** `C39` (`1B-2A-3A-4A-5C`) — *não arbitrado*<br>**Códice:** Inativo<br>**Frasco:** Cavaleiros Sangrentos ou Sol Partido<br>**Comida:** Mix Quel'dorei (+64 do secundário mais alto)<br>**Óleo:** Fênix Talassiano<br>**Poção:** Potencial da Luz | **Folio:** `C13` (`1A-2B-3A-4A-5A`) — **confirmado pelo Icy Veins**<br>**Códice:** Inativo<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Mix Quel'dorei (+64 do secundário mais alto)<br>**Óleo:** Fênix Talassiano<br>**Poção:** Potencial da Luz |
| **Raide: Chefe com Inimigos Adicionais Constantes** *(ex: Kith'ix)* | **Folio:** `C08` (`1A-2A-3A-4C-5B`)<br>**Códice:** Inativo<br>**Frasco:** Magísteres (Maestria)<br>**Comida:** Espetinhos Brilhantes<br>**Óleo:** Fênix Talassiano<br>**Poção:** Potencial da Luz | **Folio:** `C02` (`1A-2A-3A-4A-5B`)<br>**Códice:** Inativo<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Lula Carmesim<br>**Óleo:** Fênix Talassiano<br>**Poção:** Potencial da Luz | **Folio:** `C02` (`1A-2A-3A-4A-5B`)<br>**Códice:** Inativo<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Lula Carmesim<br>**Óleo:** Fênix Talassiano<br>**Poção:** Potencial da Luz |
| **Míticas+ Chaves Médias (+2 a +9)** | **Folio:** `C29` (`1A-2C-3A-4B-5B`)<br>**Códice:** Inativo<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Lula Carmesim<br>**Óleo:** Fênix Talassiano<br>**Poção:** Pancresto Tentador | **Folio:** `C61` (`1B-2C-3A-4A-5A`)<br>**Códice:** Inativo<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Lula Carmesim<br>**Óleo:** Fênix Talassiano<br>**Poção:** Pancresto Tentador | **Folio:** `C29` (`1A-2C-3A-4B-5B`)<br>**Códice:** Inativo<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Lula Carmesim<br>**Óleo:** Fênix Talassiano<br>**Poção:** Pancresto Tentador |
| **Míticas+ Chaves Altas (+10 ou mais)** | **Folio:** `C10` (`1A-2A-3A-4D-5A`) — Versatilidade<br>**Códice:** Inativo<br>**Frasco:** Resistência Talassiana<br>**Comida:** Mix Quel'dorei (+64 do secundário mais alto)<br>**Óleo:** Fênix Talassiano<br>**Poção:** Esplendor Líquido | **Folio:** `C46` (`1B-2A-3A-4D-5A`) — Versatilidade<br>**Códice:** Inativo<br>**Frasco:** Resistência Talassiana<br>**Comida:** Mix Quel'dorei (+64 do secundário mais alto)<br>**Óleo:** Fênix Talassiano<br>**Poção:** Esplendor Líquido | **Folio:** `C10` (`1A-2A-3A-4D-5A`) — Versatilidade<br>**Códice:** Inativo<br>**Frasco:** Resistência Talassiana<br>**Comida:** Mix Quel'dorei (+64 do secundário mais alto)<br>**Óleo:** Fênix Talassiano<br>**Poção:** Esplendor Líquido |
| **Imersões Solo: Tier 8 a 10** | **Folio:** `C26` (`1A-2C-3A-4A-5B`)<br>**Códice:** `P12` (Fauce Ofídica + Praga)<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Lula Carmesim<br>**Óleo:** Fênix Talassiano<br>**Poção:** Potencial da Luz | **Folio:** `C61` (`1B-2C-3A-4A-5A`)<br>**Códice:** `P12` (Fauce Ofídica + Praga)<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Lula Carmesim<br>**Óleo:** Fênix Talassiano<br>**Poção:** Potencial da Luz | **Folio:** `C25` (`1A-2C-3A-4A-5A`)<br>**Códice:** `P01` (Ciclo Ourobórico + Praga)<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Lula Carmesim<br>**Óleo:** Fênix Talassiano<br>**Poção:** Potencial da Luz |
| **Imersões Solo: Tier 11 (chefes)** | **Folio:** `C24` (`1A-2B-3A-4D-5C`) — defesa máxima<br>**Códice:** `P39` (Muco + Gorgoneion)<br>**Frasco:** Resistência Talassiana<br>**Comida:** Espetinhos Brilhantes<br>**Óleo:** Fênix Talassiano<br>**Poção:** Poção de Vida de Luaprata Concentrada | **Folio:** `C57` (`1B-2B-3A-4C-5C`)<br>**Códice:** `P24` (Praga + Veneno Amaldiçoado)<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Lula Carmesim<br>**Óleo:** Fênix Talassiano<br>**Poção:** Poção de Vida de Luaprata Concentrada | **Folio:** `C22` (`1A-2B-3A-4D-5A`) — tanque improvisado<br>**Códice:** `P01` (Ciclo Ourobórico + Praga)<br>**Frasco:** Cavaleiros Sangrentos<br>**Comida:** Lula Carmesim<br>**Óleo:** Fênix Talassiano<br>**Poção:** Poção de Vida de Luaprata + Pedra de Vida |

**Nota sobre a linha 4D:** a runa Guerreiro Versátil (*Rune of The Versatile Warrior*) não constava na versão anterior deste guia. Ela é a única opção da linha 4 com mitigação embutida e por isso passou a ser a recomendação padrão para chaves +10 e para Delve Tier 11.

## 4.1 Arbitragem do Folio Ômnico por fonte externa

Em 2026-11-05 as recomendações de Folio foram verificadas contra as fontes que o projeto já utiliza. O resultado muda a recomendação de raide do Bruxo Demonologia.

**Icy Veins (12.1.5), seção *Omnium Folio* do guia de Demonology Warlock:**

- Linha 1: Runa do Fogo Incontido
- Linha 2: Runa de Autorrecomposição **ou** Concha Maculada de Caos
- Linha 3: Runa da Perenidade
- Linha 4: **Runa do Poder Crítico**
- Linha 5: Runa de Energia Residual **ou** Runa de Sobrecarga — *"offer similar output"*

FAQ textual: *"The default choice for Warlocks is Rune of Critical Power. If you have somehow managed to hit >35% Critical Strike chance and neglected Mastery in the process, consider using Rune of Masterful Cunning."*

**MaxRoll:** o guia de M+ de Demonology (atualizado em 2026-10-26) **não possui seção sobre o Omnium Folio**. Não serve para arbitrar.

**Consequência para a matriz acima:**

| Combinação | Código | Situação |
|---|---|---|
| `1A-2B-3A-4A-5A` | **C13** | Padrão confirmado para raide de alvo único |
| `1A-2A-3A-4A-5A` | **C01** | Equivalente, com Carapaça no lugar de Autorrecomposição |
| `1A-2B-3A-4A-5B` | **C14** | Equivalente, com Energia Residual |
| `1A-2A-3A-4A-5B` | **C02** | Equivalente, melhor em grupos densos |
| `1A-2A-3A-4B-5C` | **C06** | **Não suportado**: usa Aceleração Ardente e Ecos, que nenhuma das duas fontes recomenda |

**Regra de troca por atributo:** com Acerto Crítico acima de 35% e Maestria negligenciada, trocar a linha 4 para `4C` (Astúcia Magistral) → `1A-2B-3A-4C-5B` = **C20**.

**Resolvido (2026-11-06):** Shadow Priest e Balance Druid foram conferidos contra as páginas oficiais do Icy Veins 12.1.5. Ambos recomendam exatamente **C13** (1A-2B-3A-4A-5A: Fogo Incontido + Autorrecomposição + Perenidade + Poder Crítico + Sobrecarga) como padrão de alvo único, substituindo em definitivo as menções a C06 e C39.

---

# PARTE 5: LISTA PRÁTICA DE PREPARAÇÃO PARA A MOCHILA (*BAGS CHECKLIST*)

### Preparação para Raide (*Raid Preparation*)
- [ ] 20x **Poção de Vida de Luaprata Concentrada**
- [ ] 20x **Potencial da Luz**
- [ ] 5x **Poção da Imprudência** (reserva para chefes de dano puro)
- [ ] 4x **Frasco dos Cavaleiros Sangrentos**
- [ ] 2x **Frasco da Resistência Talassiana**
- [ ] 1x **Runa Vantus: Marés** (`272195`, +162 Vers) — é a **única** runa Vantus válida na raide da temporada; a Resplandecente (`245879`) é insumo da receita dela, não uma runa alternativa (seção 3.5)
- [ ] 2x **Óleo de Fênix Talassiano**
- [ ] 10x **Runa de Aprimoramento Tocada pelo Caos**
- [ ] **Folio Ômnico configurado:** `C06` para alvo único sustentado; `C02` para controle de adicionais

### Preparação para Míticas+ (*Mythic+ Preparation*)
- [ ] 20x **Poção de Vida de Luaprata Concentrada**
- [ ] 15x **Pancresto Tentador** (puxadas grandes)
- [ ] 10x **Potencial da Luz**
- [ ] 10x **Esplendor Líquido**
- [ ] 10x **Poção da Imprudência** (chefes de chave)
- [ ] 2x **Frasco dos Cavaleiros Sangrentos**
- [ ] 2x **Frasco da Resistência Talassiana**
- [ ] 5x **Costeletas Temperadas com Peçonha** ou **Prato de Baiacu** (+65 do maior secundário)
- [ ] 5x **Lula Carmesim** ou **Filé Beijado pela Vileza** (+58 de Aceleração)
- [ ] 2x **Óleo de Fênix Talassiano**
- [ ] **Óleo da Aurora** — ~~não levar~~: só funciona com feitiços de cura
- [ ] **Folio Ômnico:** `C29` para chaves médias; `C10` para +10 ou superior

### Preparação para Imersões / Delves (*Labirinto de Kindo'jan*)
- [ ] 15x **Poção de Vida de Luaprata Concentrada**
- [ ] 2x **Frasco dos Cavaleiros Sangrentos** ou **Frasco da Resistência Talassiana** (Tier 11)
- [ ] **Configuração do Códice Corrosivo:**
  - Limpeza rápida (Tier 8 a 10): **`P12`** (Fauce Ofídica + Praga da Corrosão) ou **`P01`** (Ciclo Ourobórico + Praga da Corrosão).
  - Chefes (Tier 11): **`P39`** (Muco Virulento + Olhar do Gorgoneion) ou **`P24`** (Praga da Corrosão + Veneno Amaldiçoado).
- [ ] **Folio Ômnico:** `C61` para Sacerdote Sombra; `C26` para Druida; `C22` ou `C24` para Tier 11.

---

## Fontes

- **Wowhead — Omnium Folio Guide:** `https://www.wowhead.com/guide/midnight/omnium-folio-unlock-buffs-rewards` (atualizado 2026-08-06, consultado em 2026-11-05). Fonte dos 13 spell IDs, das 5 linhas, dos nomes oficiais e do texto de efeito de cada runa.
- **Icy Veins / MaxRoll / Method** — conforme registrado em [`talent_builds_season2.json`](talent_builds_season2.json:7).
- **Wowhead PT-BR** — nomes PT-BR de itens, tier sets e chefes.
- **Ferramenta interna:** [`rune_ids_s2.json`](rune_ids_s2.json:1) mantém o de-para canônico entre spell ID, linha, escolha e código Cxx.
