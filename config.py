import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Diretório base: pasta do .exe quando frozen, CWD quando script.
# Todos os caminhos relativos (logs, anexos, .env) resolvem a partir daqui.
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(".")

load_dotenv(BASE_DIR / ".env")


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


# Chrome portátil — suporta %USERPROFILE% e $HOME no valor
def _expandir(nome: str):
    valor = os.environ.get(nome) or ""
    expandido = os.path.expandvars(valor).strip()
    return expandido or None


CHROME_BINARY     = _expandir("CHROME_BINARY")
CHROMEDRIVER_PATH = _expandir("CHROMEDRIVER_PATH")

# Caminhos — todos relativos ao BASE_DIR para funcionar no .exe
PASTA_DOWNLOADS  = BASE_DIR / "anexos"
PASTA_DADOS      = BASE_DIR / "dados"
PASTA_ASSINATURA = BASE_DIR / "assinatura"
PLANILHA_ENTRADA = PASTA_DADOS / "planilha.xlsx"
