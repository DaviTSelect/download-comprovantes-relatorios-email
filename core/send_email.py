import base64
import logging
import os
from pathlib import Path

import requests

from config import PASTA_ASSINATURA
from core.auth import pegar_token

logger = logging.getLogger(__name__)

_CID_ASSINATURA = "assinatura_facto"


def _ler_como_anexo(caminho: str) -> dict:
    with open(caminho, "rb") as f:
        conteudo_b64 = base64.b64encode(f.read()).decode()
    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": os.path.basename(caminho),
        "contentBytes": conteudo_b64,
    }


def _carregar_assinatura(caminho: str | None = None) -> dict | None:
    """Carrega a assinatura PNG como anexo inline (cid:).

    Se ``caminho`` for fornecido, usa esse arquivo.
    Caso contrário, procura o primeiro PNG em PASTA_ASSINATURA.
    Retorna None se não houver assinatura disponível.
    """
    if caminho:
        png = Path(caminho)
    else:
        if not PASTA_ASSINATURA.exists():
            return None
        pngs = sorted(PASTA_ASSINATURA.glob("*.png"))
        if not pngs:
            return None
        png = pngs[0]

    if not png.exists():
        return None
    with open(png, "rb") as f:
        conteudo_b64 = base64.b64encode(f.read()).decode()
    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": png.name,
        "contentBytes": conteudo_b64,
        "contentId": _CID_ASSINATURA,
        "isInline": True,
    }


_AVISO_LGPD = (
    "As informações existentes nesta mensagem e nos arquivos anexados são para uso restrito, "
    "sendo seu sigilo protegido por lei. Caso não seja destinatário, saiba que a leitura, "
    "divulgação ou cópia são proibidas. Favor apagar as informações e notificar o remetente. "
    "O uso impróprio será tratado conforme as normas da Facto, Lei Geral de Proteção de Dados "
    "Pessoais (LGPD) e demais regramentos no âmbito cível e criminal."
)


def _montar_corpo(com_assinatura: bool) -> str:
    assinatura_html = (
        f'<br><img src="cid:{_CID_ASSINATURA}" alt="Assinatura" style="max-width:600px;"><br>'
        if com_assinatura else "<br>"
    )
    return f"""
<html><body style="font-family: Calibri, Arial, sans-serif; font-size: 14px; color: #1a1a1a;">
  <p>Prezada, boa tarde!</p>
  <p>
    Segue, em anexo, o comprovante de pagamento e o recibo para melhor entendimento.<br>
    Informo que o valor recebido corresponde ao valor líquido, após os descontos dos impostos.
  </p>
  {assinatura_html}
  <p style="font-size:11px; color:#555555; border-top:1px solid #dddddd; padding-top:8px; margin-top:8px;">
    <span style="color:#e94c1f; font-weight:bold;">Atenção:</span> {_AVISO_LGPD}
  </p>
</body></html>
""".strip()


def enviar_email(
    destinatario: str,
    nome_projeto: str,
    arquivos: list[str],
    remetente: str,
    assinatura_path: str | None = None,
) -> None:
    """Envia e-mail com comprovante e recibo via Microsoft Graph API.

    ``assinatura_path``: caminho para PNG de assinatura selecionado na GUI.
    Se None, tenta carregar o primeiro PNG de PASTA_ASSINATURA.
    """
    token = pegar_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    assinatura = _carregar_assinatura(assinatura_path)
    corpo_html = _montar_corpo(com_assinatura=assinatura is not None)

    anexos = [_ler_como_anexo(a) for a in arquivos]
    if assinatura:
        anexos.append(assinatura)
        logger.info("Assinatura incorporada: %s", assinatura["name"])
    else:
        logger.warning("Pasta assinatura/ sem PNG — e-mail enviado sem assinatura")

    payload = {
        "message": {
            "subject": f"Comprovante de pagamento - {nome_projeto}",
            "body": {
                "contentType": "HTML",
                "content": corpo_html,
            },
            "toRecipients": [{"emailAddress": {"address": destinatario}}],
            "attachments": anexos,
        }
    }

    url = f"https://graph.microsoft.com/v1.0/users/{remetente}/sendMail"
    resposta = requests.post(url, headers=headers, json=payload)
    resposta.raise_for_status()
    logger.info(
        "E-mail enviado para %s — '%s' (%d anexo(s))",
        destinatario, nome_projeto, len(arquivos),
    )
