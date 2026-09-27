"""Create and manage pyFMgr login accounts.

There's no public sign-up route — this is a shared household app, so
accounts are created out-of-band by whoever runs it. Usage:

    python manage_users.py create-user alice "correct horse battery staple"
    python manage_users.py create-user bob "another-password" --household "Smith House"
    python manage_users.py list-users
"""
import argparse
import os
import sqlite3
import sys

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

from database.db import FinanceDatabase

load_dotenv()

DEFAULT_HOUSEHOLD = "Household"


def _get_or_create_household(conn, name):
    row = conn.execute("SELECT id FROM households WHERE name = ?", (name,)).fetchone()
    if row:
        return row[0]
    cur = conn.execute("INSERT INTO households (name) VALUES (?)", (name,))
    conn.commit()
    return cur.lastrowid


def create_user(username, password, household_name):
    db_path = os.environ.get("DATABASE", "finance.db")
    # FinanceDatabase's constructor creates/upgrades the schema, so this is
    # safe to run against a brand-new database file too.
    db = FinanceDatabase(db_path)
    conn = db.conn
    conn.row_factory = sqlite3.Row

    existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        print(f"User '{username}' already exists.")
        db.close()
        sys.exit(1)

    household_id = _get_or_create_household(conn, household_name)
    conn.execute(
        "INSERT INTO users (household_id, username, password_hash) VALUES (?, ?, ?)",
        (household_id, username, generate_password_hash(password)),
    )
    conn.commit()
    db.close()
    print(f"Created user '{username}' in household '{household_name}'.")


def list_users():
    db_path = os.environ.get("DATABASE", "finance.db")
    db = FinanceDatabase(db_path)
    conn = db.conn
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT users.username, households.name AS household, users.created_at
        FROM users JOIN households ON households.id = users.household_id
        ORDER BY households.name, users.username
        """
    ).fetchall()
    db.close()

    if not rows:
        print("No users yet.")
        return
    for row in rows:
        print(f"{row['username']:<20} household={row['household']:<20} created={row['created_at']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_create = sub.add_parser("create-user", help="Create a new login for a household member")
    p_create.add_argument("username")
    p_create.add_argument("password")
    p_create.add_argument("--household", default=DEFAULT_HOUSEHOLD, help=f"Household name (default: '{DEFAULT_HOUSEHOLD}')")

    sub.add_parser("list-users", help="List existing users and their household")

    args = parser.parse_args()
    if args.command == "create-user":
        create_user(args.username, args.password, args.household)
    elif args.command == "list-users":
        list_users()


if __name__ == "__main__":
    main()
