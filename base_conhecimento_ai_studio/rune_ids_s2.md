# Runas do Folio Ômnico — Season 2

> As 13 runas do sistema com os nomes oficiais em português, os IDs de feitiço, o efeito e a fórmula dos códigos `Cxx`.
>
> **Origem:** [`rune_ids_s2.json`](rune_ids_s2.json:1) · **Fonte:** Wowhead PT-BR · **Atualizado:** 2026-11-05

---

## 1. Resumo

| Item | Valor |
| :--- | :--- |
| Linhas da árvore | 5 |
| Total de runas | **13** |
| Combinações possíveis | **72** |
| Cálculo | 2 × 3 × 1 × 4 × 3 = 72 |
| Runas verificadas | **13 de 13** |
| Configuração do seu personagem | **C14** (`1A-2B-3A-4A-5B`) |

---

## 2. Descoberta: cada runa tem dois IDs

As runas de **linha 3 e linha 4** possuem **dois IDs de feitiço** no banco de dados:

- **ID de nó** — é o que aparece nos exports do jogo e do AMR
- **ID de buff** — é o que aparece nos guias

| Runa | ID de nó | ID de buff |
| :--- | :-: | :-: |
| Perenidade | `1287555` | `1287663` |
| Poder Crítico | `1279609` | `1287772` |
| Aceleração Ardente | `1279610` | `1287774` |
| Astúcia Magistral | `1279612` | `1287771` |

> ⚠️ **Consequência prática:** qualquer comparação por ID precisa aceitar **os dois valores**. Comparar contra um único ID gera falso negativo em toda runa de linha 3 e 4. Foi essa descoberta que permitiu decodificar a runa `1279609` do seu export, que estava marcada como desconhecida.

---

## 3. As treze runas

### Linha 1 — Runa Central (*Core*)

| Código | Runa | ID | Efeito |
| :-: | :--- | :-: | :--- |
| `1A` | **Runa do Fogo Incontido** *Rune of Unleashed Fire* | `1279599` | Seus feitiços têm chance de chamar um pilar de fogo, causando dano de Fogo a um inimigo ou restaurando vida de um aliado próximo |
| `1B` | **Runa dos Orbes Tocados pelo Caos** *Rune of Void-Touched Orbs* | `1279596` | A cada 10 s você atrai um orbe do Caos, até 5. Seus ataques lançam os orbes, causando dano Cósmico por orbe. Curas enviam os orbes ao aliado mais ferido |

### Linha 2 — Suporte

| Código | Runa | ID | Efeito |
| :-: | :--- | :-: | :--- |
| `2A` | **Runa da Concha Maculada de Caos** *Rune of Void-Tainted Shell* | `1279604` | Ao sofrer golpe maior que 10% da vida máxima, ganha escudo de absorção. Metade do dano absorvido permanece e é aplicado ao longo de 10 s |
| `2B` | **Runa de Autorrecomposição** *Rune of Self-Mending* | `1279603` | Abaixo de 75% de vida, sua Runa Central também cura você |
| `2C` | **Runa dos Reflexos de Lince** *Rune of Lynxlike Reflexes* | `1279605` | Ao ser atingido em combate, ganha **+77,5** de velocidade por 10 s |

### Linha 3 — Perenidade (*Lingering*)

| Código | Runa | ID de nó | ID de buff | Efeito |
| :-: | :--- | :-: | :-: | :--- |
| `3A` | **Runa da Perenidade** *Rune of Lingering* | `1287555` | `1287663` | A Runa Central deixa um efeito periódico de dano Cósmico ou cura por **8 s**. A Runa Central prioriza alvos ainda não afetados |

### Linha 4 — Atributo secundário

| Código | Runa | ID de nó | ID de buff | Efeito |
| :-: | :--- | :-: | :-: | :--- |
| `4A` | **Runa do Poder Crítico** *Rune of Critical Power* | `1279609` | `1287772` | **+52,7** de Acerto Crítico por 10 s. Acumula |
| `4B` | **Runa da Aceleração Ardente** *Rune of Burning Haste* | `1279610` | `1287774` | **+52,7** de Aceleração por 10 s. Acumula |
| `4C` | **Runa da Astúcia Magistral** *Rune of Masterful Cunning* | `1279612` | `1287771` | **+52,7** de Maestria por 10 s. Acumula |
| `4D` | **Runa do Guerreiro Versátil** *Rune of the Versatile Warrior* | `1279613` | — | **+52,7** de Versatilidade por 10 s. Acumula — texto oficial: "quando a Runa Central (Orbes Tocados pelo Caos) for ativada, concede … Versatilidade por 10 s; várias aplicações podem se sobrepor" |

### Linha 5 — Ápice (*Capstone*)

| Código | Runa | ID | Efeito |
| :-: | :--- | :-: | :--- |
| `5A` | **Runa da Sobrecarga** *Rune of Overload* | `1279614` | **+100%** de eficácia da Runa Central |
| `5B` | **Runa da Energia Residual** *Rune of Residual Energy* | `1279615` | **+100%** de eficácia da Runa da Perenidade |
| `5C` | **Runa dos Ecos** *Rune of Echoes* | `1279616` | A Runa Central deixa uma maldição: após 10 s, repete em **50%** todo o dano e cura das Runas Central e da Perenidade |

---

## 4. Correções de nome aplicadas em 2026-11-05

| O projeto chamava | O nome oficial é |
| :--- | :--- |
| Runa do Fogo Desencadeado | **Runa do Fogo Incontido** |
| Runa das Esferas Tocadas pelo Vazio | **Runa dos Orbes Tocados pelo Caos** |
| Carapaça Maculada pelo Vazio | **Runa da Concha Maculada de Caos** |
| Runa de Autorrecuperação / Runa da Auto-Reparação | **Runa de Autorrecomposição** |
| Runa Remanescente / Runa da Persistência | **Runa da Perenidade** |
| Aceleração Focada (*Focused Haste*) | **Runa da Aceleração Ardente** |
| Ressonância de Maestria (*Mastery Resonance*) | **Runa da Astúcia Magistral** |
| *(não existia)* | **Runa do Guerreiro Versátil** — a quarta opção da linha 4 |

---

## 5. A fórmula dos códigos Cxx

$$C = 36 \times (bloco - 1) + 12 \times (linha_2 - 1) + 3 \times (linha_4 - 1) + (linha_5 - 1) + 1$$

| Variável | Valores |
| :--- | :--- |
| `bloco` | 1 para `1A` · 2 para `1B` |
| `linha_2` | 1 para `2A` · 2 para `2B` · 3 para `2C` |
| `linha_4` | 1 a 4, de `4A` a `4D` |
| `linha_5` | 1 a 3, de `5A` a `5C` |

**Conferência:** `1A-2B-3A-4A-5B` → `0 + 12 + 0 + 1 + 1 = 14` → **C14** ✅

---

## 6. A configuração do seu personagem

O export do AMR traz as runas no formato `<id>=<rank>`. Traduzindo:

| ID | Runa | Linha | Escolha |
| :-: | :--- | :-: | :-: |
| `1279599` | Fogo Incontido | 1 | `1A` |
| `1279603` | Autorrecomposição | 2 | `2B` |
| `1287555` | Perenidade | 3 | `3A` |
| `1279609` | **Poder Crítico** | 4 | `4A` |
| `1279615` | Energia Residual | 5 | `5B` |

**Resultado: `1A-2B-3A-4A-5B` = C14.** A runa `1279609` era a peça que faltava — estava marcada como desconhecida até esta verificação.

**Veredito:** a configuração atual **já coincide** com uma das combinações recomendadas pelo Icy Veins para Demonologia. Não há nada a corrigir no jogo.

---

## 7. Arbitragem entre fontes

| Fonte | Tem a seção? | Recomendação para Demonologia |
| :--- | :-: | :--- |
| **Icy Veins** | ✅ | 1A · 2A ou 2B · 3A · **4A** · 5A ou 5B (*"output similar"*) |
| **Method** | ✅ | 1A · **2C** · 3A · **4A** · **5A** → C25 |
| **MaxRoll** | ❌ | Não tem seção sobre o Folio |
| **Murlok** | ❌ | Não tem seção sobre o Folio |

**Consenso em 3 das 5 linhas:** Fogo Incontido (1A), Perenidade (3A) e Poder Crítico (4A) nas duas fontes.

**Regra do Icy Veins:** com **Crítico acima de 35%** e Maestria negligenciada, trocar para `4C` — Astúcia Magistral.

### Combinações válidas para Demonologia

| Combinação | Código | Situação |
| :--- | :-: | :--- |
| `1A-2B-3A-4A-5A` | **C13** | Padrão de raide |
| `1A-2B-3A-4A-5B` | **C14** | **Sua configuração atual** |
| `1A-2A-3A-4A-5A` | **C01** | Equivalente defensivo, com Concha |
| `1A-2A-3A-4A-5B` | **C02** | Melhor em grupos densos |
| `1A-2C-3A-4A-5A` | **C25** | Indicação do Method, troca cura por mobilidade |
| `1A-2A-3A-4B-5C` | ~~C06~~ | ❌ **Descartado** — ninguém usa Aceleração na linha 4 nem Ecos na linha 5 |

---

## 8. Limitação do export do SimC

O export do SimC **não informa a escolha**. Ele lista 5 nós com rank 1, o que é apenas estado de desbloqueio — todo personagem com o sistema completo exporta os mesmos 5 nós.

A escolha real só aparece no export do **AMR**, e é de lá que veio a configuração da seção 6.

**Decisão do projeto:** não reabrir o parser do AMR. A regra R5 passa a exigir um campo opcional `runas_atuais` no formulário de entrada.

---

## 9. Pendências

| Pendência | Detalhe |
| :--- | :--- |
| **Shadow Priest e Balance Druid** | Runas ainda sem arbitragem externa — as páginas do Icy Veins e do Method desses specs têm a mesma seção |
| ~~Feitiço `1279611`~~ | **Resolvido em 2026-11-06**: o ID **não existe** — HTTP 404 nos dois locales (`node tools/consultar_spells.js 1279611 1279613`), enquanto `1279610`, `1279612` e `1279613` respondem. É buraco de numeração entre `4B` e `4C` |
