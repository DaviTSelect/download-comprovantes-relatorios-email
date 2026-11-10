import base64
import os
import requests

def baixar_anexos(token, user_email, mensagens, pasta="anexos"):
    os.makedirs(pasta, exist_ok=True)

    headers = {"Authorization": f"Bearer {token}"}

    for msg in mensagens:
        if not msg.get("hasAttachments"):
            continue

        url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{msg['id']}/attachments"

        r = requests.get(url, headers=headers)
        r.raise_for_status()

        anexos = r.json().get("value", [])

        for anexo in anexos:
            if anexo["@odata.type"] == "#microsoft.graph.fileAttachment":
                nome = anexo["name"]
                conteudo = base64.b64decode(anexo["contentBytes"])

                caminho = os.path.join(pasta, nome)

                with open(caminho, "wb") as f:
                    f.write(conteudo)

                print(f"Baixado: {caminho}")