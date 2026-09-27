import os
from dotenv import load_dotenv

from database.db import FinanceDatabase

load_dotenv()

def create_database():
    db_path = os.environ.get("DATABASE", "finance.db")
    # Ensure the parent directory exists (e.g. Docker's /app/data volume).
    parent_dir = os.path.dirname(db_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)

    # FinanceDatabase's constructor creates any missing tables from
    # schema.sql and backfills any columns added to an existing table since
    # (see database/db.py). This is the same path webapp/app.py and the
    # importers use, so there's exactly one place responsible for the
    # database's shape.
    db = FinanceDatabase(db_path)
    db.close()
    print(f"✅ Database and tables created/upgraded at {db_path}.")

if __name__ == "__main__":
    create_database()
