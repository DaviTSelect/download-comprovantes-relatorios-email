# Contexto do Projeto para Agente IA

## O que este projeto faz

Automação Python (categoria AUTO) que lê uma planilha com número de pedido e e-mail,
faz login no portal Conveniar via Selenium, baixa o anexo e o relatório de cada pedido,
e envia ambos para o destinatário correspondente via Microsoft Graph API.

## Tecnologias

- Python 3.10+
- Selenium + webdriver-manager (automação do portal Conveniar)
- MSAL + Microsoft Graph API (autenticação e envio de e-mail)
- openpyxl (leitura da planilha de entrada)
- python-dotenv (configuração via .env)

## Arquitetura

```
download-comprovantes-relatorios-email/
├── core/
│   ├── auth.py                 # pegar_token() — MSAL
│   ├── conveniar_bot.py        # baixar_arquivos_pedido() — Selenium
│   ├── send_email.py           # enviar_email() — Graph API
│   ├── search_email.py         # buscar_emails_hoje() — Graph API
│   └── download_attachments.py # baixar_anexos() — Graph API
├── main.py                     # orquestrador — lê planilha e chama core/
├── gui.py                      # interface PySide6 (sem lógica de negócio)
├── config.py                   # todas as configs via os.environ / .env
├── version.py                  # VERSION, APP_NAME, REPOSITORY, DESCRIPTION, AUTHOR
└── utils.py                    # configurar_logging(), salvar_relatorio_erros()
```

**Módulos principais:**
- `core/conveniar_bot.py`: seletores Selenium marcados com `# TODO` — ajustar conforme UI real
- `core/send_email.py`: envia e-mail com 2 anexos via Graph API
- `main.py`: lê planilha linha a linha, chama bot + send_email, salva relatório de erros

## Como executar

```powershell
.\venv\Scripts\Activate.ps1
python main.py
python main.py --planilha dados/outra_planilha.xlsx
```

## Padrões do projeto

- Código em português (variáveis, funções, comentários)
- Commits com prefixo convencional (`feat:`, `fix:`, `docs:`, `chore:`)
- Versão em `version.py` → `VERSION = "1.0.0"`
- Logs via módulo `logging`, nunca `print()`
- Credenciais apenas via `.env` — nunca hardcoded

## Fluxo principal

1. `main.py` lê `dados/planilha.xlsx` — colunas `numero_pedido`, `email`
2. Para cada linha: `conveniar_bot.baixar_arquivos_pedido(numero_pedido)`
3. Selenium faz login → busca pedido → baixa 2 arquivos em `anexos/<pedido>/`
4. `send_email.enviar_email(email, pedido, arquivo1, arquivo2)` via Graph API
5. Erros são coletados e salvos em `logs/erros_<timestamp>.csv`

## O que NÃO fazer

- Não commitar `.env` com credenciais reais
- Não versionar `anexos/` (dados de beneficiários)
- Não versionar `dados/planilha.xlsx` (dados sensíveis)
- Não usar `print()` — usar `logger.*`
- Não hardcodar CLIENT_ID/SECRET no código

## Dados sensíveis

- Credenciais MSAL e Conveniar: apenas em `.env` (não versionado)
- Planilha de entrada: `dados/planilha.xlsx` no `.gitignore`
- Arquivos baixados: pasta `anexos/` no `.gitignore`

## Referência de padrão corporativo

[PADRAO_EMPRESA/specs/00_PADRAO_GERAL.spec.md](../PADRAO_EMPRESA/specs/00_PADRAO_GERAL.spec.md)
