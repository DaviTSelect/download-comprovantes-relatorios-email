import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _exigir(nome: str) -> str:
    valor = os.environ.get(nome)
    if not valor:
        raise RuntimeError(f"Variável de ambiente '{nome}' não configurada. Verifique o .env")
    return valor

# Microsoft Graph API (MSAL)
GRAPH_CLIENT_ID     = _exigir("GRAPH_CLIENT_ID")
GRAPH_CLIENT_SECRET = _exigir("GRAPH_CLIENT_SECRET")
GRAPH_TENANT_ID     = _exigir("GRAPH_TENANT_ID")
USER_EMAIL          = _exigir("USER_EMAIL")

# Conveniar
CONVENIAR_URL     = os.environ.get("CONVENIAR_URL", "https://facto.conveniar.com.br")
CONVENIAR_USUARIO = _exigir("CONVENIAR_USUARIO")
CONVENIAR_SENHA   = _exigir("CONVENIAR_SENHA")

# Chrome portátil — configurar via .env se usar Chrome não-padrão
CHROME_BINARY     = os.environ.get("CHROME_BINARY")     or None
CHROMEDRIVER_PATH = os.environ.get("CHROMEDRIVER_PATH") or None

# Caminhos
PASTA_DOWNLOADS  = Path("anexos")
PASTA_DADOS      = Path("dados")
PASTA_ASSINATURA = Path("assinatura")
PLANILHA_ENTRADA = PASTA_DADOS / "planilha.xlsx"
