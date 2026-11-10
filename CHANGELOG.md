# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/).
Versões seguem [SemVer](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado

### Corrigido

### Alterado

### Removido

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
