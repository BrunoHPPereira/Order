import shutil

import polars as pl
from tax_rules import get_tax_rates
from models import build_order_document
from db import get_db_collection, get_db_collection_review
from logger_config import *


logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = {
    "pedido_id", "produto", "categoria",
    "quantidade", "preco_unitario", "origem", "destino"
}

def validate_excel_structure(filepath,df: pl.DataFrame,error_dir):
    """Valida se o DataFrame possui todas as colunas obrigatórias."""
    existing_cols = set(df.columns)
    missing = REQUIRED_COLUMNS - existing_cols
    if missing:
        shutil.move(filepath,error_dir)
        logger.info( f"❌ Excel inválido. Colunas ausentes: {', '.join(missing)}. "
            f"Esperadas: {', '.join(REQUIRED_COLUMNS)}")
        raise ValueError(
            f"❌ Excel inválido. Colunas ausentes: {', '.join(missing)}. "
            f"Esperadas: {', '.join(REQUIRED_COLUMNS)}"
        )
    logger.info("✅ Estrutura do Excel validada com sucesso.")

def read_orders(filepath: str,error_dir) -> list[dict]:
    """Lê e valida o arquivo Excel utilizando função lazy, retornando como lista de dicionários."""
    logger.info(f"📥 Lendo arquivo: {filepath}")
    df = pl.read_excel(filepath)
    validate_excel_structure(filepath,df,error_dir)
    return df.lazy().collect().to_dicts()



def apply_tax_to_row(row: dict) -> dict:
    """Aplica as regras tributárias a uma linha de pedido."""
    rates, found = get_tax_rates(row["categoria"], row["origem"], row["destino"])
    gross_value = row["preco_unitario"] * row["quantidade"]
    ibs_value = gross_value * rates["ibs"]
    cbs_value = gross_value * rates["cbs"]
    total_value = gross_value + ibs_value + cbs_value
    return {
        **row,
        "gross_value": round(gross_value, 2),
        "ibs_value": round(ibs_value, 2),
        "cbs_value": round(cbs_value, 2),
        "total_value": round(total_value, 2),
        "tax_found": found,
        "status": "processado" if found else "nao processado"
    }


def organize_orders(rows: list[dict]) -> tuple[dict, set[str]]:
    """Agrupa os itens por pedido e define status de cada um."""
    orders_dict = {}
    review_set = set()

    for item in rows:
        pid = item["pedido_id"]
        if pid not in orders_dict:
            orders_dict[pid] = {
                "items": [],
                "total": 0,
                "ibs": 0,
                "cbs": 0,
                "status": item["status"]
            }

        orders_dict[pid]["items"].append(item)
        orders_dict[pid]["total"] += item["total_value"]
        orders_dict[pid]["ibs"] += item["ibs_value"]
        orders_dict[pid]["cbs"] += item["cbs_value"]

        if item["status"] == "nao processado":
            orders_dict[pid]["status"] = "nao processado"
            review_set.add(pid)

    return orders_dict, review_set



def persist_orders(orders_dict: dict, review_set: set[str]):
    """Persiste os pedidos no banco conforme status."""
    collection = get_db_collection()
    collection_review = get_db_collection_review()

    for pid, data in orders_dict.items():
        origem = data["items"][0]["origem"]
        destino = data["items"][0]["destino"]
        status = data["status"]

        doc = build_order_document(
            order_id=pid,
            items=data["items"],
            total=round(data["total"], 2),
            destino=destino,
            origem=origem,
            impostos={"ibs": round(data["ibs"], 2), "cbs": round(data["cbs"], 2)},
            status=status
        )

        if status == "processado":
            collection.insert_one(doc)
            logger.info(f"✅ Pedido {pid} processado e salvo com sucesso.")
        else:
            collection_review.insert_one(doc)
            logger.warning(f"⚠️ Pedido {pid} enviado para revisão (regra tributária ausente).")

    logger.info(f"✔️ Pedidos processados: {len(orders_dict) - len(review_set)}")
    logger.info(f"❌ Pedidos em revisão: {len(review_set)}")


def process_order_file(filepath: str,error_dir):
    """Pipeline principal de leitura, processamento e persistência de dados.
    📌 Podemos aplicar multithread caso necessário utilizando ProcessPoolExecutor na função apply_tax_to_row
    devemos apenas se atentar com o usage do CPU, sendo necessária uma avaliação mais detalhada."""

    raw_rows = read_orders(filepath,error_dir)
    logger.info(f"📄 Linhas lidas: {len(raw_rows)}")
    processed_rows = [apply_tax_to_row(row) for row in raw_rows]
    orders_dict, review_list = organize_orders(processed_rows)
    persist_orders(orders_dict, review_list)