import logging
from datetime import datetime, timezone

import requests

logger = logging.getLogger(__name__)


def buscar_emails_periodo(token: str, user_email: str, data_inicio: datetime) -> list[dict]:
    """Retorna e-mails recebidos desde `data_inicio` até agora."""
    inicio = data_inicio.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "$filter": f"receivedDateTime ge {inicio} and receivedDateTime le {agora}",
        "$select": "id,subject,hasAttachments,receivedDateTime",
        "$orderby": "receivedDateTime desc",
    }

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()

    emails = r.json().get("value", [])
    logger.info("%d e-mail(s) encontrado(s) desde %s", len(emails), inicio)
    return emails


def buscar_emails_hoje(token: str, user_email: str) -> list[dict]:
    inicio_do_dia = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return buscar_emails_periodo(token, user_email, inicio_do_dia)
