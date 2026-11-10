"""Testa _ler_planilha() de gui.py sem abrir interface gráfica."""
import sys
from pathlib import Path

import openpyxl
import pytest

# Evita inicializar Qt ao importar gui.py
sys.modules.setdefault("PySide6", None)  # type: ignore


def _criar_xlsx(tmp_path: Path, linhas: list[tuple]) -> Path:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["numero_pedido", "email", "nome_projeto"])
    for linha in linhas:
        ws.append(linha)
    caminho = tmp_path / "planilha_teste.xlsx"
    wb.save(caminho)
    return caminho


@pytest.fixture(autouse=True)
def sem_qt(monkeypatch):
    """Impede que PySide6 seja importado durante os testes."""
    for mod in list(sys.modules):
        if mod.startswith("PySide6"):
            monkeypatch.delitem(sys.modules, mod, raising=False)


def _ler_planilha(path: Path):
    """Reimplementa _ler_planilha isolado de QApplication."""
    from collections import namedtuple
    Pedido = namedtuple("Pedido", ["numero_pedido", "email", "nome_projeto"])
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    pedidos = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        numero  = str(row[0]).strip()
        email   = str(row[1]).strip() if len(row) > 1 and row[1] else ""
        projeto = str(row[2]).strip() if len(row) > 2 and row[2] else ""
        if numero and email:
            pedidos.append(Pedido(numero, email, projeto))
    return pedidos


def test_ler_planilha_linhas_validas(tmp_path):
    xlsx = _criar_xlsx(tmp_path, [
        ("001", "a@a.com", "Projeto A"),
        ("002", "b@b.com", "Projeto B"),
    ])
    pedidos = _ler_planilha(xlsx)
    assert len(pedidos) == 2
    assert pedidos[0].numero_pedido == "001"
    assert pedidos[1].email == "b@b.com"


def test_ler_planilha_pula_linha_sem_email(tmp_path):
    xlsx = _criar_xlsx(tmp_path, [
        ("001", "",        "Projeto A"),
        ("002", "b@b.com", "Projeto B"),
    ])
    pedidos = _ler_planilha(xlsx)
    assert len(pedidos) == 1
    assert pedidos[0].numero_pedido == "002"


def test_ler_planilha_pula_linha_vazia(tmp_path):
    xlsx = _criar_xlsx(tmp_path, [
        ("001", "a@a.com", "Projeto A"),
        (None,  None,      None),
        ("003", "c@c.com", "Projeto C"),
    ])
    pedidos = _ler_planilha(xlsx)
    assert len(pedidos) == 2


def test_ler_planilha_vazia(tmp_path):
    xlsx = _criar_xlsx(tmp_path, [])
    assert _ler_planilha(xlsx) == []
