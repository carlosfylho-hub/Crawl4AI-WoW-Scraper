# Segurança — chaves de API (F-12 §3.9)

Este documento registra o incidente da **chave Firecrawl exposta** e o
procedimento de revogação/rotação. Ele **não** substitui a ação manual no
painel do Firecrawl: o código não consegue revogar credenciais por conta
própria.

## 1. O que aconteceu

- A chave do Firecrawl (prefixo `fc` + segredo) foi gravada em `.roo/mcp.json`
  (arquivo local de configuração do Roo Code) e também apareceu no histórico
  de uma conversa de trabalho.
- `.roo/` está listado no `.gitignore` e o arquivo **não existe** no
  repositório no momento desta auditoria (`ROO_MCP_AUSENTE`).
- Varredura textual em todo o repositório (arquivos versionáveis, incluindo
  `.env.example`, `docs/`, `plans/`, `data/` e `base_conhecimento_ai_studio/`)
  **não encontrou nenhuma ocorrência** de chave Firecrawl, `firecrawl` com
  valor de chave ou `FIRECRAWL_API_KEY` com valor real.
- `.env` local **não** contém variável `FIRECRAWL` (0 ocorrências).
  Nenhum valor secreto foi impresso durante a auditoria.

> Conclusão: não há segredo em arquivo versionável. O risco remanescente é a
> chave continuar **válida** no painel do Firecrawl e ter sido exposta no
> histórico da conversa.

## 2. Ação manual obrigatória (pendente)

1. **Revogar** a chave atual no painel do Firecrawl
   (<https://www.firecrawl.dev/app/api-keys>).
2. **Gerar** uma nova chave.
3. Atualizar o `.env` local (nunca versionar):

   ```dotenv
   FIRECRAWL_API_KEY=<FIRECRAWL_API_KEY>
   ```

4. Atualizar a configuração local do MCP (`.roo/mcp.json`), que continua
   fora do controle de versão. Prefira referenciar variável de ambiente em
   vez de colar o literal:

   ```json
   {
     "mcpServers": {
       "firecrawl": {
         "env": { "FIRECRAWL_API_KEY": "${env:FIRECRAWL_API_KEY}" }
       }
     }
   }
   ```

5. Se algum código passar a usar Firecrawl, ler **sempre** de
   `os.getenv("FIRECRAWL_API_KEY")` e nunca embutir o literal no fonte.

## 3. Higiene do histórico Git (opcional, destrutivo)

Somente execute se a chave **real** tiver sido commitada em algum momento.
A auditoria atual **não encontrou** esse caso, então o procedimento abaixo
é preventivo.

> ⚠️ **Aviso:** `git filter-repo` reescreve o histórico. Hashes mudam,
> clones existentes precisam ser refeitos e o `push` exige `--force`
> coordenado com todos os colaboradores. Faça backup (`.git` ou `git bundle`)
> antes.

```bash
# 1. Backup
git bundle create backup-antes-filter-repo.bundle --all

# 2. Remover a string do histórico (troque pelo valor real)
git filter-repo --replace-text <(echo "<CHAVE_REAL>>==><REDACTED>")

# 3. Revisar
git log --oneline --all -20

# 4. Publicar (coordene com o time)
git push --force --all
git push --force --tags
```

Alternativa menos invasiva: manter a chave revogada e considerar o histórico
apenas como registro (a revogação elimina o risco de uso).

## 4. Checklist de verificação

- [ ] Chave revogada no painel Firecrawl.
- [ ] Nova chave criada e gravada apenas em `.env` (não versionado).
- [ ] Nenhuma ocorrência da chave real em arquivos versionáveis.
- [ ] `.gitignore` cobre `.env`, `.roo/` e caches.
- [ ] `docs/SEGURANCA.md` atualizado com a data da rotação.
