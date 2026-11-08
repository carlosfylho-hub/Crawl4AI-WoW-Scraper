# Modificadores e Tracks de Item — Season 2

> O que cada série de `bonus_id` do export do SimC significa, e como descobrir o track de um item sem adivinhar.
>
> **Origem:** [`bonus_ids_s2.json`](bonus_ids_s2.json:1) · **Atualizado:** 2026-11-05

---

## 1. O método que funciona

Não adivinhe séries de `bonus_id`. Consulte o **tooltip do item com a lista exata de bônus** que veio no export:

```
https://nether.wowhead.com/tooltip/item/<id>?dataEnv=1&locale=8&bonus=<id>:<id>:<id>
```

| Parâmetro | Valor |
| :--- | :--- |
| `bonus` | lista de `bonus_id` separada por dois-pontos, na ordem do export |
| `locale` | **8** para PT-BR · 0 para inglês · 3 para alemão |
| `dataEnv` | 1 — dados atuais |
| Custo | 1 crédito por item pelo Firecrawl, **ou zero** chamando direto pelo Node |

O retorno traz nome, nível de item, **rótulo do track** e o texto completo do efeito, com todos os bônus já aplicados.

---

## 2. Série `128xx` — track de upgrade

| Valor | Track | Nível observado | Item de prova |
| :-: | :--- | :-: | :--- |
| `12846` | **Herói 6/6** | 321 | `271546` — Crânio do Necrólito Maldito |
| `12854` | **Mítico 6/6** | 334 | `271543` — Cilha Tilintante do Necrólito Maldito |
| `12856` | **Mítico (dificuldade de raide)** | 341 | `273781` — Feixe de Presas Protetoras |

### O achado que invalidou a heurística anterior

`12854` e `12856` produzem o **mesmo rótulo "Mythos"** com níveis **diferentes** (334 e 341). O rótulo **não** distingue track de dificuldade.

Conclusão: **o nível de item é a âncora**, e o `bonus_id` só serve como desempate. Nunca derive o track lendo o `bonus_id` isolado.

---

## 3. Série `1369x` — marca de peça de tier

Valores observados: `13690` a `13698`.

| Item | Resultado |
| :--- | :--- |
| `271546` com bônus `13692`, `13695` e `13698` | O tooltip listou o conjunto `(0/5)` com os bônus de 2 e 4 peças por spec |

**Limitação:** não foi possível isolar **qual** dos três IDs é o marcador. A detecção confiável de tier é pela **pertinência ao conjunto no texto do tooltip**, ou por mapa explícito de ID — nunca pela série sozinha.

---

## 4. IDs ainda não classificados

| ID | Onde aparece | Situação |
| :-: | :--- | :--- |
| `6652` | Quase todos os itens | Provável atributo terciário ou qualidade de drop |
| `13440` | Peitoral e berloque | Não confirmado |
| `12699` | Itens craftados | Não confirmado |
| `12214` | Costas e pulsos craftados | Provável marcador de item craftado |
| `1587` | Cinto `271543` | Não confirmado |
| `1574` | Peitoral e botas | Não confirmado |
| `41` | Pernas | Provável atributo secundário adicional |
| `8790` | Pulso `239648` | Corroborado pelo export do SimC |
| `8960`, `12384`, `12497`, `13836` | Costas e pulsos craftados | Não confirmados |

---

## 5. Regra de decisão

| Objetivo | Como fazer |
| :--- | :--- |
| **Descobrir o track** | Usar o **nível de item** do comentário do export como âncora. `bonus_id` só desempata |
| **Detectar tier** | Pela pertinência ao conjunto no tooltip, ou por mapa de ID |
| **Ler atributos** | `crafted_stats` para itens craftados, tooltip para os demais. Nunca inferir de `bonus_id` |

### Validação cruzada que funcionou

O item `239648` aparece nos dois formatos de export com os mesmos sinais:

| Sinal | AMR | SimC |
| :--- | :--- | :--- |
| Item | `239648` | `id=239648` |
| Bônus | `b8790` | `bonus_id=.../8790/...` |
| Atributos de craft | `j36k32` | `crafted_stats=36/32` |
| Tuning | `n3615` | `content_tuning=3615` |

---

## 6. O bônus de 4 peças do Bruxo — resolvido

A divergência entre duas fontes do projeto foi encerrada por uma terceira via: o **texto oficial do conjunto** no Wowhead PT-BR (`item-set/2066`).

> **4 peças (Demonologia):** quando a energia deles se esvai, os Diabretes Selvagens têm **20% de chance** de se atirar no alvo deles e implodir com **350% de eficácia contra o alvo principal** e **315% de eficácia contra alvos secundários**.

| Fonte | Valor |
| :--- | :--- |
| `demonology_warlock.json` | 350% / 315% ✅ |
| `season2_context.json` (antes da correção) | 250% / 225% ❌ |
| MaxRoll, guia de M+ atualizado em 26/10/2026 | 250% / 225% ❌ **desatualizado** |
| **Conjunto oficial `2066` no Wowhead PT-BR** | **350% / 315%** ✅ |

**Veredito final: 350%/315%.** O MaxRoll está desatualizado neste ponto e não deve ser usado como referência para o bônus de tier.

### Os outros dois specs, para referência

| Spec | 4 peças |
| :--- | :--- |
| **Suplício** | Cada Agonia Instável ativa aumenta 2% do dano, até 6%. Semente da Corrupção aplica Agonia Instável com 20% de eficácia |
| **Destruição** | Alvos que recebem dano de Eco de Sargeras recebem mais 6% de dano por 6 s |

---

## 7. Próximos passos

1. Amostrar um item de cada track restante (**Campeão**) para fechar a série `128xx`.
2. Isolar o marcador de tier consultando um item de tier sem os outros dois IDs da família `1369x`.
3. Consultar um item com `13440`, `12699` e `41` isoladamente para confirmar a função de cada um.
4. Automatizar: uma chamada de tooltip por slot do export custa 15 requisições por personagem e devolve tudo estruturado, sem heurística.
