import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def create_database():
    db_path = os.environ.get("DATABASE", "finance.db")
    # Ensure the parent directory exists (e.g. Docker's /app/data volume).
    parent_dir = os.path.dirname(db_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
    with open(schema_path, "r") as f:
        schema = f.read()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.executescript(schema)

    conn.commit()
    conn.close()
    print(f"✅ Database and tables created from schema.sql at {db_path}.")

if __name__ == "__main__":
    create_database()
