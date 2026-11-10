import csv
from pathlib import Path
from unittest.mock import patch

from utils import salvar_relatorio_erros


def test_salvar_relatorio_erros_cria_csv(tmp_path):
    erros = [
        {"pedido": "123", "email": "a@b.com", "erro": "falha no download"},
        {"pedido": "456", "email": "c@d.com", "erro": "falha no envio"},
    ]
    with patch("utils.Path", lambda *a: tmp_path / Path(*a).name if a else tmp_path):
        # Redireciona a pasta de logs para tmp_path
        import utils
        original = utils.Path
        utils.Path = lambda *a: tmp_path if str(a[0]) == "logs" else original(*a)
        salvar_relatorio_erros(erros)
        utils.Path = original

    csvs = list(tmp_path.glob("erros_*.csv"))
    assert len(csvs) == 1

    with open(csvs[0], encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))

    assert len(linhas) == 2
    assert linhas[0]["pedido"] == "123"
    assert linhas[1]["erro"] == "falha no envio"


def test_salvar_relatorio_erros_cabecalho(tmp_path):
    erros = [{"pedido": "1", "email": "x@y.com", "erro": "timeout"}]
    with patch("utils.Path", lambda *a: tmp_path if str(a[0]) == "logs" else __import__("pathlib").Path(*a)):
        import utils
        original = utils.Path
        utils.Path = lambda *a: tmp_path if str(a[0]) == "logs" else original(*a)
        salvar_relatorio_erros(erros)
        utils.Path = original

    csv_path = next(tmp_path.glob("erros_*.csv"))
    with open(csv_path, encoding="utf-8") as f:
        cabecalho = f.readline().strip()
    assert "pedido" in cabecalho
    assert "email" in cabecalho
    assert "erro" in cabecalho
