"""Export the FlightSense MySQL database (schema + data) to a portable dump.

This uses Docker Compose to run `mysqldump` inside the `mysql` service container,
then writes a compressed dump file on the host.

Why this approach?
- It avoids credential guessing: it uses MYSQL_USER/MYSQL_PASSWORD/MYSQL_DATABASE
  from the MySQL container environment (docker-compose.yml / .env).
- The resulting dump can be imported on another machine with the same setup.

Usage:
  python scripts/export_database.py
  python scripts/export_database.py --out dumps/flightsense_dump.sql.gz

Typical flow to share DB with a teammate:
  1) export on your machine
  2) send the .sql.gz file
  3) import on their machine with scripts/import_database.py

Notes:
- Requires: docker + docker compose.
- Assumes compose service name is `mysql`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import subprocess
import sys


def _default_outfile() -> pathlib.Path:
    ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return pathlib.Path("dumps") / f"flightsense_dump_{ts}.sql.gz"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Export FlightSense MySQL DB to a .sql.gz dump via docker compose.")
    parser.add_argument(
        "--out",
        dest="outfile",
        default=str(_default_outfile()),
        help="Output dump path (default: dumps/flightsense_dump_<timestamp>.sql.gz)",
    )

    args = parser.parse_args(argv)
    outfile = pathlib.Path(args.outfile)
    outfile.parent.mkdir(parents=True, exist_ok=True)

    # Dump schema + data in a way that's easy to re-import.
    # --single-transaction: consistent snapshot (InnoDB)
    # --add-drop-table: makes imports repeatable
    # --routines/--triggers: include objects beyond tables
    # --set-gtid-purged=OFF: avoids GTID issues across environments
    # --no-tablespaces: avoids tablespace warnings on some MySQL builds
    dump_cmd = (
        "mysqldump "
        "--single-transaction "
        "--add-drop-table "
        "--routines "
        "--triggers "
        "--set-gtid-purged=OFF "
        "--no-tablespaces "
        "-u\"$MYSQL_USER\" -p\"$MYSQL_PASSWORD\" \"$MYSQL_DATABASE\" "
        "| gzip -9"
    )

    cmd = ["docker", "compose", "exec", "-T", "mysql", "sh", "-lc", dump_cmd]

    print(f"[INFO] Exporting from docker compose service 'mysql'")
    print(f"[INFO] Writing: {outfile}")

    try:
        with outfile.open("wb") as f:
            subprocess.run(cmd, check=True, stdout=f)
    except FileNotFoundError:
        print("[ERROR] docker not found. Install Docker Desktop and ensure `docker` is on PATH.")
        return 2
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Export failed (exit={e.returncode}).")
        return e.returncode or 3

    print(f"[OK] Export complete: {outfile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
