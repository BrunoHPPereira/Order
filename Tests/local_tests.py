import unittest
from unittest.mock import patch, MagicMock
import polars as pl
from processor import process_order_file


class TestExcelProcessing(unittest.TestCase):
    @patch("polars.read_excel")
    @patch("db.get_db_collection")
    def test_process_order_file_from_excel(self, mock_get_db, mock_read_excel):
        # Simulando conteúdo do Excel
        mock_df = pl.DataFrame([
            {"pedido_id": 1, "produto": "Brahma", "categoria": "Lata 350 ml", "preco_unitario": 3000, "quantidade": 2},
            {"pedido_id": 1, "produto": " Patagonia Amber Lager", "categoria": "Lata 473 ml", "preco_unitario": 200, "quantidade": 1},
            {"pedido_id": 2, "produto": "Hoegarden", "categoria": "Garrafa  350 ml", "preco_unitario": 20, "quantidade": 5}
        ])

        # Mocka o Polars Lazy + collect()
        mock_lazy = MagicMock()
        mock_lazy.collect.return_value = mock_df
        mock_read_excel.return_value.lazy.return_value = mock_lazy

        # Mocka o MongoDB
        mock_collection = MagicMock()
        mock_get_db.return_value = mock_collection

        # Chama o processamento
        process_order_file("fake.xlsx")

        # Espera 2 inserções (pedido_id 1 e 2)
        self.assertEqual(mock_collection.insert_one.call_count, 2)

        # Verifica se campos essenciais foram inseridos
        args, _ = mock_collection.insert_one.call_args
        inserted_doc = args[0]
        self.assertIn("pedido_id", inserted_doc)
        self.assertIn("total_pedido", inserted_doc)
        self.assertIn("status", inserted_doc)
        self.assertIn("impostos_totais", inserted_doc)


if __name__ == "__main__":
    unittest.main()
