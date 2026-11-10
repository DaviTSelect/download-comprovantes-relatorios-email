import requests
from datetime import datetime, timezone

def buscar_emails_hoje(token, user_email):

    inicio = datetime(
        2026, 8, 25,
        0, 0, 0,
        tzinfo=timezone.utc
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    agora = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    params = {
        "$filter": f"receivedDateTime ge {inicio} and receivedDateTime le {agora}",
        "$select": "id,subject,hasAttachments,receivedDateTime",
        "$orderby": "receivedDateTime desc"
    }

    r = requests.get(
        url,
        headers=headers,
        params=params
    )

    print("Status:", r.status_code)
    print(r.text)

    r.raise_for_status()

    return r.json().get("value", [])