"""Create or reset an admin user in the FlightSense MySQL database.

Use this when `user_data` was cleared and you need a known admin login.

Defaults:
  - username: admin
  - password: rootroot
  - role: admin
  - email/department: NULL

It is idempotent:
  - If the user exists, it updates password_hash/role/is_active.
  - If the user does not exist, it inserts a new row.

Connection uses environment variables (same as the app):
  - MYSQL_HOST (default: localhost)
  - MYSQL_PORT (default: 3306)
  - MYSQL_DATABASE (default: flightsense)
  - MYSQL_USER (default: flightsense)
  - MYSQL_PASSWORD (default: flightsense123)

Examples:
  python scripts/create_admin_user.py
  python scripts/create_admin_user.py --username admin --password rootroot

Docker Compose (recommended):
  docker compose exec app python scripts/create_admin_user.py
"""

from __future__ import annotations

import argparse
import os
import sys

import bcrypt
import mysql.connector
from mysql.connector import Error


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Create/reset an admin user in MySQL.")
    parser.add_argument("--host", default=_env("MYSQL_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(_env("MYSQL_PORT", "3306")))
    parser.add_argument("--database", default=_env("MYSQL_DATABASE", "flightsense"))
    parser.add_argument("--user", dest="db_user", default=_env("MYSQL_USER", "flightsense"))
    parser.add_argument("--db-password", dest="db_password", default=_env("MYSQL_PASSWORD", "flightsense123"))

    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="rootroot")
    parser.add_argument("--role", default="admin")

    args = parser.parse_args(argv)

    password_hash = _hash_password(args.password)

    try:
        conn = mysql.connector.connect(
            host=args.host,
            port=args.port,
            user=args.db_user,
            password=args.db_password,
            database=args.database,
        )
    except Error as e:
        print(f"[ERROR] Could not connect to MySQL: {e}")
        return 2

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO user_data (username, email, password_hash, role, department, is_active)
            VALUES (%s, %s, %s, %s, %s, 1)
            ON DUPLICATE KEY UPDATE
                password_hash = VALUES(password_hash),
                role = VALUES(role),
                department = VALUES(department),
                is_active = 1
            """,
            (args.username, None, password_hash, args.role, None),
        )
        conn.commit()

        cursor.execute("SELECT id, username, role, department, is_active FROM user_data WHERE username = %s", (args.username,))
        row = cursor.fetchone()

        if row:
            print(f"[OK] Admin user ready: id={row[0]} username={row[1]} role={row[2]} is_active={row[4]}")
        else:
            print("[WARN] User upsert ran but could not re-read the row.")

        return 0

    except Error as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print(f"[ERROR] Failed to create/reset admin user: {e}")
        return 3

    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
