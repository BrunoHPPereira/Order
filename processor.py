import polars as pl
from tax_rules import get_tax_rates
from models import build_order_document
from db import get_db_collection, get_db_collection_review
import logging

# Logging configurado
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = {
    "pedido_id", "produto", "categoria",
    "quantidade", "preco_unitario", "origem", "destino"
}

def validate_excel_structure(df: pl.DataFrame):
    """Valida se o DataFrame possui todas as colunas obrigatórias."""
    existing_cols = set(df.columns)
    missing = REQUIRED_COLUMNS - existing_cols
    if missing:
        raise ValueError(
            f"❌ Excel inválido. Colunas ausentes: {', '.join(missing)}. "
            f"Esperadas: {', '.join(REQUIRED_COLUMNS)}"
        )
    logger.info("✅ Estrutura do Excel validada com sucesso.")

def read_orders(filepath: str) -> list[dict]:
    """Lê e valida o arquivo Excel, retornando como lista de dicionários."""
    logger.info(f"📥 Lendo arquivo: {filepath}")
    df = pl.read_excel(filepath)
    validate_excel_structure(df)
    return df.lazy().collect().to_dicts()



def apply_tax_to_row(row: dict) -> dict:
    """Aplica as regras tributárias a uma linha de pedido."""
    rates, found = get_tax_rates(row["categoria"], row["origem"], row["destino"])
    valor_bruto = row["preco_unitario"] * row["quantidade"]
    valor_ibs = valor_bruto * rates["ibs"]
    valor_cbs = valor_bruto * rates["cbs"]
    valor_total = valor_bruto + valor_ibs + valor_cbs
    return {
        **row,
        "valor_bruto": round(valor_bruto, 2),
        "valor_ibs": round(valor_ibs, 2),
        "valor_cbs": round(valor_cbs, 2),
        "valor_total": round(valor_total, 2),
        "taxa_localizada": found,
        "status": "processado" if found else "nao processado"
    }


def organize_orders(rows: list[dict]) -> tuple[dict, list[str]]:
    """Agrupa os itens por pedido e define status de cada um."""
    pedidos_dict = {}
    review_list = []

    for item in rows:
        pid = item["pedido_id"]
        if pid not in pedidos_dict:
            pedidos_dict[pid] = {
                "items": [],
                "total": 0,
                "ibs": 0,
                "cbs": 0,
                "status": item["status"]
            }

        pedidos_dict[pid]["items"].append(item)
        pedidos_dict[pid]["total"] += item["valor_total"]
        pedidos_dict[pid]["ibs"] += item["valor_ibs"]
        pedidos_dict[pid]["cbs"] += item["valor_cbs"]

        if item["status"] == "nao processado":
            pedidos_dict[pid]["status"] = "nao processado"
            review_list.append(pid)

    return pedidos_dict, review_list


def persist_orders(pedidos_dict: dict, review_list: list[str]):
    """Persiste os pedidos no banco conforme status."""
    collection = get_db_collection()
    collection_review = get_db_collection_review()

    for pid, data in pedidos_dict.items():
        origem = data["items"][0]["origem"]
        destino = data["items"][0]["destino"]
        status = data["status"]

        doc = build_order_document(
            pedido_id=pid,
            items=data["items"],
            total=round(data["total"], 2),
            destino=destino,
            origem=origem,
            impostos={"ibs": data["ibs"], "cbs": data["cbs"]},
            status=status
        )

        if status == "processado":
            collection.insert_one(doc)
            logger.info(f"✅ Pedido {pid} processado e salvo com sucesso.")
        else:
            collection_review.insert_one(doc)
            logger.warning(f"⚠️ Pedido {pid} enviado para revisão (regra tributária ausente).")

    logger.info(f"✔️ Pedidos processados: {len(pedidos_dict) - len(review_list)}")
    logger.info(f"❌ Pedidos em revisão: {len(review_list)}")


def process_order_file(filepath: str):
    """Pipeline principal de leitura, processamento e persistência."""
    raw_rows = read_orders(filepath)
    logger.info(f"📄 Linhas lidas: {len(raw_rows)}")

    processed_rows = [apply_tax_to_row(row) for row in raw_rows]
    pedidos_dict, review_list = organize_orders(processed_rows)
    persist_orders(pedidos_dict, review_list)
