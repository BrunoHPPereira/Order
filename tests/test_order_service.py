import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from tax_rules import get_tax_rates
from models import build_order_document

class TestTaxRules(unittest.TestCase):
    def test_eletronico_rates(self):
        rates = get_tax_rates("Eletronico")
        self.assertEqual(rates["ibs"], 0.12)
        self.assertEqual(rates["cbs"], 0.09)

    def test_alimento_rates(self):
        rates = get_tax_rates("Alimento")
        self.assertEqual(rates["ibs"], 0.05)
        self.assertEqual(rates["cbs"], 0.02)

    def test_livro_rates(self):
        rates = get_tax_rates("Livro")
        self.assertEqual(rates["ibs"], 0.00)
        self.assertEqual(rates["cbs"], 0.00)

    def test_default_rates(self):
        rates = get_tax_rates("Outros")
        self.assertEqual(rates["ibs"], 0.10)
        self.assertEqual(rates["cbs"], 0.10)

class TestBuildOrderDocument(unittest.TestCase):
    def test_document_structure(self):
        pedido_id = 1
        items = [
            {
                "produto": "Notebook",
                "categoria": "Eletronico",
                "quantidade": 2,
                "preco_unitario": 3000,
                "valor_bruto": 6000,
                "valor_ibs": 720,
                "valor_cbs": 540
            }
        ]
        total = 6000
        impostos = {"ibs": 720, "cbs": 540}
        doc = build_order_document(pedido_id, items, total, impostos)

        self.assertEqual(doc["pedido_id"], pedido_id)
        self.assertEqual(doc["total_pedido"], total)
        self.assertEqual(doc["itens"], items)
        self.assertEqual(doc["impostos_totais"], impostos)
        self.assertEqual(doc["status"], "processado")
        self.assertIsInstance(doc["data_processamento"], datetime)

class TestMongoInsertion(unittest.TestCase):
    @patch("order_service.MongoClient")
    def test_db_connection(self, mock_mongo_client):
        from db import get_db_collection

        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_mongo_client.return_value.__getitem__.return_value = mock_db
        mock_db.__getitem__.return_value = mock_collection

        collection = get_db_collection()
        self.assertEqual(collection, mock_collection)

if __name__ == "__main__":
    unittest.main()
