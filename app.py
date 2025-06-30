import logging
import time
from pathlib import Path
from itertools import chain
from processor import process_order_file
import logger_config


logger = logging.getLogger(__name__)

# --- Configuração de diretórios ---
DATA_DIR = Path("data")
INPUT_DIR = DATA_DIR / "input"
PROCESSED_DIR = DATA_DIR / "processed"
ERROR_DIR = DATA_DIR / "error"


def setup_directories():
    """Garante que os diretórios necessários existam."""
    for path in [INPUT_DIR, PROCESSED_DIR, ERROR_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def get_excel_files() -> list[Path]:
    """Busca todos os arquivos Excel na pasta de input."""
    return list(chain(INPUT_DIR.glob("*.xlsx"), INPUT_DIR.glob("*.xls")))


def handle_file(file: Path):
    """Processa um único arquivo, movendo-o após o processamento."""
    try:
        process_order_file(str(file))
        dest = PROCESSED_DIR / file.name
        file.replace(dest)
        logger.info(f"📁 Arquivo movido para: {dest}")
    except Exception as e:
        logger.exception(f"❌ Erro ao processar {file.name}: {e}")
        dest = ERROR_DIR / file.name
        file.replace(dest)
        logger.info(f"📁 Arquivo movido para: {dest}")
        # Se for erro de estrutura, o processor já move para error_dir


def main():
    logger.info("📦 Iniciando processamento de pedidos...")
    setup_directories()

    start_time = time.time()
    files = get_excel_files()

    if not files:
        logger.warning("⚠️ Nenhum arquivo .xlsx ou .xls encontrado na pasta 'data/input/'.")
        return

    for file in files:
        logger.info(f"📄 Processando arquivo: {file.name}")
        handle_file(file)

    duration = round(time.time() - start_time, 2)
    logger.info(f"⏱️ Tempo total de execução: {duration} segundos.")


if __name__ == "__main__":
    main()
