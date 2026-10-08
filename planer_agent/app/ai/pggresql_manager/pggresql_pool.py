from psycopg_pool import ConnectionPool
from dotenv import load_dotenv
import os

load_dotenv()
pool = ConnectionPool(
    conninfo=os.getenv("PG_URL"),
    min_size=10,
    max_size=20,
)