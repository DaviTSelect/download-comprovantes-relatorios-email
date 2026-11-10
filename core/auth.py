import logging
import msal
from config import GRAPH_CLIENT_ID, GRAPH_CLIENT_SECRET, GRAPH_TENANT_ID

logger = logging.getLogger(__name__)


def pegar_token() -> str:
    authority = f"https://login.microsoftonline.com/{GRAPH_TENANT_ID}"

    app = msal.ConfidentialClientApplication(
        client_id=GRAPH_CLIENT_ID,
        client_credential=GRAPH_CLIENT_SECRET,
        authority=authority,
    )

    resultado = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" not in resultado:
        raise RuntimeError(
            f"Falha ao obter token MSAL: {resultado.get('error_description', resultado)}"
        )

    logger.info("Token MSAL obtido com sucesso")
    return resultado["access_token"]
