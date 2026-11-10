import base64
import logging
import os

import requests

logger = logging.getLogger(__name__)


def baixar_anexos(token: str, user_email: str, mensagens: list[dict], pasta: str = "anexos") -> None:
    """Baixa todos os anexos das mensagens fornecidas para `pasta`."""
    os.makedirs(pasta, exist_ok=True)
    headers = {"Authorization": f"Bearer {token}"}

    for msg in mensagens:
        if not msg.get("hasAttachments"):
            continue

        url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{msg['id']}/attachments"
        r = requests.get(url, headers=headers)
        r.raise_for_status()

        for anexo in r.json().get("value", []):
            if anexo["@odata.type"] != "#microsoft.graph.fileAttachment":
                continue

            nome = anexo["name"]
            conteudo = base64.b64decode(anexo["contentBytes"])
            caminho = os.path.join(pasta, nome)

            with open(caminho, "wb") as f:
                f.write(conteudo)

            logger.info("Anexo baixado: %s", caminho)
