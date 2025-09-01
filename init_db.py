import sqlite3

def create_database():
    with open("schema.sql", "r") as f:
        schema = f.read()

    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.executescript(schema)

    conn.commit()
    conn.close()
    print("✅ Database and tables created from schema.sql.")

if __name__ == "__main__":
    create_database()
