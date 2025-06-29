# 🧾 Order Ambev – Processamento Tributário com Python, Polars e MongoDB

Este projeto é um microserviço Python que realiza o **processamento tributário de pedidos** a partir de arquivos Excel, utilizando a biblioteca **Polars (Lazy)** para alta performance e **MongoDB** para persistência dos dados.

---

## 🎯 Objetivo

Desenvolver um serviço robusto e escalável para:
- 📥 Ler pedidos de arquivos Excel
- 🧮 Calcular impostos com base na nova **reforma tributária**
- 📊 Calcular totais por pedido
- 💾 Persistir os dados processados no **MongoDB**

> Capaz de lidar com **até 2 milhões de registros/dia** com performance otimizada.

---

## ⚙️ Funcionalidades

- ✅ Leitura eficiente com Polars Lazy
- ✅ Cálculo de impostos IBS e CBS por item
- ✅ Agrupamento e somatório por pedido
- ✅ Armazenamento dos resultados no MongoDB
- ✅ Modular, simples e pronto para extensões REST

---

## 📁 Estrutura

order_service.py # Código principal consolidado
requirements.txt # Dependências do projeto
pedidos.xlsx # Exemplo de planilha de entrada
.env # Variáveis de ambiente (MONGO_URI)
README.md # Este arquivo

----
2. Crie o arquivo .env

    MONGO_URI=mongodb://localhost:27017---

▶️ Execução

1. Insira a planilha de pedidos na pastsa Data
 - A planilha deve conter as seguintes colunas
   - pedido_id
   - produto
   - categoria
   - preco_unitario
   - quantidade

2. Rode o serviço
   - python order_service.py

3. Você verá no terminal:
📥 Lendo arquivo Excel...
✅ Processamento finalizado: 3 pedidos inseridos no MongoDB.

4. 💾 MongoDB – Exemplo de Documento Armazenado
json
Copiar
Editar
{
  "pedido_id": 1,
  "data_processamento": "2025-06-28T14:03:00Z",
  "itens": [
    {
      "produto": "Notebook",
      "categoria": "Eletronico",
      "quantidade": 2,
      "preco_unitario": 3000,
      "valor_bruto": 6000,
      "valor_ibs": 720,
      "valor_cbs": 540
    },
    {
      "produto": "Fone Bluetooth",
      "categoria": "Eletronico",
      "quantidade": 1,
      "preco_unitario": 200,
      "valor_bruto": 200,
      "valor_ibs": 24,
      "valor_cbs": 18
    }
  ],
  "total_pedido": 6200,
  "impostos_totais": {
    "ibs": 744,
    "cbs": 558
  },
  "status": "processado"
}


5. 🧪 Verificar no MongoDB
Via terminal:

> use order_service
> db.orders.find().pretty()


## 📚 Regras Tributárias

| Categoria          | IBS (%) | CBS (%) |
|--------------------|---------|---------|
| Lata 350 ml        | 12%     | 9%      |
| Garrafa 350 ml     | 5%      | 2%      |
| Lata 473 ml        | 0%      | 0%      |
| Lata sem alcool    | 10%     | 4%      |

---

## 💻 Instalação

### 1. Clone o projeto

```bash
git clone https://github.com/seuusuario/order-ambev.git
cd order-service



Desenho tecnico
┌─────────────────────┐
│  pedidos.xlsx       │
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│ Polars Lazy (Leitura│
│ e transformação)    │
└────────┬────────────┘
         ▼
┌─────────────────────┐
│ Aplicação de regras │ ← tax_rules
│ tributárias (IBS/CBS│
└────────┬────────────┘
         ▼
┌─────────────────────┐
│ Agrupamento por     │
│ pedido_id e cálculo │
└────────┬────────────┘
         ▼
┌─────────────────────┐
│ Persistência no     │
│ MongoDB (JSON)      │
└─────────────────────┘


🧑‍💻 Autor
Bruno Henrique
📧 bruno.dkhenrique@gmail.com
🔗 bruno-pereira-220522
🔗 [Seu GitHub]