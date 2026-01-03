"""Import a FlightSense MySQL database dump created by scripts/export_database.py.

This uses Docker Compose to run `mysql` inside the `mysql` service container and
pipes the dump into it.

Usage:
  python scripts/import_database.py dumps/flightsense_dump_YYYYMMDD_HHMMSS.sql.gz

Notes:
- The export uses --add-drop-table, so importing overwrites existing tables.
- Uses MYSQL_USER/MYSQL_PASSWORD/MYSQL_DATABASE from the MySQL container env.
- Requires: docker + docker compose.
- Assumes compose service name is `mysql`.
"""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Import a .sql or .sql.gz dump into FlightSense MySQL via docker compose.")
    parser.add_argument("dumpfile", help="Path to .sql or .sql.gz dump file")

    args = parser.parse_args(argv)
    dumpfile = pathlib.Path(args.dumpfile)

    if not dumpfile.exists() or not dumpfile.is_file():
        print(f"[ERROR] Dump file not found: {dumpfile}")
        return 2

    print(f"[INFO] Importing into docker compose service 'mysql' from: {dumpfile}")

    if dumpfile.name.endswith(".gz"):
        import_cmd = "gunzip -c | mysql -u\"$MYSQL_USER\" -p\"$MYSQL_PASSWORD\" \"$MYSQL_DATABASE\""
        cmd = ["docker", "compose", "exec", "-T", "mysql", "sh", "-lc", import_cmd]
        with dumpfile.open("rb") as f:
            data = f.read()
    else:
        import_cmd = "mysql -u\"$MYSQL_USER\" -p\"$MYSQL_PASSWORD\" \"$MYSQL_DATABASE\""
        cmd = ["docker", "compose", "exec", "-T", "mysql", "sh", "-lc", import_cmd]
        data = dumpfile.read_bytes()

    try:
        subprocess.run(cmd, input=data, check=True)
    except FileNotFoundError:
        print("[ERROR] docker not found. Install Docker Desktop and ensure `docker` is on PATH.")
        return 2
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Import failed (exit={e.returncode}).")
        return e.returncode or 3

    print("[OK] Import complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
