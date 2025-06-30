import logging
import shutil

from processor import process_order_file
from pathlib import Path
import time
from itertools import chain
from logger_config import *



logger = logging.getLogger(__name__)

def main():
    logger.info("📦 Iniciando processamento de pedidos...")

    start_time = time.time()
    data_dir = Path("Data")
    input_dir = Path("Data/input")

    # Busca arquivos .xlsx e .xls
    excel_files = list(chain(input_dir.glob("*.xlsx"), data_dir.glob("*.xls")))
    processed_dir = data_dir / "processed"
    processed_dir.mkdir(exist_ok=True)
    error_dir = data_dir / "error"
    error_dir.mkdir(exist_ok=True)

    if not excel_files:
        logger.warning("⚠️ Nenhum arquivo .xlsx ou .xls encontrado na pasta 'Data/'.")
        return

    for file in excel_files:
        try:
            process_order_file(str(file), str(error_dir))
            dest_file = processed_dir / file.name
            file.replace(dest_file)
            logger.info(f"📁 Arquivo movido para: {dest_file}")
        except Exception as e:
            logger.exception(f"❌ Erro ao processar {file.name}: {e}")
            # O arquivo já é movido para o diretório de erro dentro de process_order_file

    duration = round(time.time() - start_time, 2)
    logger.info(f"⏱️ Tempo total de execução: {duration} segundos.")

if __name__ == "__main__":
    main()