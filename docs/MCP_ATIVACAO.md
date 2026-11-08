# Ativação do MCP em qualquer IA/cliente

> Guia prático para conectar o servidor [`mcp_server.py`](../mcp_server.py:1) a
> VS Code, Roo Code, Cline, Claude Desktop, Cursor, Windsurf, Continue ou
> qualquer cliente compatível com MCP via **stdio**.
>
> Testado neste ambiente em **2026-11-06**: `mcp 1.30.0`, `initialize` OK,
> **9 tools** expostas e `call_tool(estado_dados)` respondendo.

---

## 1. Como o servidor é executado

O `mcp_server.py` é um servidor **stdio**: o cliente inicia o processo e troca
mensagens JSON-RPC pelo stdin/stdout. Não há porta, HTTP ou token de rede.

O cliente precisa de quatro informações:

| Campo | Valor |
|---|---|
| `command` | caminho do interpretador Python |
| `args` | caminho absoluto do `mcp_server.py` |
| `cwd` | raiz do projeto — **opcional**; alguns clientes (Roo) rejeitam esse campo. O servidor resolve `data/` por `Path(__file__).resolve().parent` |
| `env` | `PYTHONIOENCODING=utf-8`, `PYTHONPATH=<raiz>`, `MCP_TRANSPORT=stdio` |

---

## 2. Pré-requisitos

```bat
python --version
python -m pip install "mcp>=1.0,<2"
```

Confirme que a raiz tem:

- `mcp_server.py`
- `scraper_season2.py`, `wow_season2.py`, `config.py`, `tooltip_client.py`
- `data/` (os JSONs canônicos)

---

## 3. Descobrir os caminhos (obrigatório)

No Windows, o `python` do PATH pode ser um **alias** da Microsoft Store. Para a
configuração, use sempre o caminho retornado por:

```bat
python -c "import sys; print(sys.executable)"
```

Neste ambiente o retorno é:

```text
C:\Users\carlo\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\python.exe
```

A raiz do projeto é:

```text
C:\Users\carlo\Desktop\Crawl4AI
```

O `mcp_server.py` gera a config pronta em três formatos:

```bat
python mcp_server.py --print-config --formato=roo
python mcp_server.py --print-config --formato=vscode
python mcp_server.py --print-config --formato=bloco
```

- `roo` (padrão): `{"mcpServers": {...}}`, **sem `cwd`** — compatível com Roo/Cline,
  Claude, Cursor e Windsurf.
- `vscode`: `{"servers": {...}}`, com `type: stdio` e `cwd`.
- `bloco`: apenas `command/args/cwd/env`, para clientes que usam outro invólucro.

---

## 4. Validar antes de configurar o cliente

### 4.1 Selftest do servidor

```bat
python mcp_server.py --selftest
```

Deve sair com código 0 e listar o estado dos arquivos de `data/`.

### 4.2 Teste real do protocolo stdio

```bat
python tools\testar_mcp_stdio.py --tool estado_dados
```

Saída esperada:

```text
[OK] initialize; tools=6
     estado_dados, listar_catalogo, recomendar_encantamento_gema,
     scrape_pagina, scrape_wowhead_item, scrape_wowhead_items
[OK] call_tool(estado_dados) -> 1019 chars
```

### 4.3 Inspector oficial (opcional)

Se tiver Node.js:

```bat
npx @modelcontextprotocol/inspector python mcp_server.py
```

---

## 5. Configuração por cliente

> Substitua `<PYTHON>` e `<PROJETO>` pelos caminhos da seção 3.

### 5.1 VS Code nativo (Copilot / agent mode)

Arquivo: `.vscode/mcp.json` na raiz do projeto.

```json
{
  "servers": {
    "crawl4ai-wow": {
      "type": "stdio",
      "command": "<PYTHON>",
      "args": ["<PROJETO>\\mcp_server.py"],
      "cwd": "<PROJETO>",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "<PROJETO>",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Ativação: `Ctrl+Shift+P` → **MCP: List Servers** → selecione
`crawl4ai-wow` → **Start**. Se já estava rodando, use **Restart**.

### 5.2 Roo Code / Cline

Arquivo: `.roo/mcp.json` (config local, já ignorada pelo `.gitignore`).

```json
{
  "mcpServers": {
    "crawl4ai-wow": {
      "command": "<PYTHON>",
      "args": ["<PROJETO>\\mcp_server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "<PROJETO>",
        "MCP_TRANSPORT": "stdio"
      },
      "alwaysAllow": ["estado_dados", "listar_catalogo"],
      "disabled": false
    }
  }
}
```

Ativação: painel **MCP Servers** do Roo → **Restart** no servidor. Se não
aparecer, recarregue a janela do VS Code.

> `.roo/` já está no [`.gitignore`](../.gitignore:3); não versione essa config.
>
> **Importante:** o Roo valida o schema e **rejeita campos extras** (por exemplo
> `cwd` ou `type`) com a mensagem “Formato JSON das configurações MCP inválido”.
> Por isso o bloco acima não usa `cwd`: o `mcp_server.py` resolve `data/` a partir
> de `Path(__file__).resolve().parent`, e o `PYTHONPATH` no `env` cobre os imports.
> Gere o JSON exato com `python mcp_server.py --print-config --formato=roo`.

### 5.3 Claude Desktop

Arquivo: `%APPDATA%\Claude\claude_desktop_config.json`.

```json
{
  "mcpServers": {
    "crawl4ai-wow": {
      "command": "<PYTHON>",
      "args": ["<PROJETO>\\mcp_server.py"],
      "cwd": "<PROJETO>",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "<PROJETO>",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Ativação: feche e reabra o Claude Desktop por completo.

### 5.4 Cursor

Arquivo: `.cursor/mcp.json` (projeto) ou `~/.cursor/mcp.json` (global).

```json
{
  "mcpServers": {
    "crawl4ai-wow": {
      "command": "<PYTHON>",
      "args": ["<PROJETO>\\mcp_server.py"],
      "cwd": "<PROJETO>",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "<PROJETO>",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Ativação: **Settings → MCP** → recarregar/reconectar.

### 5.5 Windsurf

Arquivo: `~/.codeium/windsurf/mcp_config.json`.

```json
{
  "mcpServers": {
    "crawl4ai-wow": {
      "command": "<PYTHON>",
      "args": ["<PROJETO>\\mcp_server.py"],
      "cwd": "<PROJETO>",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "<PROJETO>",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Ativação: painel **MCP** → **Refresh**.

### 5.6 Continue

Use o bloco `mcpServers` no arquivo de configuração do Continue
(`config.yaml`/`config.json`, conforme a versão):

```yaml
mcpServers:
  - name: crawl4ai-wow
    command: <PYTHON>
    args:
      - <PROJETO>\mcp_server.py
    env:
      PYTHONIOENCODING: utf-8
      PYTHONPATH: <PROJETO>
      MCP_TRANSPORT: stdio
```

### 5.7 Qualquer outro cliente

Se o cliente aceita servidor **stdio**, basta o modelo:

```json
{
  "mcpServers": {
    "crawl4ai-wow": {
      "command": "<PYTHON>",
      "args": ["<PROJETO>\\mcp_server.py"],
      "cwd": "<PROJETO>",
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "<PROJETO>",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

> VS Code nativo usa `"servers"`; os demais usam `"mcpServers"`. O conteúdo do
> bloco é o mesmo. Se o cliente for o **Roo**, remova `cwd` (veja a seção 5.2) ou
> gere com `python mcp_server.py --print-config --formato=roo`.

### 5.8 Google Antigravity

O Antigravity consome servidores MCP pelo próprio painel de configurações do
agente. Use o bloco do formato `roo` (chave `mcpServers`, **sem `cwd`**):

```json
{
  "mcpServers": {
    "crawl4ai-wow": {
      "command": "<PYTHON>",
      "args": ["<PROJETO>\\mcp_server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "<PROJETO>",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

Ativação: abra as configurações de MCP do Antigravity, cole o JSON, salve e
reinicie o servidor/agente. Se a versão usar um arquivo, o nome pode variar
(`mcp_config.json`); o conteúdo é o mesmo.

> O Antigravity **não** executa o crawl na nuvem: ele apenas inicia o
> `mcp_server.py` localmente via stdio. Veja a seção 10 (Custos).

---

## 6. Tools expostas

| Tool | Para que serve |
|---|---|
| `estado_dados` | Estado dos arquivos de `data/` e contagens. |
| `listar_catalogo` | Lista gemas/encantamentos/missivas do catálogo. |
| `recomendar_encantamento_gema` | Recomenda encantamento/gema por classe/spec. |
| `scrape_pagina` | Raspa página web com Fit Markdown limpo (estilo Firecrawl), JS e detecção automática de abas (`auto_clicar_abas=True`). |
| `scrape_todas_as_abas` | Varre, clica sequencialmente e extrai automaticamente TODAS as abas dinâmicas de uma página SPA em Markdown estruturado. |
| `map_site` | Mapeia todas as rotas e links internos de um domínio (estilo `firecrawl_map`). |
| `scrape_estruturado` | Extrai dados em JSON usando CSS Schema (estilo `ScrapegraphAI`). |
| `scrape_wowhead_item` | Extrai um item por ID/URL. Aceita `qualidade_craft_min` e `exigir_craft`. |
| `scrape_wowhead_items` | Extrai várias URLs/listas. Aceita `qualidade_craft_min` e `exigir_craft`. |

Para o requisito **somente R5 + Épico**, chame as tools de scrape com:

```json
{
  "item": "237831",
  "qualidade_craft_min": 5,
  "exigir_craft": true
}
```

---

## 7. Troubleshooting

| Sintoma | Causa provável | Solução |
|---|---|---|
| Servidor não inicia / encerra na hora | `command` aponta para o alias da Store | Use o caminho absoluto de `python -c "import sys; print(sys.executable)"` |
| `ModuleNotFoundError: config` | `cwd`/`PYTHONPATH` errados | Defina `cwd` na raiz e `PYTHONPATH` para a raiz |
| `UnicodeEncodeError` | console `cp1252` | `PYTHONIOENCODING=utf-8` no `env` |
| `No module named mcp` | dependência ausente | `python -m pip install "mcp>=1.0,<2"` |
| Tool não aparece | cliente não recarregou | Reinicie o servidor MCP ou recarregue a janela |
| “Formato JSON das configurações MCP inválido” no Roo | campo não suportado pelo schema (ex.: `cwd`, `type`) | Rode `--print-config --formato=roo` e cole o resultado; remova campos extras |
| `scrape_*` falha com 403 | anti-bot do Wowhead | Aguarde; o `circuit_breaker` interrompe após 5 falhas |
| Muitos itens sem craft | lista de loot de M+ | Ligue `exigir_craft` para usar os 112 IDs craftados |

### Nota sobre background no Windows

`Start-Process` e `DETACHED_PROCESS` **não** funcionam com o `python.exe` do
WindowsApps neste ambiente: o processo morre sem saída. Para rodar em segundo
plano, use [`tools/iniciar_varredura_bg.py`](../tools/iniciar_varredura_bg.py:1),
que usa `CREATE_NEW_PROCESS_GROUP`.

---

## 8. Segurança

- Nenhum token é necessário para as tools que leem `data/`.
- `DEEPSEEK_API_KEY` é lida do `.env` apenas quando o fallback LLM é acionado.
- `.roo/` é ignorado pelo Git; `.vscode/mcp.json` não contém segredos.
- Não coloque chaves diretamente no JSON de config do cliente; use variáveis de
  ambiente ou `${env:...}` quando o cliente suportar.

---

## 9. Checklist rápido

1. `python -c "import sys; print(sys.executable)"` → guarde `<PYTHON>`.
2. `python mcp_server.py --selftest` → exit 0.
3. `python tools\testar_mcp_stdio.py --tool estado_dados` → 6 tools + resposta.
4. Crie a config do seu cliente (seção 5).
5. Reinicie o servidor MCP no cliente.
6. Peça à IA: “use a tool `estado_dados`” para confirmar.

---

## 10. Custos

| Item | Custo | Observação |
|---|---|---|
| **Crawl4AI** | **R$ 0** | Biblioteca open-source executada localmente. Não há cobrança por página. |
| **Playwright/Chromium** | **R$ 0** | Navegador headless local. |
| **Wowhead** | **R$ 0** | Acesso público; sujeito a 403/anti-bot e ao circuit breaker. |
| **Firecrawl** | **não usado** | Não há referência a Firecrawl no código Python nem no `requirements.txt`; só aparece em documentação antiga. |
| **DeepSeek (LLM)** | **opcional** | Só entra se você chamar o fallback LLM (`_extrair_com_llm`/`aplicar_llm_em_item`) e tiver `DEEPSEEK_API_KEY`. O fluxo principal não usa LLM. |
| **Antigravity** | depende do plano do Antigravity | Ele apenas consome o MCP local; o crawl continua rodando na sua máquina, sem custo por requisição. |

**Resposta curta:** usar o Antigravity **não** cria cobrança do crawl. Você paga
apenas pelo que o Antigravity já cobra (se cobrar) e, se quiser, pela API do
DeepSeek no fallback LLM.