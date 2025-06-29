import polars as pl
from tax_rules import get_tax_rates
from models import build_order_document
from db import get_db_collection
import logging

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def process_order_file(filepath: str):
    logger.info(f"Iniciando leitura do arquivo: {filepath}")
    df = pl.read_excel(filepath).lazy()

    def apply_tax(row):
        rates, found = get_tax_rates(row["categoria"], row["origem"], row["destino"])
        valor_bruto = row["preco_unitario"] * row["quantidade"]
        valor_ibs = valor_bruto * rates["ibs"]
        valor_cbs = valor_bruto * rates["cbs"]
        valor_total = valor_bruto + valor_ibs + valor_cbs
        return {
            "pedido_id": row["pedido_id"],
            "produto": row["produto"],
            "categoria": row["categoria"],
            "quantidade": row["quantidade"],
            "preco_unitario": row["preco_unitario"],
            "origem": row["origem"],
            "destino": row["destino"],
            "valor_bruto": valor_bruto,
            "valor_ibs": round(valor_ibs, 2),
            "valor_cbs": round(valor_cbs, 2),
            "valor_total": round(valor_total, 2),
            "taxa_localizada": found
        }

    df_collect = df.collect().to_dicts()
    pedidos_dict = {}

    logger.info(f"Linhas lidas: {len(df_collect)}")

    for row in df_collect:
        item = apply_tax(row)
        status = "processado" if item["taxa_localizada"] else "nao processado"
        pid = item["pedido_id"]
        if pid not in pedidos_dict:
            pedidos_dict[pid] = {
                "items": [],
                "total": 0,
                "ibs": 0,
                "cbs": 0,
                "status": status
            }
        pedidos_dict[pid]["items"].append(item)
        pedidos_dict[pid]["total"] += item["valor_total"]
        pedidos_dict[pid]["ibs"] += item["valor_ibs"]
        pedidos_dict[pid]["cbs"] += item["valor_cbs"]

    collection = get_db_collection()

    for pid, data in pedidos_dict.items():
        origem = data["items"][0]["origem"]
        destino = data["items"][0]["destino"]

        status = data["status"]
        doc = build_order_document(
            pid,
            data["items"],
            data["total"],
            origem,
            destino,
            {"ibs": data["ibs"], "cbs": data["cbs"]},
            status
        )
        collection.insert_one(doc)
        logger.info(f"Pedido {pid} processado e inserido com sucesso.")

    logger.info(f"✔️ Total de pedidos processados: {len(pedidos_dict)}")
