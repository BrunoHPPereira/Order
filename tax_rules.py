# tax_rules.py
import logging
logger = logging.getLogger(__name__)


# Tabela fictícia de alíquotas IBS/CBS por tipo + origem/destino
PRODUCT_TAX_RULES = {
    "lata 350 ml": {
        ("SP", "SP"): {"ibs": 0.12, "cbs": 0.09},
        ("SP", "RJ"): {"ibs": 0.15, "cbs": 0.10},
        ("SP", "PR"): {"ibs": 0.9, "cbs": 0.08},
        ("SP", "SC"): {"ibs": 0.14, "cbs": 0.08}
    },
    "garrafa 350 ml": {
        ("SP", "SP"): {"ibs": 0.05, "cbs": 0.02},
        ("SP", "RJ"): {"ibs": 0.07, "cbs": 0.03},
        ("SP", "PR"): {"ibs": 0.9, "cbs": 0.08},
        ("SP", "SC"): {"ibs": 0.14, "cbs": 0.08}
    },
    "lata 473 ml": {
        ("SP", "SP"): {"ibs": 0.00, "cbs": 0.00},
        ("SP", "RJ"): {"ibs": 0.01, "cbs": 0.01},
        ("SP", "PR"): {"ibs": 0.9, "cbs": 0.08},
        ("SP", "SC"): {"ibs": 0.14, "cbs": 0.08}
    },
    "lata sem alcool": {
        ("SP", "SP"): {"ibs": 0.10, "cbs": 0.40},
        ("SP", "RJ"): {"ibs": 0.12, "cbs": 0.45},
        ("SP", "PR"): {"ibs": 0.9, "cbs": 0.08},
        ("SP", "SC"): {"ibs": 0.14, "cbs": 0.08}
    }
}

def get_tax_rates(categoria, uf_origem, uf_destino):
    key = categoria.lower()
    uf_key = (uf_origem.upper(), uf_destino.upper())
    regras_produto = PRODUCT_TAX_RULES.get(key, {})
    if uf_key in regras_produto:
        return regras_produto[uf_key], True

    logger.warning(
        f"Nenhuma regra de taxa localizada para categoria='{categoria}', origem='{uf_origem}', destino='{uf_destino}'."
    )
    return {"ibs": 0, "cbs": 0}, False

