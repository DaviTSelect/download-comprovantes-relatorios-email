# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versões seguem [SemVer](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado

### Corrigido

### Alterado

### Removido

---

## [1.0.4] - 2026-11-11

### Adicionado
- Interface: barra de rolagem no corpo do cartão — aparece automaticamente quando há
  muitos pedidos carregados; rodapé com botão "Iniciar" permanece fixo
- Interface: estilo dedicado `ESTILO_INICIAR_RODANDO` (azul escuro + texto claro) para o
  botão durante o processamento — corrige texto preto ilegível causado pelo estado
  `disabled` padrão do Qt/Windows
- Interface: diálogos de alerta, confirmação e erro com tema escuro via helper `_dialogo()`
  — fundo `#203447`, texto claro, botão laranja; consistente com o restante da interface

### Corrigido
- Interface: cor inválida `#ebebе7` (com caractere cirílico) no stylesheet da scrollbar
  corrigida para `#ebebe7`

### Alterado
- E-mail: "Atenciosamente," adicionado antes da imagem de assinatura no corpo HTML
- Interface: dimensões padrão da janela ajustadas (altura 720→750 px, mínimo 640→670 px)
- Regra de desenvolvimento: alterações que ainda não foram publicadas devem ser
  documentadas em `CHANGELOG.md` sob a versão em desenvolvimento

---

## [1.0.3] - 2026-11-10

### Adicionado
- Interface: etapa 02 "Assinatura do e-mail" — seleção de PNG diretamente
  pelo painel; pré-carrega automaticamente se já houver PNG em `assinatura/`
- Logging: `logger.exception()` nos blocos de download e envio do `gui.py` —
  erros agora aparecem em `logs/app.log` com traceback completo

### Corrigido
- Download: `.tmp` só é renomeado para `.pdf` após o tamanho estabilizar,
  evitando corrupção quando o Chrome ainda está gravando o arquivo

---

## [1.0.2] - 2026-11-10

### Adicionado
- Auto-update silencioso: ao abrir o app verifica o GitHub Releases em segundo plano,
  baixa o novo `.exe`, valida SHA-256 e agenda a troca via PowerShell — sem interação do usuário

---

## [1.0.1] - 2026-11-10

### Corrigido
- `.env` e pastas (`anexos/`, `dados/`, `assinatura/`, `logs/`) agora resolvem corretamente
  na pasta do `.exe` independente do diretório de trabalho (fix para PyInstaller frozen)
- Chrome/ChromeDriver sem caminho configurado usa o Chrome instalado no sistema automaticamente
- Caminhos com `%USERPROFILE%` expandidos via `os.path.expandvars()`

---

## [1.0.0] - 2026-11-10

### Adicionado
- Automação Selenium para login e download de arquivos do Conveniar
- Envio de e-mail com 2 anexos via Microsoft Graph API
- Planilha modelo com `numero_pedido` e `email`
- Estrutura de projeto seguindo padrão corporativo AUTO
- Logging em arquivo (`logs/app.log`) e console
- Relatório de erros em CSV (`logs/erros_<timestamp>.csv`)
- Configuração por variáveis de ambiente via `.env`
