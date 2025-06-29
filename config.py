from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = "order_service"
MONGO_COLLECTION = "orders"
MONGO_COLLECTION_REVIEW = "orders_pending_review"
