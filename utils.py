import csv
import logging
from datetime import datetime
from pathlib import Path


def configurar_logging(caminho_log: Path) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(caminho_log, encoding="utf-8"),
        ],
    )


def salvar_relatorio_erros(erros: list[dict]) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    caminho = Path("logs") / f"erros_{timestamp}.csv"
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["pedido", "email", "erro"])
        writer.writeheader()
        writer.writerows(erros)
    logging.getLogger(__name__).warning("Relatório de erros salvo em %s", caminho)
