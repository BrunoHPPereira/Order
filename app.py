from processor import process_order_file
from pathlib import Path

def main():
    print("📦 Iniciando processamento de pedidos...")

    data_dir = Path("Data")
    excel_files = list(data_dir.glob("*.xlsx"))

    if not excel_files:
        print("⚠️ Nenhum arquivo .xlsx encontrado na pasta 'Data/'.")
        return

    for file in excel_files:
        print(f"📄 Processando arquivo: {file.name}")
        process_order_file(str(file))

if __name__ == "__main__":
    main()
