import logging
from processor import process_order_file
from pathlib import Path
import time
from itertools import chain



# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def main():
    logger.info("📦 Iniciando processamento de pedidos...")

    start_time = time.time()
    data_dir = Path("Data")

    # Busca arquivos .xlsx e .xls
    excel_files = list(chain(data_dir.glob("*.xlsx"), data_dir.glob("*.xls")))

    if not excel_files:
        logger.warning("⚠️ Nenhum arquivo .xlsx ou .xls encontrado na pasta 'Data/'.")
        return

    for file in excel_files:
        logger.info(f"📄 Processando arquivo: {file.name}")
        process_order_file(str(file))

    duration = round(time.time() - start_time, 2)
    logger.info(f"⏱️ Tempo total de execução: {duration} segundos.")

if __name__ == "__main__":
    main()