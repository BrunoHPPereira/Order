import logging
from pymongo.errors import BulkWriteError
from more_itertools import chunked
import polars as pl

from tax_rules import get_tax_rates
from db import get_db_collection, get_db_collection_review
from models import build_order_document

logger = logging.getLogger(__name__)
BULK_CHUNK_SIZE = 1000

REQUIRED_COLUMNS = {
    "pedido_id", "produto", "categoria",
    "quantidade", "preco_unitario", "origem", "destino"
}

def validate_excel_structure(df: pl.DataFrame) -> None:
    """Verifica se todas as colunas obrigatórias estão presentes."""
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        logger.info(f"❌ Excel inválido. Colunas ausentes: {', '.join(missing)}. "
                    f"Esperadas: {', '.join(REQUIRED_COLUMNS)}")
        raise ValueError(f"Excel inválido. Colunas ausentes: {', '.join(missing)}")
    logger.info("✅ Estrutura do Excel validada com sucesso.")

def read_orders(filepath: str) -> list[dict]:
    """Lê e valida um Excel, retornando as linhas como lista de dicionários."""
    logger.info(f"📥 Lendo arquivo: {filepath}")
    df = pl.read_excel(filepath)
    validate_excel_structure(df)
    return df.lazy().collect().to_dicts()

def apply_tax_to_row(row: dict) -> dict:
    """Aplica as regras tributárias e calcula totais."""
    rates, found = get_tax_rates(row["categoria"], row["origem"], row["destino"])
    valor_bruto = row["preco_unitario"] * row["quantidade"]
    valor_ibs = valor_bruto * rates["ibs"]
    valor_cbs = valor_bruto * rates["cbs"]
    return {
        **row,
        "valor_bruto": round(valor_bruto, 2),
        "valor_ibs": round(valor_ibs, 2),
        "valor_cbs": round(valor_cbs, 2),
        "valor_total": round(valor_bruto + valor_ibs + valor_cbs, 2),
        "taxa_localizada": found,
        "status": "processado" if found else "nao processado"
    }

def group_orders(rows: list[dict]) -> dict[str, dict]:
    """Agrupa itens por pedido e consolida valores e status."""
    grouped = {}
    for item in rows:
        pid = item["pedido_id"]
        if pid not in grouped:
            grouped[pid] = {
                "items": [],
                "total": 0.0,
                "ibs": 0.0,
                "cbs": 0.0,
                "status": item["status"]
            }

        grouped[pid]["items"].append(item)
        grouped[pid]["total"] += item["valor_bruto"]
        grouped[pid]["ibs"] += item["valor_ibs"]
        grouped[pid]["cbs"] += item["valor_cbs"]

        if item["status"] == "nao processado":
            grouped[pid]["status"] = "nao processado"

    return grouped

def persist_orders(orders_dict: dict[str, dict]) -> None:
    """Persiste pedidos no MongoDB com inserção em lote otimizada."""
    processados, revisao = [], []

    for pid, data in orders_dict.items():
        doc = build_order_document(
            order_id=pid,
            items=data["items"],
            total=round(data["total"], 2),
            destino=data["items"][0]["destino"],
            origem=data["items"][0]["origem"],
            impostos={
                "ibs": round(data["ibs"], 2),
                "cbs": round(data["cbs"], 2)
            },
            status=data["status"]
        )
        (processados if data["status"] == "processado" else revisao).append(doc)

    safe_bulk_insert(get_db_collection(), processados, "processados")
    safe_bulk_insert(get_db_collection_review(), revisao, "revisão")

    logger.info(f"✔️ Total processados: {len(processados)}")
    logger.info(f"❌ Total em revisão: {len(revisao)}")

def safe_bulk_insert(collection, documents: list[dict], tipo: str) -> None:
    """Executa insert_many com chunking e tratamento de erros."""
    if not documents:
        return

    logger.info(f"⬆️ Inserindo {len(documents)} pedidos '{tipo}'...")
    try:
        for i, chunk in enumerate(chunked(documents, BULK_CHUNK_SIZE), 1):
            collection.insert_many(chunk, ordered=False)
            logger.debug(f"📦 Lote {i} de {tipo}: {len(chunk)} docs.")
        logger.info(f"✅ Pedidos '{tipo}' inseridos com sucesso.")
    except BulkWriteError as e:
        logger.error(f"❌ Falha ao inserir pedidos '{tipo}': {e.details}")

def process_order_file(filepath: str) -> None:
    """Pipeline principal de leitura, processamento e persistência de dados.
    📌 Podemos aplicar multithread caso necessário utilizando ProcessPoolExecutor na função apply_tax_to_row
    devemos apenas se atentar com o usage do CPU, sendo necessária uma avaliação mais detalhada."""

    raw_rows = read_orders(filepath)
    logger.info(f"📄 Linhas lidas: {len(raw_rows)}")
    processed = [apply_tax_to_row(row) for row in raw_rows]
    orders = group_orders(processed)
    persist_orders(orders)
