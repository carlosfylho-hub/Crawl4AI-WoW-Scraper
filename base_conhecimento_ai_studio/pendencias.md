# Pendências — WoW Calculator (Season 2)

**Última atualização:** 2026-11-06
**Sessão anterior:** auditoria completa contra o Wowhead, correção de atributos, efeitos dos berloques e nomes de consumíveis
**Esta sessão:** resolução integral das pendências em aberto via Firecrawl e tooltips oficiais — runas do Sombra e Druida (Icy Veins C13), recarga de 5 min da poção de vida (spell 1295247), decodificação total das 5 trilhas de bonus_id (128xx) e slots de tier (1369x), bônus 1574/1587/13440/41/12699 classificados, família Cortesão (Courtly 239668–239676), armas de fogo de Engenharia (268475/268477/268479), buff da runa 4D (1287770), berloques 281215 e 270164 mapeados e correção de divergências C06/C29

---

## 1. Correção de uma afirmação errada deste documento

A versão anterior dizia que os três arquivos de spec estavam com **"100% dos atributos numéricos preenchidos"**. Isso era falso.

A auditoria de 2026-11-05 comparou os 93 registros com atributos contra o tooltip oficial e encontrou valores **de 1,9× a 3,9× abaixo do real**. Os números existiam, mas pertenciam a outra escala — provavelmente estimados, não raspados.

**O que foi feito:** todos os 93 registros foram substituídos pelos valores oficiais no **nível máximo de cada item**, com campo `ilvl_referencia` e `stats_fonte` em cada registro.

**Lição:** preenchido não é o mesmo que correto. A partir de agora, todo número de atributo precisa de fonte declarada.

---

## 2. Estado atual dos documentos de dados

| Arquivo | Estado | Observação |
| :--- | :--- | :--- |
| `season2_context.json` | ✅ Corrigido | Bônus de 4 peças em 350/315, sistema Forjado com Peçonha documentado |
| `demonology_warlock.json` | ✅ Corrigido | Berloque de Força removido, substituto passivo adotado, nomes EN corrigidos |
| `shadow_priest.json` | ✅ Corrigido | Nomes EN corrigidos, campo concatenado desmembrado, atributos oficiais |
| `balance_druid.json` | ✅ Corrigido | Nomes EN corrigidos, atributos oficiais |
| `mplus_loot_database.json` | ✅ Corrigido | Errata ajustada, 8 berloques marcados como não utilizáveis por conjurador |
| `delve_loot_kindojan.json` | ✅ OK | Atributos conferidos; rótulos de slot do Pisa-piras a revisar |
| `talent_builds_season2.json` | ✅ Corrigido | Nomes das runas atualizados; códigos de build do Demo duplicados |
| `rune_ids_s2.json` | ✅ Refeito | 13 runas, nomes PT oficiais, IDs duplos mapeados, configuração do personagem decodificada |
| `bonus_ids_s2.json` | ✅ OK | Séries confirmadas, conflito do 4 peças encerrado |
| `stats_oficiais_itens.json` | ✅ Novo | Referência oficial dos 187 itens no nível máximo |
| `auditoria_itens.json` | 📦 Cache | Tooltip cru em inglês dos 190 IDs |
| `auditoria_ptbr.json` | 📦 Cache | Tooltip cru em PT-BR dos 190 IDs |
| `craft_sistemas_s2.json` | ✅ Novo | 91 IDs de embelezamento, missiva e reagente em PT-BR e EN, com a linha “Usável com” |
| `craft_receitas_s2.json` | ✅ Novo | Inventário de receitas craftáveis por profissão, extraído das visões gerais do Wowhead |
| `craft_armas_s2.json` | ✅ Novo | **29** armas craftáveis com nome oficial PT-BR, tipo, nível e atributos |
| `encantamentos_e_gemas_s2.json` | ✅ Novo | 38 encantamentos em 76 IDs, 72 gemas e 6 aprimoramentos de perna em 12 IDs — nome oficial PT-BR e efeito exato |
| `varredura_itens.json` | 📦 Cache | Varredura por faixa de ID (243947–244100, 240860–240990, 273065–273080) |
| `monitor_upgrades_s2.json` | 🆕 Novo (2026-11-06) | **Monitor de armas, pescoços, mão secundária e berloques** separado nos dois tetos: **341** (Mito 6/6 + forja) e **328** (Herói 6/6 + forja). 73 itens em 341, 15 em 328, 4 acima do teto (344) e 136 fora dos tetos |
| `monitor_upgrades_s2.md` | 🆕 Novo (2026-11-06) | Camada de leitura do monitor, com as duas tabelas por teto |
| `enchant_ids_s2.json` | ✅ Novo | Traduz o `enchant_id` do SimC (76 IDs) para o encantamento do catálogo |
| `dados_enchant_ids.csv` | 📦 Cache | DB2 `SpellItemEnchantment` da Wago Tools usado no mapeamento |

### Camada de leitura

> 📌 **Ponto de entrada do projeto:** [`00-INSTRUCOES-IA.md`](00-INSTRUCOES-IA.md:1). É o documento mestre de método — como interpretar os dados, como analisar, os perfis de objetivo (dano, equilibrado, sobrevivência), os cenários (M+, raide, imersão), a hierarquia de decisão e o formato de resposta. Qualquer leitura do projeto começa por ele.

Todos os arquivos de dados têm versão `.md` escrita à mão: [`season2_context.md`](season2_context.md:1), [`demonology_warlock.md`](demonology_warlock.md:1), [`shadow_priest.md`](shadow_priest.md:1), [`balance_druid.md`](balance_druid.md:1), [`mplus_loot_database.md`](mplus_loot_database.md:1), [`delve_loot_kindojan.md`](delve_loot_kindojan.md:1), [`stats_oficiais_itens.md`](stats_oficiais_itens.md:1), [`talent_builds_season2.md`](talent_builds_season2.md:1), [`rune_ids_s2.md`](rune_ids_s2.md:1) e [`bonus_ids_s2.md`](bonus_ids_s2.md:1).

O sistema de criação tem um par próprio: [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1) é a camada de leitura de [`craft_sistemas_s2.json`](craft_sistemas_s2.json:1), de [`craft_receitas_s2.json`](craft_receitas_s2.json:1) e de [`craft_armas_s2.json`](craft_armas_s2.json:1) — estes dois últimos sem `.md` próprio porque inventário é consulta, não prosa.

Encantamentos e gemas têm par próprio também: [`encantamentos_e_gemas_s2.md`](encantamentos_e_gemas_s2.md:1) lê [`encantamentos_e_gemas_s2.json`](encantamentos_e_gemas_s2.json:1), e a descoberta por faixa de ID fica em [`varredura_itens.json`](varredura_itens.json:1).

---

## 3. Pendências em aberto

### 3.1 Runas dos outros dois specs — **RESOLVIDO em 2026-11-06**

| Item | Detalhe |
| :--- | :--- |
| **Shadow Priest** | **RESOLVIDO.** Raspagem oficial do guia Icy Veins 12.1.5 (*Ellipsis*): baseline recomendada é **`1A-2B-3A-4A-5A` (`C13`)** — Fogo Incontido, Autorrecomposição, Perenidade, Poder Crítico e Sobrecarga. A fonte explica que Poder Crítico (`4A`) é a escolha geral para contornar retornos decrescentes (DR) de Aceleração e Maestria nesta fase do patch |
| **Balance Druid** | **RESOLVIDO.** Raspagem oficial do guia Icy Veins 12.1.5 (*Tettles*): baseline recomendada é **`1A-2B-3A-4A-5A` (`C13`)** — Fogo Incontido, Autorrecomposição, Perenidade, Poder Crítico e Sobrecarga |
| **Onde ficou** | Registrado em [`rune_ids_s2.json`](rune_ids_s2.json:1), [`rune_ids_s2.md`](rune_ids_s2.md:1), [`shadow_priest.md`](shadow_priest.md:1), [`balance_druid.md`](balance_druid.md:1) e [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:1) |

### 3.2 Runa Vantus — RESOLVIDO, e corrigido em 2026-11-05

| Item | Detalhe |
| :--- | :--- |
| **Situação anterior** | O nome *Runa Vantus: O Abismo Venenoso* e o bônus de Versatilidade nunca tinham sido conferidos no tooltip |
| **Resolução de nomes e valores** | O nome **não existe** no cliente PT-BR. A runa da raide da temporada é **Runa Vantus: Marés** (`272194` +130 Vers / `272195` +162 Vers, alvo no Templo de Ula'tek) |
| **Erro que a primeira resolução introduziu** | Tratar a **Runa Vantus: Resplandecente** (`245879` +259 / `245880` +324) como *"a outra runa da temporada, com valor muito maior"* |
| **Correção (fonte: receita `1290561`)** | A Resplandecente é **insumo** da receita da Marés — 1× por craft. Não é consumível de buff na Temporada 2. Os alvos da aura dela são instâncias da Temporada 1: Marcha em Quel'Danas, Fenda Onírica, Torre do Caos e Esporasca |
| **Onde ficou** | [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:465) seção 3.5 (consumível × insumo) e [`craft_receitas_s2.json`](craft_receitas_s2.json:1) em `receitas.escrivania.runas_e_consumiveis` |
| **Pendência restante** | ~~Confirmar no jogo qual das duas é a runa da temporada~~ — **resolvida pela receita**: a Marés é a única consumível, e o tooltip dela aponta o Templo de Ula'tek |
| **Gargalo de acesso registrado** | A técnica `272196` exige **Ranque de Renome 5 com as Forças de Zul'jarra**, além de Escrivania de Midnight (50) |

### 3.3 Recarga da poção de vida — **RESOLVIDO em 2026-11-06**

| Item | Detalhe |
| :--- | :--- |
| **Evidência oficial** | Consulta ao feitiço de efeito de item **`1295247`** (*Concentrated Silvermoon Health Potion*): tooltip declara textualmente **"5 min cooldown"** (**5 min de recarga**) |
| **Categoria de recarga** | Pertence à categoria de Poções de Vida (reinicia ao sair de combate), **independente das poções de combate/dano** (Potencial da Luz / Poção da Imprudência) |
| **Onde ficou** | Atualizado em [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:438) |

### 3.4 Cantrips de duas adagas — **RESOLVIDO em 2026-11-06**

| Item | Detalhe |
| :--- | :--- |
| **Situação anterior** | O projeto descrevia os efeitos, mas a leitura anterior do tooltip não trazia linha `Equipar:` |
| **O que o tooltip mostra hoje** | `275070` **Navalha de Lumineira Afiada** — "Equipar: Seus ataques e habilidades de dano bem-sucedidos têm chance de calcinar o alvo, causando **6322 de dano Sagrado**". `273778` **Canalizador de Lumineira Polido** — "Equipar: Seus feitiços bem-sucedidos têm chance de lançar uma partícula de luz … causando **(15807 × 1) de dano Sagrado dividido entre inimigos próximos**, +30% por inimigo adicional até 150%" |
| **Conclusão** | Os textos do projeto estavam **certos**. Os dois itens são 341, Forjado com Peçonha: Mito, e os efeitos estão no tooltip oficial — não vieram de item parecido |
| **Ressalva** | A fórmula `(15807 × 1)` é placeholder do cliente para dano que escala com nível; não tratar como número fixo |

### 3.5 Rótulos de slot do conjunto Pisa-piras — **RESOLVIDO em 2026-11-06**

| Item | Detalhe |
| :--- | :--- |
| **O que parecia erro** | "Cingidouro" marcado como pulsos e "Botinas" como pernas |
| **O que o tooltip diz** | `272238` **Cingidouro do Pisa-piras** → **Pulsos**; `272235` **Botinas do Pisa-piras** → **Pernas** |
| **Conclusão** | O catálogo estava **certo**. O nome "Botinas" (Treads em inglês) descreve uma peça de **pernas** no cliente PT-BR — é estranheza do jogo, não do projeto |
| **Achado novo** | Duas peças diferentes se chamam "Dragonas do Pisa-piras": `272236` (ombros, *Pyrewalker's Mantlet*) e `272225` (costas, *Pyrewalker's Mantle*). Sempre citar o ID junto do nome |

### 3.6 Builds de Demonologia duplicadas — **RESOLVIDO em 2026-11-06**

| Item | Detalhe |
| :--- | :--- |
| **Causa** | Os dois talentos heroicos estavam com o **mesmo código** porque só um tinha sido copiado da página |
| **Fonte reconsultada** | [talent-builds-pve-dps](https://www.wowhead.com/pt/guide/classes/warlock/demonology/talent-builds-pve-dps), autor NotWarlock, atualizado 13/10/2026 — tabela *Demonology Warlock Talent Import Codes* |
| **O que ficou gravado** | Os **8 códigos** (4 por arquétipo: Raid, Raid Cleave, Mythic+, Delves) em `demo_warlock.codigos_wowhead_2026_11_06`. Diabolista repete o mesmo código em Raid Cleave/M+/Delves; Ceifador repete o de Cleave em Delves — **isso é do guia** |
| **Código do Ceifador em M+** | `CoQAAAAAAAAAAAAAAAAAAAAAAYmhZGNbmx2MzYWGAAAAAAgxyyADYAzwSIjNDGLjZmZmZAgZMzYGgZmZmhZ2AAAzMzMjZGsNzAMA` |
| **Código do Ceifador em raide (ST)** | `CoQAAAAAAAAAAAAAAAAAAAAAAYmZMzoZjhZmxsMAAAAAAAjllBGwAmhlQGbmhZ2mlZmZMDAYMzMzAMzMzMmZAAAmZmZmZMDLDAD` |

### 3.7 Série de `bonus_id` — **RESOLVIDO em 2026-11-06**

| Item | Detalhe |
| :--- | :--- |
| **Trilhas de upgrade `128xx`** | **Decodificação completa das 5 trilhas (1/6 a 6/6):**<br>• `12817`–`12822`: **Aventureiro** 1/6 a 6/6<br>• `12825`–`12830`: **Veterano** 1/6 a 6/6<br>• `12833`–`12838`: **Campeão** 1/6 a 6/6 (fechando a lacuna)<br>• `12841`–`12846`: **Herói** 1/6 a 6/6<br>• `12848`: **Ascendente Forjado com Peçonha: Herói** (teto 328)<br>• `12849`–`12854`: **Mito** 1/6 a 6/6<br>• `12856`: **Ascendente Forjado com Peçonha: Mito** (teto 341) |
| **Slots de tier `1369x`** | **Isolados por slot:**<br>• `13690`: **Torso / Peitoral**<br>• `13691`: **Mãos**<br>• `13692`: **Cabeça**<br>• `13693`: **Pernas**<br>• `13694`: **Ombros**<br>• `13695`–`13698`: Marcadores de faixa/dificuldade da raide no tier |
| **Classificação de bônus soltos** | • `41`: Atributo terciário **Sorver (+Leech)**<br>• `13440`: Marcador de procedência **Masmorra Mítico+ (Mythic+)**<br>• `1574`: Nível de **Raide Heroico** (ilvl 321)<br>• `1587`: Nível de **Raide Mítico** (ilvl 334)<br>• `12699`: **Downscale/base de craft** (ilvl 44 sem reagentes de poder) |
| **Onde ficou** | Gravado em [`bonus_ids_s2.json`](bonus_ids_s2.json:1) e documentado em [`bonus_ids_s2.md`](bonus_ids_s2.md:1) |

### 3.8 Feitiço de runa sem nome — **RESOLVIDO em 2026-11-06**

| Item | Detalhe |
| :--- | :--- |
| **ID** | `1279611` |
| **Teste** | `node tools/consultar_spells.js 1279611 1279613` — **HTTP 404 nos dois locales** (PT-BR e EN), enquanto `1279610` (4B), `1279612` (4C) e `1279613` (4D) respondem com nome e efeito |
| **Conclusão** | **Não existe**: é um buraco na numeração entre a 4B e a 4C. Fechado — ninguém precisa procurar de novo |
| **Bônus do teste** | O `1279613` (4D) devolve **Runa do Guerreiro Versátil** com o texto oficial: "+… de Versatilidade por 10 s, várias aplicações podem se sobrepor" — confirma o mecanismo da linha 4 e o empilhamento |

### 3.9 Chave de API exposta — **SANITIZADA em 2026-11-06 (revogação pendente)**

- [x] Chave sanitizada em 2026-11-06 — **AÇÃO MANUAL PENDENTE: revogar/rotacionar no painel Firecrawl**

| Item | Detalhe |
| :--- | :--- |
| **Problema** | A chave do Firecrawl (prefixo `fc` + segredo) foi gravada em `.roo/mcp.json` e também ficou no histórico da conversa |
| **Mitigação** | `.roo/` consta no [`.gitignore`](../../.gitignore:3) criado nesta rodada e o arquivo **não existe** no repositório no momento da auditoria. Varredura textual em todos os arquivos versionáveis (`.env.example`, `docs/`, `plans/`, `data/`, `base_conhecimento_ai_studio/`) **não encontrou nenhuma ocorrência** de chave Firecrawl, `firecrawl` com valor de chave ou `FIRECRAWL_API_KEY` real. O `.env` local também não contém variável `FIRECRAWL` (0 ocorrências) |
| **Identificadores reservados** | Qualquer documentação deve usar `<FIRECRAWL_API_KEY>` / `<REDACTED>` no lugar do valor. Se algum código passar a usar Firecrawl, ler de `os.getenv("FIRECRAWL_API_KEY")` |
| **Ação manual** | **PENDENTE:** revogar a chave atual e gerar uma nova no painel Firecrawl; atualizar o `.env` local. Procedimento completo em [`docs/SEGURANCA.md`](../../docs/SEGURANCA.md:1) |
| **Histórico Git** | **Não executar** `git filter-repo` sem aval explícito: reescreve histórico e exige force-push coordenado. Procedimento documentado (opcional) em `docs/SEGURANCA.md` §3 |

### 3.10 Sistema de craft — pendências abertas

Documento novo: [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1). A regra do teto **331** e do limite de **2 efeitos de embelezamento** (sem limite de peças craftadas) foi registrada nele e em [`season2_context.md`](season2_context.md:1), seção 11.

| Item | Detalhe |
| :--- | :--- |
| **Nomes PT-BR das famílias de craft** | **RESOLVIDO em 2026-11-06.** Varredura de faixa + tooltip PT-BR amarrou nome oficial a ID: **Blood-Tempered = Temperado em Sangue** (`237917`–`237925`, armadura, escudo `237920`), **Dawnforged = Albaforjado** (`237926`/`237927`/`237928`/`237930`/`237931`), **Primalforged = Primeforjado** (`237929`/`237932`), **Thalassian Competitor's = Competidor Talassiano** (`237909`–`237916`), **Aetherlume = Aeterlúmen** (`244744`–`244773`). Gravado em [`craft_armas_s2.json`](craft_armas_s2.json:1) → `familias_ptbr_confirmadas_2026_11_06`. **Ressalva:** são o craft de entrada (ilvl 165–263), não o craft com Centelha (246→331) |
| **Família *Courtly* ** | **RESOLVIDO em 2026-11-06.** Localizado na faixa 239668–239676 de Alfaiataria sob o nome oficial PT-BR **Cortesão**: `239668` Elmo Cortesão, `239669` Luvas Cortesãs, `239670` Cinto Cortesão, `239671` Pulsos Cortesãos, `239672` Vestes Cortesãs, `239673` Sapatilhas Cortesãs, `239674` Manto Cortesão, `239675` Omoplatas Cortesãs, `239676` Calças Cortesãs. Gravado em [`craft_receitas_s2.json`](craft_receitas_s2.json:1) e [`craft_armas_s2.json`](craft_armas_s2.json:1) |
| **Armas de fogo de Engenharia** | **RESOLVIDO em 2026-11-06.** A seção "Reagente para (3)" da página do `273062` (Olho de Cobra Enrolado) foi extraída via Firecrawl. As 3 armas fabricadas por Engenharia são: `268475` **Quebra-coco Evinúcleo** (*Evercore Dome Dinger*, 201 Azul, Eng 35), `268477` **P.O.U. x3** (*P.O.W. x3*, 246 Épica com Centelha, sobe até 331, Eng 90) e `268479` **Rifle do Competidor Talassiano** (*Thalassian Competitor's Rifle*, 263 Verde PvP, Eng 60). Gravado em [`craft_receitas_s2.json`](craft_receitas_s2.json:1), [`craft_armas_s2.json`](craft_armas_s2.json:1) e [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1) |
| **IDs duplicados dos embelezamentos T2** | **RESOLVIDO em 2026-11-06.** Os pares têm **efeito idêntico** e diferem só na linha de dificuldade: `273059`/`273065`/`273068` dizem **“+15 Dificuldade da receita”** e `273060`/`273066`/`273069` dizem **“+5”**. Não são dois itens diferentes: é o par de dificuldade do mesmo reagente |
| **“+1 de Brilho” do Chaveiro da Sorte** | Vem de guia de craft, não do tooltip. Conferir no jogo |
| **Teto 318 vs 331 por qualidade** | A faixa 318–331 do craft mítico depende da qualidade 1–5; falta a tabela de qualidade por rank |
| **Pedra Ritual do Caçador em mão secundária** | O tooltip limita a “Armas de Ferraria de Midnight”, mas guias recomendam na Lanterna de Aln'hara **e um item de jogador foi confirmado com esse proc** (101 de secundário e +50% em Caça às Presas). O catálogo mantém a recomendação de Signo de Negraluna, mas o **item equipado vence** e o conflito fica aberto |
| **Item craftado com secundário “fixo” nas fichas** | As fichas listavam “Missiva: Aceleração + Maestria” como se fosse atributo do item. Craftado **não tem** secundário nem embelezamento fixos (tooltip traz “Atributo Aleatório 1/2”). Corrigido: só os atributos fixos ficam na ficha; secundários e embelezamento passam a ser recomendação + lista de opções |

### 3.11 Profissão da Lanterna de Aln'hara

| Item | Detalhe |
| :--- | :--- |
| **Situação** | As três fichas de spec diziam `Craft (Alfaiataria)` para `245769` |
| **Correção** | A página do item no Wowhead informa **Midnight Inscription** (Escrivania). Já corrigido nas três fichas |
| **Efeito colateral** | O tooltip da Pedra Ritual do Caçador restringe a arma de Ferraria, mas há Lanterna com esse proc em uso — divergência registrada na seção 3.10. O catálogo recomenda Signo de Negraluna para mão secundária e aceita o item do jogador como evidência |

### 3.12 Armas, encantamentos e gemas

Documentos: [`encantamentos_e_gemas_s2.md`](encantamentos_e_gemas_s2.md:1) e a seção 7.1 de [`craft_sistemas_s2.md`](craft_sistemas_s2.md:1). **Todos os nomes são cópia literal do tooltip PT-BR**, nunca tradução do projeto.

| Item | Detalhe |
| :--- | :--- |
| **Encantamento de pulsos, mãos e capa** | A varredura de 243700–244037 **não encontrou** nenhuma receita de Midnight para esses slots. Falta confirmar no jogo se ficaram sem encantamento na temporada |
| **Pernas não recebem encantamento** | Usa **Magilinha** (*Spellthread*, Alfaiataria) ou **Kit de Armadura** (Couraria): 6 nomes em 12 IDs, já catalogados. Nenhum é encantamento |
| **Cada encantamento tem duas qualidades** | 38 nomes em 76 IDs. Quem lista só um ID lista metade do catálogo |
| **Armas sem ID confirmado** | **RESOLVIDO em 2026-11-06.** IDs e nomes PT-BR em [`craft_armas_s2.json`](craft_armas_s2.json:1): `237916` **Espada do Competidor Talassiano** (*Thalassian Competitor's Sword*), `237914` **Espeto do Competidor Talassiano** (*… Skewer*), `237913` **Talhadeira do Competidor Talassiano** (*… Splitter*), família **Albaforjado** (Dawnforged) e **Primeforjado** (Primalforged) completas, escudo **Baluarte Temperado em Sangue** (`237920`) |
| **Armas de fogo de Engenharia** | **RESOLVIDO em 2026-11-06.** Raspada com Firecrawl a aba "Reagente para (3)" de `273062`. Os 3 IDs de armas de Engenharia são: `268475` (Quebra-coco Evinúcleo, Azul), `268477` (P.O.U. x3, Épica) e `268479` (Rifle do Competidor Talassiano, PvP). Catalogados em armas e receitas |
| **`Rito dos Hash'ey` com nível 580** | **RESOLVIDO em 2026-11-06.** O 580 é o **nível do pergaminho**, não outra trilha: a receita é **`273073` Fórmula: Rito dos Hash'ey**, no mesmo bloco 273059–273073 das outras receitas de Midnight, na especialização **Aprimoramentos Amani — Zelo de Zul'Aman**. Duas qualidades: `273071` (120) e `273072` (139) |
| **Valor de dano em fórmula** | Alguns encantamentos de arma mostram o dano como `(1 * N)` no tooltip; o número final depende do nível do personagem |
| **Gemas `Amani` da página de Joalheria** | `Pedra Amani Perfurante`, `Peridoto Amani Opalescente` e `Granada Amani Rugidora` são **decoração de casa**, não gema de combate |
| **`enchant_id` do SimC ≠ ID do pergaminho** | O export traz a linha de `SpellItemEnchantment` (uma por qualidade). Mapeados **76 IDs** em [`enchant_ids_s2.json`](enchant_ids_s2.json:1) via [`tools/mapear_enchant_ids.js`](tools/mapear_enchant_ids.js:1). Ex.: `7981` = Precisão de Jan'alai **Tier 2** (`243971`) |
| **Magilinha e Kit de Armadura fora do DB2** | As 3 Magilinhas e os 3 Kits de Midnight não aparecem na tabela `SpellItemEnchantment` deste build; se vierem em `enchant_id`, resolver pelo nome na seção 2.2 de [`encantamentos_e_gemas_s2.md`](encantamentos_e_gemas_s2.md:1) |
| **`Olho de Lince do Contrabandista` (`8612`/`8613`)** | **RESOLVIDO em 2026-11-06.** O **item** existe e é o `257747`: “Uso: Encanta permanentemente uma arma de longo alcance para aumentar em **15** de forma esporádica a Maestria.” Fabricado por Engenharia de Midnight (habilidade 70), nível do item 1, requer nível 81. Fica em [`encantamentos_e_gemas_s2.json`](encantamentos_e_gemas_s2.json:1) → `mira_de_arma` |
| **`R0CKY` como encantamento de elmo** | Enchant `8702` / item `275676` — reduz a velocidade de queda por 2 min e **ocupa a linha de encantamento do elmo**, competindo com Evasão (+37) e Velocidade (+22). Confirmado por fórum oficial e tooltip |
| **Óleo + encantamento permanente** | Coexistem (camadas diferentes). Evidência: guia de Mago Gélido 12.1.5 do Maxroll lista `Enchant Weapon - Arcane Mastery` no item **e** `Thalassian Phoenix Oil` nos consumíveis |
| **Óleos têm DUAS qualidades (dois IDs)** | Fênix Talassiano = `243733` (278, +13/+13) e `243734` (295, +16/+16); Óleo da Aurora = `243735` (278, 1.503) e `243736` (295, 1.879); Gume = `243737` (1.002) e `243738` (1.253). **Não existe “ID errado”**: o erro é tratar a qualidade baixa como se fosse a única. Corrigido em [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:1) §3.4, com retratação registrada em [`auditoria_ptbr.md`](auditoria_ptbr.md:1) |
| **Escopo dos encantamentos de ferramenta** | 6 encantamentos de ferramenta (12 IDs) mapeados em [`enchant_ids_s2.json`](enchant_ids_s2.json:1) com nome PT-BR; ficam fora do cálculo de combate |

### 3.13 Runas do Folio — conflitos internos e lacuna de ID

| Item | Detalhe |
| :--- | :--- |
| **Conflito 2B × 2C** | A matriz situacional de [`consumiveis_e_sistemas_s2.md`](consumiveis_e_sistemas_s2.md:1) indica **`C29`** (com `2C`) para M+ médias e **`C26`** (com `2C`) para imersão Tier 8–10, mas a nota “Linha 2” logo abaixo lista **“2B ou 2A”**. Conflito interno, não resolvido pela fonte |
| **`2C` não é mitigação** | O efeito é **+77,5 de velocidade de movimento** por 10 s ao ser atingido — reposicionamento. A frase “`2C` brilha em imersão porque você toma dano” existia em [`00-INSTRUCOES-IA.md`](00-INSTRUCOES-IA.md:1) e foi corrigida: quem defende é `2A` (absorção) e `2B` (autocura) |
| **`4D` com `id_buff`** | **RESOLVIDO em 2026-11-06.** O ID do buff da **Runa do Guerreiro Versátil** é **`1287770`**, com tooltip oficial: "Quando a sua Runa Central for ativada, concede +52,7 de Versatilidade por 10 s; várias aplicações podem se sobrepor". Atualizado em [`rune_ids_s2.json`](rune_ids_s2.json:1) e [`rune_ids_s2.md`](rune_ids_s2.md:1) |
| **`C23` vs `C24`** | `C23` (`1A-2B-3A-4D-5B`) e `C24` (`1A-2B-3A-4D-5C`) diferem só na linha 5: `5B` amplia a Perenidade em 100%, `5C` ecoa 50% do dano/cura após 10 s. A matriz escolhe **`C24`** para Tier 11; `C23` é descrita como “solo de alto risco” |

### 3.14 Suplício e Destruição — avaliação contra Demonologia (2026-11-06)

| Item | Detalhe |
| :--- | :--- |
| **Pergunta** | Suplício (*Affliction*) e Destruição (*Destruction*) do Bruxo valem a pena em Delve, raide, Caçada, Ilha Enrolada ou M+? |
| **Fontes usadas** | Icy Veins (Motoko, 12/10/2026), Method (Omnithic, 13/10/2026) e Murlok top 50 de M+ (Battle.net API) |
| **Resultado (M+)** | **Nenhuma das duas é melhor.** Rating do top 50 no Murlok: Demo **3994–4248** (50/50 em Diabolista), Destruição **3646–4152**, Suplício **3732–4031** |
| **Resultado (raide)** | Tier list 12.1.5 do Icy Veins: Demo **S**, Suplício **A**, Destruição **B** |
| **Resultado (Delve)** | Tier list de Delves S2 (ExpCarry, 05/09/2026): Demo **S** nas duas listas · Suplício **A** nas duas · Destruição **A** semanal e **B** em Tier 8–11 |
| **Kindo'jan Tier 11** | Na lista de **progressão Tier 8–11** — a faixa do Kindo'jan — **Demonologia é a única spec de Bruxo em S**; Suplício **A**; Destruição **B**. A fonte justifica o B: no Tier 10+ "um interrupt perdido ou janela fraca de recuperação é punido muito mais duro". Registrado em `warlock_outras_specs.comparativo_por_cenario.kindojan_tier11` |
| **Onde cada uma ganha** | Destruição: raide com **2 alvos constantes** (Havoc/Mayhem). Suplício: Caçada e Delve solo de risco, por Drenar Vida aprimorado + Drenar Essência (−25% de dano recebido) e Maldição do Sátiro |
| **Onde ficou gravado** | [`talent_builds_season2.md`](talent_builds_season2.md:90) e `warlock_outras_specs` em [`talent_builds_season2.json`](talent_builds_season2.json:1), com os 9 códigos de importação das duas specs |
| **Lacuna de fonte** | **Murlok não publica raide nem Delve** — só M+ e PvP. Raide e Delve passaram a ter **tier list de spec** (Icy Veins e ExpCarry), mas nenhuma delas publica **número de DPS** comparando as três. **Caçada não tem tier list nenhuma** — ali o veredito é só por mecanismo |
| **Qualidade da fonte de Delve** | ExpCarry e Skycoach são sites de serviço (boosting). O ExpCarry informa data (05/09/2026) e base (4 semanas de conteúdo jogado) e traz nota por spec em Semanal / Alto / Azta'rec — por isso foi usado como desempate. **Não** substitui simulação |
| **Erro de rota registrado** | `murlok.io/warlock/<spec>/mythic+` devolve **404**; o caminho correto é `murlok.io/warlock/<spec>/m+` |
| **`/solo` do Murlok NÃO é Delve** | `murlok.io/warlock/affliction/soul-harvester/solo` é **Solo Shuffle (PvP de arena)**: prioridade Versatilidade > Aceleração > Maestria > Crítico, rating 2799–3296, talents JxJ e gear PvP. O Murlok **não tem** página de Delve nem de raide. Quem quer build de Delve solo usa o Wowhead |
| **Builds de raide e Delve do Suplício** | Gravadas em `warlock_outras_specs.affliction_suplicio.codigos_wowhead_para_raid_e_delve`, fonte [Wowhead PT — Affliction](https://www.wowhead.com/pt/guide/classes/warlock/affliction/talent-builds-pve-dps) (Kalamazi, 17/10/2026): **Hellcaller** para raide, **Ceifador de Almas** para Delve solo e M+ |
| **Conflito de talento heroico do Suplício** | O Wowhead afirma no resumo que Hellcaller é o mais forte "em alvo único e em Mythic+" e, na seção de M+, que Soul Harvester é a melhor opção. Icy Veins e Method dizem que Soul Harvester domina tudo. Murlok top 50 de M+: **27 Ceifador × 23 Hellcaller**. Resolução registrada no JSON: Ceifador para M+/Delve, Hellcaller para raide de alvo único |
| **Detalhe do guia** | No Method, o código de "Diabolist (Cleave)" da Destruição é **idêntico** ao de "Hellcaller (Single Target)" — é do guia, não erro de extração |

### 3.15 Bruxo Suplício — ficha criada e divergências encontradas (2026-11-06)

| Item | Detalhe |
| :--- | :--- |
| **Novo documento** | [`affliction_warlock.md`](affliction_warlock.md:1) e [`affliction_warlock.json`](affliction_warlock.json:1) — prioridade de atributos, talentos por cenário, armadura do top 50, embelezamentos, encantamentos, gemas, Folio Ômnico e Códice Corrosivo |
| **Fonte da armadura** | Murlok top 50 de M+ do Suplício (frequência de uso por peça) + nomes PT-BR do banco do projeto. Sete itens não existiam no banco local e foram resolvidos pelo tooltip oficial (`nether.wowhead.com/tooltip/item`) e gravados em [`tools/_nomes_faltantes_suplicio.json`](tools/_nomes_faltantes_suplicio.json:1) |
| **Diferencial vs Demonologia** | O Suplício usa **5 peças** do conjunto Necrólito Maldito (44/50 mantêm a cabeça do tier); a Demonologia troca a cabeça pelo cantrip Capucho Horrendo do Guardião da Peçonha |
| **Recorte sem raide** | O usuário não joga raide. A ficha ganhou `bis_sem_raide` e `arma_sem_raide` com M+/Delve/craft/Catalyst. **Itens de raide que precisaram de substituto:** Jan'thrazet 271092 (Ula'tek), Relicário Aqiricida 268265 (Ula'tek), Elo do Chama-enxame 281029 (Kith'ix), Capucho da Peçonha 271874 (Ula'tek). Substitutos: Canalizador de Lumineira Polido 273778, Feixe de Presas Protetoras 273781, Elo do Senhor da Guerra Amani 273792 |
| **Arma + Lanterna** | A Lanterna de Aln'hara ocupa a mão secundária, então a arma principal **tem de ser de uma mão**. Três adagas de 341 saem de M+ (273778 Altar das Presas, 159137 Descanso do Rei, 251225 Arena da Chaga do Caos) e duas de Delve (272266, 272270) ficam em 328 |
| **Origem dos berloques confirmada** | **RESOLVIDO em 2026-11-06.** `281215` (Tentáculo do Terror Pervertido) cai de **Kith'ix** na raide *The Unbinding of Kith'ix*; `270164` (Bolsa sem Fundo de Gebbo) cai de **Mor'zahi** (encontro Exploradores Perdidos) na raide *The Venomous Abyss*. Ambas confirmadas como fontes de raide |
| **Dossiê de Delves raspado (06/11/2026)** | 6 fontes pedidas pelo usuário. **Só 3 publicam build de Delve.** Icy Veins Destruction tem a seção mas **não expõe o código**; Method Affliction **não tem** build de Delve; o YouTube `xgllW-GHybY` é guia de **Assistente de Botão Único de 31/03/2026**, **anterior ao 12.1**, logo desatualizado e sem conteúdo de Delve. Gravado em `dossie_delves_bruxo` no [`talent_builds_season2.json`](talent_builds_season2.json:1) e em [`talent_builds_season2.md`](talent_builds_season2.md:152) |
| **Reddit é bloqueado pelo Firecrawl** | `reddit.com` e `old.reddit.com` retornam "we do not support this site". A thread `1tv79ig` entrou apenas por **trechos de busca**: "Soul Harvester Affliction with a Voidwalker to tank"; "Voidwalker is the best pet but it will go down, save the instant summon". Nenhuma discussão completa foi lida |
| **Convergência rara (registrar)** | Icy Veins (Delves) e ExpCarry (Delve Build) publicam **literalmente o mesmo código** de Delve do Suplício, com Ceifador de Almas. É a recomendação de build mais bem sustentada do acervo |
| **Bônus de tier do Suplício — RESOLVIDO por tooltip oficial** | Puxado o conjunto `2066` "Grilhões Despedaçados do Necrólito Maldito" no [Wowhead PT](https://www.wowhead.com/pt/item-set=2066) em 06/11/2026. **2 peças (Suplício):** Murchar/Corrupção +25% e Agonia +15%. **4 peças (Suplício):** "Cada Agonia Instável ativa aumenta em 2% o dano, até 6%; a Semente da Corrupção aplica Agonia Instável ao alvo com 20% de eficácia". **Veredito: o ExpCarry estava certo**; o Method descreveu só metade do efeito (incompleto, não errado). Spells `1296568` (2pc) e `1296569` (4pc) |
| **Correção de nome PT (06/11/2026)** | O nome PT de *Unstable Affliction* é **Agonia Instável**, não "Ferida Instável". "Agonia" sozinho é *Agony*. Nome corrigido em 5 arquivos: [`affliction_warlock.md`](affliction_warlock.md:1), `affliction_warlock.json`, [`talent_builds_season2.md`](talent_builds_season2.md:1), `talent_builds_season2.json` e neste `pendencias.md` |
| **Rodada 2 de raspagem (06/11/2026)** | YouTube `JuesXj34o-4` (TheWoWCasual, 21/08/2026): Demonologia no top 5 de Delves, **sem talentos** — só ranking de classe. Method `/guides/affliction-warlock` (13/10/2026): **confirma que não existe build de Delve** no guia; em troca documenta a mudança de talentos do 4 peças (removeu Patient Zero e Nocturnal Yield) |
| **Build de Delve da Destruição — obtida** | O Icy Veins não publica o código, mas raspando os **LINKS** da página saem as 5 builds do calculador na ordem das seções; a **5ª é a de Delve**. Link gravado em `dossie_delves_bruxo.destruction_delve.icy_veins_link_calculadora`. O código de import continua vindo do Wowhead |
| **Divergência 1 — Folio C06** | **RESOLVIDO em 2026-11-06.** Decidido pelo consenso das fontes: `C06` é descartado como não suportado e a checklist de raide foi corrigida para indicar **`C13`** (ou `C14`) para alvo único |
| **Divergência 2 — tag do C23** | **RESOLVIDO em 2026-11-06.** Corrigida a tag em [`guia_masmorras_e_delves_s2.md`](guia_masmorras_e_delves_s2.md:261) para **`C29`** (`1A-2C-3A-4B-5B`), eliminando a divergência |
| **Lacuna — bônus de tier do Suplício** | Texto de 2/4 peças específico do Suplício não está no acervo. As peças são as mesmas da Demonologia, mas o efeito do spec não foi capturado |
| **Lacuna — Folio por spec** | Nenhuma fonte publica recomendação de Folio por spec. A matriz é class-wide (FAQ do Icy Veins para Bruxo), e a ficha registra isso explicitamente em vez de inventar diferença |

### 3.16 Monitor de upgrades — como usar e o que ainda falta

| Item | Detalhe |
| :--- | :--- |
| **O que foi criado** | [`tools/monitorar_upgrades.js`](tools/monitorar_upgrades.js:1) varre IDs no tooltip oficial e guarda **só** arma, pescoço, mão secundária, escudo e berloque; [`tools/gerar_doc_monitor_upgrades.js`](tools/gerar_doc_monitor_upgrades.js:1) separa os baldes **341** e **328** e escreve o `.md` |
| **Fonte** | `nether.wowhead.com/tooltip/item` locale `8` (PT-BR) + locale `0` (EN) — **zero créditos** Firecrawl |
| **Regra dos tetos** | `341` = Mito 6/6 (**334**) + Forjado com Peçonha (**+7**); `328` = Herói 6/6 (**321**) + Forjado com Peçonha (**+7**). Só entra no balde quem declara exatamente esse nível |
| **Cuidado** | O tooltip padrão do Wowhead mostra **um** nível por item. O mesmo item aparece em 341 e em 328 mudando só o `bonus_id`; por isso os dois baldes listam **IDs diferentes** |
| **Cobertura atual** | Faixas varridas: 250100–250300, 251100–251250, 268150–268280, 270150–270180, 272200–272300, 273640–273660, 273780–273800, 275050–275090 + todos os IDs já catalogados no projeto (605) |
| **Lacuna** | Se a temporada ganhar itens novos em faixas não varridas, o monitor não os vê. Rodar de novo com a faixa nova resolve — os dois scripts são idempotentes |
| **Série de `bonus_id` (3.7)** | **RESOLVIDO em 2026-11-06.** Todas as 5 trilhas `128xx` mapeadas (incluindo Campeão `12833`–`12838` e os dois tetos forjados `12848` e `12856`); slots de tier `13690`–`13694` isolados; e bônus `13440`, `12699`, `41`, `1574` e `1587` classificados |

---

## 4. O que já está resolvido e não precisa mais ser verificado

| Item | Resolução |
| :--- | :--- |
| **Runa `1279609`** | É a **Runa do Poder Crítico** (linha 4A) |
| **Nomes PT-BR de todos os itens** | Conferidos contra o Wowhead PT: **0 divergências reais** |
| **Nomes EN de 13 itens** | Corrigidos, incluindo `Speakeasy Shroud` e `Hex Lord's Dooming Idol` |
| **Nomes PT de `251132` e `270169`** | **Estavam certos**: Mortalha do Inferninho e Ídolo da Perdição do Grão-bagateiro |
| **ID da Astúcia Magistral** | `1279612` é o nó e `1287771` é o buff — **os dois estão corretos** |
| **Bônus de 4 peças do Bruxo** | **350%/315%**, confirmado pelo texto oficial do conjunto `2066` |
| **Berloque de Força como BiS de conjurador** | Removido de todos os arquivos; **10 berloques** do banco de M+ marcados com `usavel_por_conjurador: false`, incluindo os dois reclassificados nesta revisão (`273797` e `250228`) |
| **Configuração de runas do personagem** | `1A-2B-3A-4A-5B` = **C14**, já dentro do recomendado |
| **Efeitos dos berloques** | **20 textos corrigidos** em 4 arquivos JSON. 16 efeitos tinham número inventado (ex.: Emblema de Dazar dizia +129 de Aceleração e o oficial é +1.082) e 9 omitiam número do tooltip |
| **Nomes dos consumíveis** | **15 nomes estavam errados** e foram trocados pelos oficiais PT-BR; 2 poções que faltavam foram adicionadas; o Óleo da Aurora foi retirado da recomendação de DPS porque só proca com feitiços de cura |
| **Berloques que só dão Força/Agilidade** | `tools/conferir_primario_berloques.js` confere os 19 berloques do banco de M+ contra o tooltip: **0 problemas** |
| **Armaduras de tecido e couro + armas** | `tools/auditar_armaduras.js` conferiu **85 entradas** (nomes PT, nomes EN, slot, tipo de armadura, primário e combo de secundários) contra os dois locales: **0 divergências** |
| **Valores reais das armaduras** | As seções de armadura só tinham uma escala relativa 0–10. `tools/injetar_stats_armaduras.js` gravou `stats_oficiais` com os valores de jogo das **85 peças** |
| **Regra do Matrix Catalyst** | Documentada em `visao_geral_temporada.catalyst` e cruzada com a decisão de Voidcore em R9 e R12 |

---

## 5. Notas técnicas

| Assunto | Detalhe |
| :--- | :--- |
| **Coleta de dados** | O endpoint `nether.wowhead.com/tooltip/` responde a requisições locais. Toda a auditoria de 190 itens rodou **sem consumir créditos Firecrawl** |
| **Locale PT-BR** | É o `8`. O `0` é inglês e o `3` é alemão |
| **Pegadinha do locale PT** | Em **64 itens** o tooltip em português imprime a linha `??? Atributo não utilizado (+N)` no lugar de `Aumenta o índice de versatilidade em +N`. O tooltip em inglês mostra `+N Versatility`. Nunca leia o conjunto de secundários do texto cru em PT: use os campos parseados ou o tooltip EN |
| **Scripts** | [`tools/audit_itens.js`](tools/audit_itens.js:1), [`tools/audit_ptbr.js`](tools/audit_ptbr.js:1), [`tools/compare_auditoria.js`](tools/compare_auditoria.js:1), [`tools/corrigir_nomes.js`](tools/corrigir_nomes.js:1), [`tools/gerar_stats_oficiais.js`](tools/gerar_stats_oficiais.js:1), [`tools/injetar_stats.js`](tools/injetar_stats.js:1), [`tools/auditar_efeitos.js`](tools/auditar_efeitos.js:1), [`tools/corrigir_efeitos.js`](tools/corrigir_efeitos.js:1), [`tools/corrigir_consumiveis.js`](tools/corrigir_consumiveis.js:1), [`tools/conferir_primario_berloques.js`](tools/conferir_primario_berloques.js:1), [`tools/consultar_ids.js`](tools/consultar_ids.js:1), [`tools/auditar_armaduras.js`](tools/auditar_armaduras.js:1), [`tools/injetar_stats_armaduras.js`](tools/injetar_stats_armaduras.js:1) — todos re-executáveis e idempotentes |
| **Scripts novos (2026-11-06)** | [`tools/consultar_spells.js`](tools/consultar_spells.js:1) (tooltip de feitiço em PT e EN), [`tools/varrer_armas.js`](tools/varrer_armas.js:1) (só armas por faixa), [`tools/listar_faixa.js`](tools/listar_faixa.js:1) (todos os itens de uma faixa, com filtro por nome), [`tools/monitorar_upgrades.js`](tools/monitorar_upgrades.js:1) e [`tools/gerar_doc_monitor_upgrades.js`](tools/gerar_doc_monitor_upgrades.js:1) — todos leem só `nether.wowhead.com` |
| **Créditos Firecrawl nesta sessão** | **6** — três páginas de guia/profissão que a varredura não cobria (builds do Demo, hub de Engenharia, lista de armas) e uma busca de item. Todo o resto saiu do endpoint gratuito |
| **Créditos gastos na sessão** | Cerca de 31 nas raspagens iniciais; **zero** na auditoria e nas verificações seguintes |
| **Detalhe da auditoria** | [`auditoria_ptbr.md`](auditoria_ptbr.md:1) registra cada correção com evidência |
