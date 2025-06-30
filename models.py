from datetime import datetime


def build_order_document(order_id, items, total, destino, origem, impostos, status):
    """Template de estrutura para o banco de dados"""

    return {
        "pedido_id": order_id,
        "data_processamento": datetime.utcnow(),
        "itens": items,
        "total_pedido": total,
        "origem": origem,
        "destino": destino,
        "impostos_totais": impostos,
        "status": status
    }

