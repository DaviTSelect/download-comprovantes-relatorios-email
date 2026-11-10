"""
Automação Conveniar → Email

Sem argumentos: abre o painel gráfico (GUI PySide6).
Com --planilha:  processa a planilha em modo CLI sem interface.

Uso:
    python main.py                              # abre o painel
    python main.py --planilha dados/minha.xlsx  # modo CLI
"""
import argparse
import logging
import sys
from pathlib import Path

import openpyxl

from config import USER_EMAIL
from core.conveniar_bot import baixar_arquivos_pedido
from core.send_email import enviar_email
from utils import configurar_logging, salvar_relatorio_erros

# Quando rodando como .exe (PyInstaller frozen), logs ficam na pasta do executável.
# Quando rodando como script, logs ficam no diretório de trabalho corrente.
if getattr(sys, "frozen", False):
    _BASE_DIR = Path(sys.executable).parent
else:
    _BASE_DIR = Path(".")

LOG_DIR = _BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
configurar_logging(LOG_DIR / "app.log")

logger = logging.getLogger(__name__)


def processar_planilha(caminho_planilha: Path) -> None:
    if not caminho_planilha.exists():
        logger.error("Planilha não encontrada: %s", caminho_planilha)
        sys.exit(1)

    wb = openpyxl.load_workbook(caminho_planilha)
    ws = wb.active

    erros: list[dict] = []
    pendentes: list[dict] = []

    # ── Passo 1: baixar todos os arquivos ────────────────────────────────────
    for linha in ws.iter_rows(min_row=2, values_only=True):
        if not linha or not linha[0]:
            continue
        numero_pedido = str(linha[0]).strip()
        email = str(linha[1]).strip() if linha[1] else ""
        if not numero_pedido or not email:
            logger.warning("Linha ignorada — pedido ou e-mail vazio: %s | %s", numero_pedido, email)
            continue
        try:
            logger.info("[Download] Pedido %s", numero_pedido)
            arquivos, nome_projeto = baixar_arquivos_pedido(numero_pedido)
            pendentes.append({"pedido": numero_pedido, "email": email,
                               "arquivos": arquivos, "nome_projeto": nome_projeto})
            logger.info("[Download] Pedido %s concluído (%d arquivo(s))", numero_pedido, len(arquivos))
        except Exception:
            logger.exception("[Download] Erro no pedido %s", numero_pedido)
            erros.append({"pedido": numero_pedido, "email": email, "erro": "falha no download"})

    logger.info("Downloads: %d/%d concluídos", len(pendentes), len(pendentes) + len(erros))

    # ── Passo 2: enviar todos os e-mails ─────────────────────────────────────
    sucesso = 0
    for item in pendentes:
        try:
            logger.info("[Envio] Pedido %s → %s", item["pedido"], item["email"])
            enviar_email(item["email"], item["nome_projeto"], item["arquivos"], USER_EMAIL)
            sucesso += 1
            logger.info("[Envio] Pedido %s enviado com sucesso", item["pedido"])
        except Exception:
            logger.exception("[Envio] Erro no pedido %s", item["pedido"])
            erros.append({"pedido": item["pedido"], "email": item["email"], "erro": "falha no envio"})

    total = len(pendentes) + len([e for e in erros if e["erro"] == "falha no download"])
    logger.info("Concluído: %d/%d enviados com sucesso", sucesso, total)

    if erros:
        logger.warning("%d pedido(s) com erro:", len(erros))
        for e in erros:
            logger.warning("  pedido=%s email=%s erro=%s", e["pedido"], e["email"], e["erro"])
        salvar_relatorio_erros(erros)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automação Conveniar → Email")
    parser.add_argument(
        "--planilha",
        type=Path,
        default=None,
        help="Caminho da planilha (modo CLI). Sem este argumento abre o painel gráfico.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    if args.planilha is None:
        from gui import abrir_janela
        sys.exit(abrir_janela())
    else:
        processar_planilha(args.planilha)
