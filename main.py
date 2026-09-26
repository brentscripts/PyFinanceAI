import os
import sys
from dotenv import load_dotenv
from importers.bank import BankCSVImporter
from importers.chase import ChaseCSVImporter
from database.db import FinanceDatabase

load_dotenv()

def load_csv(filepath, source):
    if source == 'bank':
        importer = BankCSVImporter()
    elif source == 'chase':
        importer = ChaseCSVImporter()
    else:
        raise ValueError(f"Unknown source {source}")

    transactions = importer.parse(filepath)

    db_path = os.environ.get("DATABASE", "finance.db")
    db = FinanceDatabase(db_path)
    db.insert_transactions(transactions)
    print(f"Inserted {len(transactions)} transactions from {source}.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <csv_path> <source>")
        sys.exit(1)

    path = sys.argv[1]
    source = sys.argv[2].lower()
    load_csv(path, source)

