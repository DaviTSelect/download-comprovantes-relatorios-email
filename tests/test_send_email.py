"""Testa funções puras de core/send_email.py sem chamar a Graph API."""
import base64
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture(autouse=True)
def mock_config(monkeypatch):
    """Evita que config.py chame _exigir() com vars de ambiente reais."""
    mock = MagicMock()
    mock.PASTA_ASSINATURA = Path("assinatura")
    monkeypatch.setitem(__import__("sys").modules, "config", mock)


def test_montar_corpo_com_assinatura():
    from core.send_email import _montar_corpo, _CID_ASSINATURA
    html = _montar_corpo(com_assinatura=True)
    assert f'src="cid:{_CID_ASSINATURA}"' in html
    assert "<html>" in html


def test_montar_corpo_sem_assinatura():
    from core.send_email import _montar_corpo, _CID_ASSINATURA
    html = _montar_corpo(com_assinatura=False)
    assert f'src="cid:{_CID_ASSINATURA}"' not in html
    assert "<html>" in html


def test_montar_corpo_contem_aviso_lgpd():
    from core.send_email import _montar_corpo
    html = _montar_corpo(com_assinatura=False)
    assert "LGPD" in html


def test_ler_como_anexo(tmp_path):
    from core.send_email import _ler_como_anexo
    arquivo = tmp_path / "comprovante.pdf"
    conteudo = b"PDF simulado"
    arquivo.write_bytes(conteudo)

    anexo = _ler_como_anexo(str(arquivo))

    assert anexo["name"] == "comprovante.pdf"
    assert anexo["@odata.type"] == "#microsoft.graph.fileAttachment"
    assert base64.b64decode(anexo["contentBytes"]) == conteudo


def test_ler_como_anexo_nome_correto(tmp_path):
    from core.send_email import _ler_como_anexo
    arquivo = tmp_path / "relatorio_pedido_123.xlsx"
    arquivo.write_bytes(b"xlsx simulado")
    anexo = _ler_como_anexo(str(arquivo))
    assert anexo["name"] == "relatorio_pedido_123.xlsx"
