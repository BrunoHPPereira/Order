from processor import process_order_file
from pathlib import Path
import time

def main():
    print("📦 Iniciando processamento de pedidos...")

    start_time = time.time()

    data_dir = Path("Data")
    excel_files = list(data_dir.glob("*.xlsx"))

    if not excel_files:
        print("⚠️ Nenhum arquivo encontrado na pasta 'Data/'.")
        return

    for file in excel_files:
        print(f"📄 Processando arquivo: {file.name}")
        process_order_file(str(file))

    duration = round(time.time() - start_time, 2)
    print(f"⏱️ Tempo total de execução: {duration} segundos.")

if __name__ == "__main__":
    main()
