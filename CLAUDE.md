# Regras do Projeto — download-comprovantes-relatorios-email

Derivadas do [PADRAO_EMPRESA](../PADRAO_EMPRESA/specs/00_PADRAO_GERAL.spec.md) · Categoria **AUTO** · Versão 1.0 · 2026-11-10

---

## Categoria e Estrutura

Este projeto é categoria **AUTO** (Automação/Bot com GUI mínima PySide6).

Estrutura obrigatória mantida:
```
download-comprovantes-relatorios-email/
├── core/           # lógica de negócio — um módulo por domínio
├── dados/          # planilha de entrada (não versionada)
├── logs/           # logs de execução (não versionados, apenas .gitkeep)
├── anexos/         # downloads do Conveniar (não versionados)
├── assinatura/     # imagem de assinatura (não versionada)
├── main.py         # ponto de entrada único
├── config.py       # todas as configs via os.environ / .env
├── version.py      # VERSION, APP_NAME, REPOSITORY, DESCRIPTION, AUTHOR
├── utils.py        # configurar_logging(), salvar_relatorio_erros()
├── gui.py          # interface PySide6 — sem lógica de negócio
├── requirements.txt
├── .env            # credenciais reais (NÃO versionar)
├── .env.example    # estrutura sem valores reais (versionado)
├── .gitignore
├── README.md
├── CHANGELOG.md
└── agente.md
```

---

## Código

- **Idioma:** variáveis, funções e comentários em **português brasileiro**
- **Nomes de arquivos Python:** `snake_case.py`
- **Logging:** sempre `logging.*`, nunca `print()` em produção
- **Exceções:** nunca `pass` silencioso; logar com `logger.exception()` para erros inesperados
- **Dados sensíveis em logs:** usar `redigir()` para CPFs, senhas, tokens — nunca logar em texto claro
- **GUI:** a classe `App` em `gui.py` não deve conter lógica de negócio; usar sinais PySide6 para comunicar resultado ao UI

---

## Configuração

- **Obrigatório:** toda config que varia por ambiente (caminhos, credenciais, URLs) vem de variável de ambiente — nunca hardcoded
- **Obrigatório:** `.env` com valores reais no `.gitignore`; `.env.example` com estrutura versionado
- **Variáveis obrigatórias:** `GRAPH_CLIENT_ID`, `GRAPH_CLIENT_SECRET`, `GRAPH_TENANT_ID`, `USER_EMAIL`, `CONVENIAR_USUARIO`, `CONVENIAR_SENHA`
- **Variáveis opcionais com default:** `CONVENIAR_URL`, `CHROME_BINARY`, `CHROMEDRIVER_PATH`
- **Padrão:** `config.py` usa `_exigir()` para vars obrigatórias e `os.environ.get("VAR", default)` para opcionais

---

## O que NUNCA versionar

```
.env                   # credenciais reais
venv/ .venv/ env/      # ambientes virtuais
__pycache__/ *.pyc     # cache Python
anexos/                # dados de beneficiários baixados
dados/planilha.xlsx    # planilha com dados pessoais
logs/*.log logs/*.csv  # logs de execução
assinatura/*.png *.jpg # imagem de assinatura
build/ dist/ *.exe     # artefatos de build
```

---

## Versionamento

- **Esquema:** SemVer — `MAJOR.MINOR.PATCH`
- **Arquivo canônico:** `version.py` com `VERSION`, `APP_NAME`, `REPOSITORY`, `DESCRIPTION`, `AUTHOR`, `__version__ = VERSION`
- **Branches:** `main` (estável), `dev` (desenvolvimento), `feature/nome`, `fix/nome`
- **Nunca commitar diretamente em `main`** — apenas via PR de `dev`
- **Commits:** prefixo convencional — `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `release:`
- **CHANGELOG.md:** atualizar seção `[Não lançado]` a cada commit relevante

---

## Logs

- Configurados em `main.py` via `utils.configurar_logging()`
- Formato obrigatório: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- Dois handlers: `StreamHandler()` (console) + `FileHandler(logs/app.log)`
- Relatório de erros em CSV com timestamp: `logs/erros_YYYY-MM-DD_HHMMSS.csv`
- `logs/.gitkeep` mantém a pasta no git; conteúdo ignorado

---

## Segurança

- Nenhuma credencial, token ou senha no código-fonte
- Verificar antes de cada commit: `git diff --cached --name-only` — confirmar que `.env` não está staged
- CPFs e dados pessoais processados em memória e não logados em texto claro

---

## Referências

- Padrão geral: `../PADRAO_EMPRESA/specs/00_PADRAO_GERAL.spec.md`
- Arquitetura: `../PADRAO_EMPRESA/specs/02_ARQUITETURA.spec.md`
- Versionamento: `../PADRAO_EMPRESA/specs/04_VERSIONAMENTO.spec.md`
- Logs/Erros: `../PADRAO_EMPRESA/specs/10_LOGS_ERROS.spec.md`
- Segurança: `../PADRAO_EMPRESA/specs/11_SEGURANCA.spec.md`
- Documentação: `../PADRAO_EMPRESA/specs/12_DOCUMENTACAO.spec.md`
