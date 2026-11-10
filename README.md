# Automação Conveniar Email

> Lê uma planilha com número de pedido e e-mail, baixa o anexo e o relatório do portal Conveniar via Selenium e envia ambos para o destinatário via Microsoft Graph API.

## Pré-requisitos

- Python 3.10+
- Google Chrome instalado
- Acesso ao portal Conveniar (usuário e senha)
- App registrado no Azure AD com permissão `Mail.Send`

## Instalação

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Configuração

```powershell
copy .env.example .env
# Editar .env com as credenciais reais
```

Variáveis necessárias (ver `.env.example`):

| Variável | Descrição |
|---|---|
| `GRAPH_CLIENT_ID` | Client ID do app Azure AD |
| `GRAPH_CLIENT_SECRET` | Secret do app Azure AD |
| `GRAPH_TENANT_ID` | Tenant ID da organização |
| `USER_EMAIL` | E-mail remetente (caixa que envia) |
| `CONVENIAR_URL` | URL base do portal (padrão: https://facto.conveniar.com.br) |
| `CONVENIAR_USUARIO` | Usuário de login no Conveniar |
| `CONVENIAR_SENHA` | Senha de login no Conveniar |

## Uso

```powershell
# Execução padrão (usa dados/planilha.xlsx)
python main.py

# Com planilha alternativa
python main.py --planilha dados/outra_planilha.xlsx
```

## Entrada e Saída

| Item | Local | Descrição |
|---|---|---|
| Entrada | `dados/planilha.xlsx` | Planilha com `numero_pedido` e `email` |
| Template | `dados/planilha_modelo.xlsx` | Modelo para preenchimento |
| Downloads | `anexos/<numero_pedido>/` | Arquivos baixados do Conveniar (não versionados) |
| Log | `logs/app.log` | Log de execução |
| Erros | `logs/erros_<timestamp>.csv` | Relatório de pedidos com falha |

## Estrutura

```
download-comprovantes-relatorios-email/
├── core/
│   ├── auth.py                 # autenticação MSAL
│   ├── conveniar_bot.py        # Selenium — baixa arquivos do Conveniar
│   ├── send_email.py           # Graph API — envia e-mail com anexos
│   ├── search_email.py         # Graph API — busca e-mails recebidos
│   └── download_attachments.py # Graph API — baixa anexos de e-mails recebidos
├── dados/
│   └── planilha_modelo.xlsx    # template da planilha de entrada
├── logs/                       # logs de execução (não versionados)
├── main.py                     # orquestrador principal
├── config.py                   # leitura de variáveis de ambiente
├── version.py                  # versão da automação
├── utils.py                    # logging e utilitários
├── gui.py                      # interface gráfica PySide6
├── requirements.txt
├── .env.example
├── .gitignore
├── CHANGELOG.md
└── CLAUDE.md                   # regras do projeto (PADRAO_EMPRESA AUTO)
```

## Ajuste dos Seletores Selenium

O arquivo [core/conveniar_bot.py](core/conveniar_bot.py) contém comentários `# TODO` nos pontos
que precisam ser ajustados conforme o layout real do portal Conveniar.
Execute com `headless=False` (padrão) para inspecionar os elementos no Chrome.

## Padrão Corporativo

Este projeto segue o [Padrão de Engenharia da Empresa — AUTO](../PADRAO_EMPRESA/specs/00_PADRAO_GERAL.spec.md).
