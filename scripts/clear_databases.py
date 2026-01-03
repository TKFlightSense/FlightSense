"""FlightSense database reset utility.

This script clears (truncates) all tables in a MySQL database while keeping the
schema intact. It's intended for local/dev resets and demos.

By default it targets the database configured by env vars:
  - MYSQL_HOST (default: localhost)
  - MYSQL_PORT (default: 3306)
  - MYSQL_DATABASE (default: flightsense)
  - MYSQL_USER (default: flightsense)
  - MYSQL_PASSWORD (default: flightsense123)

Safety:
  - Requires --yes to actually execute.
  - Only operates on the database you specify (or MYSQL_DATABASE).

Examples:
  python scripts/clear_databases.py --yes
  python scripts/clear_databases.py --database flightsense --yes

Docker Compose example:
  docker compose exec app python scripts/clear_databases.py --yes
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import List

import mysql.connector
from mysql.connector import Error


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def _get_tables(cursor, database: str) -> List[str]:
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """,
        (database,),
    )
    return [row[0] for row in cursor.fetchall()]


def clear_mysql_database(*, host: str, port: int, user: str, password: str, database: str) -> int:
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
    except Error as e:
        print(f"[ERROR] Could not connect to MySQL: {e}")
        return 2

    try:
        cursor = conn.cursor()
        tables = _get_tables(cursor, database)

        if not tables:
            print(f"[INFO] No tables found in database '{database}'. Nothing to clear.")
            return 0

        print(f"[INFO] Clearing database '{database}' on {host}:{port} as '{user}'")
        print(f"[INFO] Tables ({len(tables)}): {', '.join(tables)}")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in tables:
            cursor.execute(f"TRUNCATE TABLE `{table}`")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        conn.commit()
        print(f"[OK] Cleared {len(tables)} tables in '{database}'.")
        return 0

    except Error as e:
        try:
            conn.rollback()
        except Exception:
            pass
        print(f"[ERROR] Failed while clearing database '{database}': {e}")
        return 3

    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conn.close()


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="Clear (truncate) all tables in the configured MySQL database.")
    parser.add_argument("--host", default=_env("MYSQL_HOST", "localhost"), help="MySQL host")
    parser.add_argument("--port", type=int, default=int(_env("MYSQL_PORT", "3306")), help="MySQL port")
    parser.add_argument("--database", default=_env("MYSQL_DATABASE", "flightsense"), help="Database name")
    parser.add_argument("--user", default=_env("MYSQL_USER", "flightsense"), help="MySQL user")
    parser.add_argument("--password", default=_env("MYSQL_PASSWORD", "flightsense123"), help="MySQL password")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Required confirmation flag. Without this, the script will only print what it would do.",
    )

    args = parser.parse_args(argv)

    if not args.yes:
        print("[SAFE MODE] No changes made (missing --yes).")
        print("Would clear all tables in:")
        print(f"  host={args.host}")
        print(f"  port={args.port}")
        print(f"  database={args.database}")
        print(f"  user={args.user}")
        print("Run again with --yes to execute.")
        return 1

    return clear_mysql_database(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
    )


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
