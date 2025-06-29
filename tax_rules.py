# tax_rules.py

# Tabela fictícia de alíquotas IBS/CBS por tipo + origem/destino
PRODUCT_TAX_RULES = {
    "lata 350 ml": {
        ("SP", "SP"): {"ibs": 0.12, "cbs": 0.09},
        ("SP", "RJ"): {"ibs": 0.15, "cbs": 0.10},
        ("RJ", "SP"): {"ibs": 0.10, "cbs": 0.08}
    },
    "garrafa 350 ml": {
        ("SP", "SP"): {"ibs": 0.05, "cbs": 0.02},
        ("SP", "RJ"): {"ibs": 0.07, "cbs": 0.03}
    },
    "lata 473 ml": {
        ("SP", "SP"): {"ibs": 0.00, "cbs": 0.00},
        ("SP", "RJ"): {"ibs": 0.01, "cbs": 0.01}
    },
    "lata sem alcool": {
        ("SP", "SP"): {"ibs": 0.10, "cbs": 0.40},
        ("SP", "RJ"): {"ibs": 0.12, "cbs": 0.45}
    }
}

def get_tax_rates(categoria, uf_origem, uf_destino):
    key = categoria.lower()
    uf_key = (uf_origem.upper(), uf_destino.upper())
    regras_produto = PRODUCT_TAX_RULES.get(key, {})
    if uf_key in regras_produto:
        return regras_produto[uf_key], True
    return {"ibs": 0.1, "cbs": 0.1}, False  # regra default, não localizada

