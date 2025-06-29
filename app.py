from processor import process_order_file

def main():
    print("📦 Iniciando processamento de pedidos...")
    process_order_file("Data/orders.xlsx")

if __name__ == "__main__":
    main()
