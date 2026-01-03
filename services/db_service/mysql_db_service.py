import mysql.connector
from mysql.connector import Error, pooling
import pandas as pd
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import logging
import os
from decimal import Decimal
import csv

from models.labels import ALL_LABELS
from models.enums.enums import DepartmentTables, DepartmentToLabels
from datetime import date, datetime, time

# Set up logging
logger = logging.getLogger(__name__)


class MySQLDbService:
    """
    MySQL database service for production deployment.
    Implements the same interface as DbService for compatibility.
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        pool_size: int = 5,
    ):
        """
        Initialize MySQL database connection with connection pooling.

        Args:
            host: MySQL server host (default: from env MYSQL_HOST)
            port: MySQL server port (default: from env MYSQL_PORT)
            database: Database name (default: from env MYSQL_DATABASE)
            user: MySQL user (default: from env MYSQL_USER)
            password: MySQL password (default: from env MYSQL_PASSWORD)
            pool_size: Connection pool size
        """
        self.host = host or os.getenv("MYSQL_HOST", "localhost")
        self.port = port or int(os.getenv("MYSQL_PORT", "3306"))
        self.database = database or os.getenv("MYSQL_DATABASE", "flightsense")
        self.user = user or os.getenv("MYSQL_USER", "flightsense")
        self.password = password or os.getenv("MYSQL_PASSWORD", "")

        self.pool = None
        # Database is created by Docker container (MYSQL_DATABASE env var)
        # We don't need to create it manually, and the user might not have permissions.
        # self._create_database_if_not_exists()
        self._create_connection_pool(pool_size)
        self._create_tables()
        logger.info(f"MySQL DbService initialized: {self.host}:{self.port}/{self.database}")

    # -------------------------------------------------------------------------
    # CONNECTION MANAGEMENT
    # -------------------------------------------------------------------------

    def _create_connection_pool(self, pool_size: int):
        """Create MySQL connection pool."""
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name="flightsense_pool",
                pool_size=pool_size,
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                autocommit=False,
            )
            logger.info(f"Created MySQL connection pool (size={pool_size})")
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise

    def _get_connection(self):
        """Get connection from pool."""
        try:
            return self.pool.get_connection()
        except Error as e:
            logger.error(f"Error getting connection from pool: {e}")
            raise

    def _create_database_if_not_exists(self):
        """Create database if it doesn't exist."""
        try:
            # Connect without database
            conn = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            conn.commit()
            cursor.close()
            conn.close()
            logger.info(f"Database '{self.database}' ensured")
        except Error as e:
            logger.error(f"Error creating database: {e}")
            raise

    def _create_tables(self):
        """Create all necessary tables if they don't exist."""
        self._create_reviews_table()
        self._migrate_reviews_table()  # Add missing columns if needed
        self._create_review_details_table()
        self._create_tickets_table()
        self._create_user_table()
        self._create_cagri_merkezi_table()
        self._create_ikram_ucak_ici_table()
        self._create_kabin_hizmetleri_table()
        self._create_rez_biletleme_table()
        self._create_tgs_table()
        self._create_yer_isletme_bagaj_table()
        self._create_gelir_yonetimi_table()
        self._create_airport_coordinates_table()
        self._create_review_processing_status_table()
        self._create_review_status_table()
        logger.info("All MySQL tables created/verified successfully")

    # -------------------------------------------------------------------------
    # TABLE CREATION
    # -------------------------------------------------------------------------
    def _create_reviews_table(self):
        """Create processed_data table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            review TEXT,
            date DATE,
            flight_number VARCHAR(50),
            pnr VARCHAR(50),
            origin_iata VARCHAR(50),
            destination_iata VARCHAR(50),
            route VARCHAR(50),
            bidirectional_route VARCHAR(50),
            INDEX idx_date (date),
            INDEX idx_flight_number (flight_number),
            INDEX idx_pnr (pnr),
            INDEX idx_bidirectional_route (bidirectional_route),
            INDEX idx_route (route)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'reviews' created/verified")
        except Error as e:
            logger.error(f"Error creating reviews table: {e}")
            raise
        finally:
            conn.close()

    def _migrate_reviews_table(self):
        """Add missing columns to reviews table (for existing databases)."""
        columns_to_add = [
            ("origin_iata", "VARCHAR(50)"),
            ("destination_iata", "VARCHAR(50)"),
            ("route", "VARCHAR(50)"),
            ("bidirectional_route", "VARCHAR(50)"),
        ]
        
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            
            # Check existing columns
            cursor.execute("DESCRIBE reviews")
            existing_columns = {row[0] for row in cursor.fetchall()}
            
            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    alter_query = f"ALTER TABLE reviews ADD COLUMN {col_name} {col_type}"
                    cursor.execute(alter_query)
                    logger.info(f"Added column '{col_name}' to reviews table")
            
            # Add indexes if they don't exist (ignore errors if they already exist)
            index_queries = [
                "CREATE INDEX idx_route ON reviews(route)",
                "CREATE INDEX idx_bidirectional_route ON reviews(bidirectional_route)",
            ]
            for idx_query in index_queries:
                try:
                    cursor.execute(idx_query)
                except Error:
                    pass  # Index already exists
            
            conn.commit()
            cursor.close()
        except Error as e:
            logger.error(f"Error migrating reviews table: {e}")
            # Don't raise - migration is best-effort for backwards compatibility
        finally:
            conn.close()

    def _create_review_processing_status_table(self):
        """
        Create review_processing_status table in MySQL.

        This table is used to track processing state per review_id to prevent
        re-processing loops (e.g., when no segments are extracted) and to
        provide an atomic claim mechanism across multiple workers.

        Conventions:
          - status=0: PENDING
          - status=1: PROCESSING
          - status=4: COMPLETED
          - status=-1: FAILED
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS review_processing_status (
            review_id INT PRIMARY KEY,
            status INT NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_status (status),
            CONSTRAINT fk_rps_review FOREIGN KEY (review_id)
                REFERENCES reviews(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'review_processing_status' created/verified")
        except Error as e:
            logger.error(f"Error creating review_processing_status table: {e}")
            raise
        finally:
            conn.close()

    def _create_review_status_table(self):
        """
        Create review_status table in MySQL (single-row tracker).

        NOTE: Earlier iterations of this project used a per-review `review_status` table.
        The Streamlit status UI (`services/review_status/app.py`) expects the single-row
        tracker schema with `id=1` + `tracking_enabled`.

        If an existing per-review `review_status` table is detected (no `id` column),
        it is migrated to `review_processing_status` and the tracker table is created.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS review_status (
            id TINYINT PRIMARY KEY DEFAULT 1,
            review_id INT NULL,
            status INT NOT NULL DEFAULT 0,
            tracking_enabled TINYINT(1) NOT NULL DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_review_status_review_id (review_id),
            CONSTRAINT fk_review_status_review FOREIGN KEY (review_id)
                REFERENCES reviews(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()

            # Migration: if `review_status` exists but doesn't have `id`, it's the legacy per-review schema.
            cursor.execute("SHOW TABLES LIKE 'review_status'")
            has_table = cursor.fetchone() is not None
            if has_table:
                cursor.execute("SHOW COLUMNS FROM review_status")
                cols = {r[0] for r in cursor.fetchall()}
                if "id" not in cols:
                    # Copy existing data into review_processing_status (best-effort), then rename the old table.
                    try:
                        cursor.execute(
                            """
                            INSERT IGNORE INTO review_processing_status (review_id, status)
                            SELECT review_id, status FROM review_status
                            """
                        )
                    except Exception:
                        # Older schemas may not match; continue with rename anyway.
                        pass

                    # Preserve legacy table for debugging; overwrite an old backup if present.
                    cursor.execute("DROP TABLE IF EXISTS review_status_legacy")
                    cursor.execute("RENAME TABLE review_status TO review_status_legacy")
                    conn.commit()

            cursor.execute(create_table_query)
            # Ensure the single row exists for Streamlit UI toggles.
            cursor.execute(
                """
                INSERT IGNORE INTO review_status (id, review_id, status, tracking_enabled)
                VALUES (1, NULL, 0, 0)
                """
            )
            conn.commit()
            cursor.close()
            logger.info("Table 'review_status' created/verified")
        except Error as e:
            logger.error(f"Error creating review_status table: {e}")
            raise
        finally:
            conn.close()
    
    def _create_airport_coordinates_table(self):
        """Create airport_coordinates table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS airport_coordinates (
            iata_code VARCHAR(10) PRIMARY KEY,
            latitude DOUBLE NOT NULL,
            longitude DOUBLE NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'airport_coordinates' created/verified")
        except Error as e:
            logger.error(f"Error creating airport_coordinates table: {e}")
            raise
        finally:
            conn.close()

    def _create_tickets_table(self):
        """Create tickets table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tickets (
            id INT AUTO_INCREMENT PRIMARY KEY,
            processed_data_id INT,
            primary_label VARCHAR(100),
            department VARCHAR(255),
            summary VARCHAR(500) NOT NULL,
            description TEXT NOT NULL,
            external_key VARCHAR(50),
            source VARCHAR(20) DEFAULT 'mock',
            status VARCHAR(20) DEFAULT 'OPEN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_processed_data_id (processed_data_id),
            INDEX idx_status (status),
            INDEX idx_external_key (external_key),
            FOREIGN KEY (processed_data_id) REFERENCES reviews(id) ON DELETE SET NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'tickets' created/verified")
        except Error as e:
            logger.error(f"Error creating tickets table: {e}")
            raise
        finally:
            conn.close()

    def _create_kabin_hizmetleri_table(self):
        """Create kabin_hizmetleri table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS kabin_hizmetleri (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            label VARCHAR(255) NOT NULL,
            date_from DATETIME,
            date_to DATETIME,
            positive_count INT DEFAULT 0,
            negative_count INT DEFAULT 0,
            neutral_count INT DEFAULT 0,
            low_count INT DEFAULT 0,
            medium_count INT DEFAULT 0,
            high_count INT DEFAULT 0,
            
            INDEX idx_label (label),
            INDEX idx_analysis_range (label, date_from, date_to)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'kabin_hizmetleri' created/verified")
        except Error as e:
            logger.error(f"Error creating kabin_hizmetleri table: {e}")
            raise
        finally:
            conn.close()

    def _create_ikram_ucak_ici_table(self):
        """Create ikram_ucak_ici table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS ikram_ucak_ici (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            label VARCHAR(255) NOT NULL,
            date_from DATETIME,
            date_to DATETIME,
            positive_count INT DEFAULT 0,
            negative_count INT DEFAULT 0,
            neutral_count INT DEFAULT 0,
            low_count INT DEFAULT 0,
            medium_count INT DEFAULT 0,
            high_count INT DEFAULT 0,
            
            INDEX idx_label (label),
            INDEX idx_analysis_range (label, date_from, date_to)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'ikram_ucak_ici' created/verified")
        except Error as e:
            logger.error(f"Error creating ikram_ucak_ici table: {e}")
            raise
        finally:
            conn.close()

    def _create_yer_isletme_bagaj_table(self):
        """Create yer_isletme_bagaj table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS yer_isletme_bagaj (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            label VARCHAR(255) NOT NULL,
            date_from DATETIME,
            date_to DATETIME,
            positive_count INT DEFAULT 0,
            negative_count INT DEFAULT 0,
            neutral_count INT DEFAULT 0,
            low_count INT DEFAULT 0,
            medium_count INT DEFAULT 0,
            high_count INT DEFAULT 0,
            
            INDEX idx_label (label),
            INDEX idx_analysis_range (label, date_from, date_to)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'yer_isletme_bagaj' created/verified")
        except Error as e:
            logger.error(f"Error creating yer_isletme_bagaj table: {e}")
            raise
        finally:
            conn.close()

    def _create_tgs_table(self):
        """Create tgs table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tgs (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            label VARCHAR(255) NOT NULL,
            date_from DATETIME,
            date_to DATETIME,
            positive_count INT DEFAULT 0,
            negative_count INT DEFAULT 0,
            neutral_count INT DEFAULT 0,
            low_count INT DEFAULT 0,
            medium_count INT DEFAULT 0,
            high_count INT DEFAULT 0,
            
            INDEX idx_label (label),
            INDEX idx_analysis_range (label, date_from, date_to)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'tgs' created/verified")
        except Error as e:
            logger.error(f"Error creating tgs table: {e}")
            raise
        finally:
            conn.close()

    def _create_rez_biletleme_table(self):
        """Create rez_biletleme table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS rez_biletleme (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            label VARCHAR(255) NOT NULL,
            date_from DATETIME,
            date_to DATETIME,
            positive_count INT DEFAULT 0,
            negative_count INT DEFAULT 0,
            neutral_count INT DEFAULT 0,
            low_count INT DEFAULT 0,
            medium_count INT DEFAULT 0,
            high_count INT DEFAULT 0,
            
            INDEX idx_label (label),
            INDEX idx_analysis_range (label, date_from, date_to)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'rez_biletleme' created/verified")
        except Error as e:
            logger.error(f"Error creating rez_biletleme table: {e}")
            raise
        finally:
            conn.close()

    def _create_cagri_merkezi_table(self):
        """Create cagri_merkezi table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS cagri_merkezi (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            label VARCHAR(255) NOT NULL,
            date_from DATETIME,
            date_to DATETIME,
            positive_count INT DEFAULT 0,
            negative_count INT DEFAULT 0,
            neutral_count INT DEFAULT 0,
            low_count INT DEFAULT 0,
            medium_count INT DEFAULT 0,
            high_count INT DEFAULT 0,
            
            INDEX idx_label (label),
            INDEX idx_analysis_range (label, date_from, date_to)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'cagri_merkezi' created/verified")
        except Error as e:
            logger.error(f"Error creating cagri_merkezi table: {e}")
            raise
        finally:
            conn.close()

    def _create_gelir_yonetimi_table(self):
        """Create gelir_yonetimi table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS gelir_yonetimi (
            ID INT AUTO_INCREMENT PRIMARY KEY,
            label VARCHAR(255) NOT NULL,
            date_from DATETIME,
            date_to DATETIME,
            positive_count INT DEFAULT 0,
            negative_count INT DEFAULT 0,
            neutral_count INT DEFAULT 0,
            low_count INT DEFAULT 0,
            medium_count INT DEFAULT 0,
            high_count INT DEFAULT 0,
            
            INDEX idx_label (label),
            INDEX idx_analysis_range (label, date_from, date_to)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'gelir_yonetimi' created/verified")
        except Error as e:
            logger.error(f"Error creating gelir_yonetimi table: {e}")
            raise
        finally:
            conn.close()

    def _create_user_table(self):
        """Create user_data table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) DEFAULT 'viewer',
            department VARCHAR(255),
            is_active TINYINT(1) DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP NULL,
            INDEX idx_username (username),
            INDEX idx_email (email),
            INDEX idx_role (role)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'user_data' created/verified")
        except Error as e:
            logger.error(f"Error creating user_data table: {e}")
            raise
        finally:
            conn.close()

    def _create_review_details_table(self):
        """Create review_details table to store per-segment labels for reviews.

        Columns (requested order / semantics):
          - id: primary key
          - review_id: references processed_data.id
          - label: canonical label string
          - `index`: text in format "start:end" (e.g. "130:150")
          - sentiment: POSITIVE / NEGATIVE / NEUTRAL / NONE
          - priority: HIGH / MEDIUM / LOW / unknown
          - created_at: timestamp
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS processed_reviews (
            id INT AUTO_INCREMENT PRIMARY KEY,
            review_id INT NOT NULL,
            label VARCHAR(255) NOT NULL,
            `index` VARCHAR(50) DEFAULT NULL,
            sentiment VARCHAR(50) DEFAULT 'NONE',
            priority VARCHAR(50) DEFAULT 'unknown',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_review_id (review_id),
            INDEX idx_label (label),
            FOREIGN KEY (review_id) REFERENCES reviews(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """

        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'processed_reviews' created/verified")
        except Error as e:
            logger.error(f"Error creating review_details table: {e}")
            raise
        finally:
            conn.close()

    def insert_processed_data_row(
        self,
        review: str,
        date: Optional[str] = None,
        flight_number: Optional[str] = None,
        pnr: Optional[str] = None,
    ) -> int:
        """Insert a single processed_data row and return the inserted id.

        This is useful when callers need the auto-incremented `id` to reference
        from related tables (e.g., `review_details`).
        """
        query = """
        INSERT INTO reviews (review, date, flight_number, pnr)
        VALUES (%s, %s, %s, %s)
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(query, (review, date, flight_number, pnr))
            conn.commit()
            inserted_id = cursor.lastrowid
            cursor.close()
            logger.info(f"Inserted reviews id={inserted_id}")
            return inserted_id
        except Error as e:
            logger.error(f"Error inserting processed_data row: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def insert_review_details_bulk(self, rows: List[Dict[str, Any]]) -> int:
        """Bulk insert review_details rows.

        `rows` should be a list of dicts with keys: review_id, label, index, sentiment, priority
        Returns number of rows inserted.
        """
        if not rows:
            return 0

        query = """
        INSERT INTO processed_reviews (review_id, label, `index`, sentiment, priority)
        VALUES (%s, %s, %s, %s, %s)
        """
        data = []
        for r in rows:
            data.append((
                r.get("review_id"),
                r.get("label"),
                r.get("index"),
                r.get("sentiment", "NONE"),
                r.get("priority", "unknown"),
            ))

        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.executemany(query, data)
            conn.commit()
            inserted = cursor.rowcount
            cursor.close()
            logger.info(f"Inserted {inserted} rows into processed_reviews")
            return inserted
        except Error as e:
            logger.error(f"Error inserting review_details rows: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def upsert_review_status(
        self, status: int, review_id: Optional[int], tracking_enabled: bool = True
    ) -> None:
        """
        Single-row tracker (id=1) with monotonic progression.
        - Preserves existing review_id once set.
        - Blocks jumping from 1 -> 3; -1 (FAILED) always allowed.
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            conn.start_transaction()

            cursor.execute(
                "SELECT id, review_id, status, tracking_enabled FROM review_status WHERE id = 1 FOR UPDATE"
            )
            row = cursor.fetchone()

            current_id = None
            current_review_id = None
            current_status = None
            current_tracking = None
            if row:
                current_id, current_review_id, current_status, current_tracking = row

            # Decide if we allow the new status
            allow_update = False
            if current_status is None:
                allow_update = True  # first write
            elif status == -1:
                allow_update = True  # failures always allowed
            elif status == 3 and current_status < 2:
                allow_update = False  # block premature COMPLETED
            elif status < current_status:
                allow_update = False  # block regressions
            else:
                allow_update = True  # forward/duplicate moves allowed

            if row is None:
                cursor.execute(
                    """
                    INSERT INTO review_status (id, review_id, status, tracking_enabled)
                    VALUES (1, %s, %s, %s)
                    """,
                    (review_id, status, 1 if tracking_enabled else 0),
                )
            elif allow_update:
                # Keep the original review_id once set
                effective_review_id = current_review_id if current_review_id is not None else review_id
                cursor.execute(
                    """
                    UPDATE review_status
                    SET review_id = %s,
                        status = %s,
                        tracking_enabled = %s
                    WHERE id = 1
                    """,
                    (effective_review_id, status, 1 if tracking_enabled else 0),
                )
            # else: blocked update; keep current state

            conn.commit()
            cursor.close()
        except Error as e:
            logger.error(f"Error upserting review_status: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()


    # Backward compatibility: alias
    def get_latest_review_status(self):
        return self.get_review_status()

    def get_review_status(self) -> Optional[Dict[str, Any]]:
        """
        Returns the single-row tracker (id=1) joined with its review.
        """
        query = """
        SELECT rs.review_id, rs.status, rs.tracking_enabled,
               r.review, r.flight_number, r.pnr, r.date
        FROM review_status rs
        LEFT JOIN reviews r ON r.id = rs.review_id
        WHERE rs.id = 1
        LIMIT 1
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            row = cursor.fetchone()
            cursor.close()
            return row
        except Error as e:
            logger.error(f"Error reading review_status: {e}")
            raise
        finally:
            conn.close()

    # Backward compatibility: alias
    def get_latest_review_status(self):
        return self.get_review_status()



    def upsert_review_processing_status(self, review_id: int, status: int) -> None:
        query = """
        INSERT INTO review_processing_status (review_id, status)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE status = VALUES(status)
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(query, (review_id, status))
            conn.commit()
            cursor.close()
        except Error as e:
            logger.error(f"Error upserting review_processing_status for review_id={review_id}: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def claim_review_for_processing(self, review_id: int) -> bool:
        """
        Atomically claim a review for processing by transitioning its status to PROCESSING.

        This prevents concurrent workers (or repeated triggers) from processing the same review twice.

        Conventions:
          - status=0: PENDING (or missing row)
          - status=1: PROCESSING
          - status=4: COMPLETED
          - status=-1: FAILED
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            conn.start_transaction()

            cursor.execute(
                "SELECT status FROM review_processing_status WHERE review_id = %s FOR UPDATE",
                (review_id,),
            )
            row = cursor.fetchone()

            if row is None:
                cursor.execute(
                    "INSERT INTO review_processing_status (review_id, status) VALUES (%s, %s)",
                    (review_id, 1),
                )
                conn.commit()
                return True

            # mysql-connector returns a tuple for non-dictionary cursors
            current_status = row[0]
            if current_status != 0:
                conn.rollback()
                return False

            cursor.execute(
                "UPDATE review_processing_status SET status = %s WHERE review_id = %s AND status = %s",
                (1, review_id, 0),
            )
            claimed = cursor.rowcount == 1
            if claimed:
                conn.commit()
            else:
                conn.rollback()
            return claimed
        except Error as e:
            logger.error(f"Error claiming review_processing_status for review_id={review_id}: {e}")
            try:
                conn.rollback()
            except Exception:
                pass
            return False
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            conn.close()

    # -------------------------------------------------------------------------
    # PROCESSED DATA OPERATIONS
    # -------------------------------------------------------------------------

    def push_processed_data(self, df: pd.DataFrame) -> int:
        """Push DataFrame to reviews table with full schema support."""
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()

            query = """
            INSERT INTO reviews (review, date, flight_number, pnr, origin_iata, destination_iata, route, bidirectional_route)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            data = []
            for _, row in df.iterrows():
                data.append((
                    row.get("review"),
                    row.get("date") or row.get("review_date"),  # Support both column names
                    row.get("flight_number"),
                    row.get("pnr"),
                    row.get("origin_iata"),
                    row.get("destination_iata"),
                    row.get("route"),
                    row.get("bidirectional_route"),
                ))

            cursor.executemany(query, data)
            conn.commit()
            rows_inserted = cursor.rowcount
            cursor.close()
            logger.info(f"Inserted {rows_inserted} rows into reviews")
            return rows_inserted
        except Error as e:
            logger.error(f"Error pushing data: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_processed_data(
        self,
        limit: Optional[int] = None,
        label_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> pd.DataFrame:
        """Retrieve processed data with optional filters."""
        # Join with processed_reviews to get labels
        query = """
        SELECT r.*, GROUP_CONCAT(pr.label) as labels
        FROM reviews r
        LEFT JOIN processed_reviews pr ON r.id = pr.review_id
        WHERE 1=1
        """
        params: List[Any] = []

        if date_from:
            query += " AND r.date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND r.date <= %s"
            params.append(date_to)

        query += " GROUP BY r.id ORDER BY r.date DESC"

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        conn = self._get_connection()
        try:
            conn.database = self.database
            df = pd.read_sql_query(query, conn, params=params if params else None)
            
            # If label_type was requested, filter the DataFrame (since we didn't filter in SQL)
            if label_type and not df.empty:
                # Filter rows where 'labels' column contains the label_type
                # labels is comma-separated
                mask = df['labels'].fillna('').apply(lambda x: label_type in x.split(','))
                df = df[mask]
                
            return df
        except Error as e:
            logger.error(f"Error retrieving reviews: {e}")
            raise
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # TICKET OPERATIONS
    # -------------------------------------------------------------------------

    def insert_ticket(
        self,
        processed_data_id: Optional[int],
        primary_label: str,
        department: str,
        summary: str,
        description: str,
        external_key: Optional[str] = None,
        source: str = "mock",
        status: str = "OPEN",
    ) -> int:
        """Insert a new ticket."""
        query = """
        INSERT INTO tickets (
            processed_data_id, primary_label, department,
            summary, description, external_key, source, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(
                query,
                (
                    processed_data_id,
                    primary_label,
                    department,
                    summary,
                    description,
                    external_key,
                    source,
                    status,
                ),
            )
            conn.commit()
            ticket_id = cursor.lastrowid
            cursor.close()
            logger.info(f"Inserted ticket id={ticket_id}")
            return ticket_id
        except Error as e:
            logger.error(f"Error inserting ticket: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_open_tickets(self) -> pd.DataFrame:
        """Get all open tickets."""
        query = "SELECT * FROM tickets WHERE status = 'OPEN' ORDER BY created_at DESC"
        conn = self._get_connection()
        try:
            conn.database = self.database
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()

    def get_tickets_for_processed_id(self, processed_data_id: int) -> pd.DataFrame:
        """Get tickets for a specific processed_data row."""
        query = "SELECT * FROM tickets WHERE processed_data_id = %s"
        conn = self._get_connection()
        try:
            conn.database = self.database
            return pd.read_sql_query(query, conn, params=[processed_data_id])
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # USER OPERATIONS
    # -------------------------------------------------------------------------

    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str = "viewer",
        department: Optional[str] = None,
    ) -> int:
        """Create a new user."""
        query = """
        INSERT INTO user_data (username, email, password_hash, role, department)
        VALUES (%s, %s, %s, %s, %s)
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(query, (username, email, password_hash, role, department))
            conn.commit()
            user_id = cursor.lastrowid
            cursor.close()
            logger.info(f"Created user: {username} (id={user_id})")
            return user_id
        except Error as e:
            logger.error(f"Error creating user: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        query = "SELECT * FROM user_data WHERE username = %s"
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            cursor.close()
            return user
        except Error as e:
            logger.error(f"Error getting user: {e}")
            raise
        finally:
            conn.close()

    def update_last_login(self, username: str):
        """Update last login timestamp."""
        query = "UPDATE user_data SET last_login = CURRENT_TIMESTAMP WHERE username = %s"
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(query, (username,))
            conn.commit()
            cursor.close()
        except Error as e:
            logger.error(f"Error updating last login: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # STATISTICS OPERATIONS
    # -------------------------------------------------------------------------
    def _convert_decimal(self, value):
        """Decimal → int/float dönüştürücü"""
        if isinstance(value, Decimal):
            # Eğer virgülsüz bir sayı (ör: 19.0) ise int yap
            if value == value.to_integral_value():
                return int(value)
            return float(value)
        return value

    def execute(self, query, params=None, fetch=False):
        conn = self._get_connection()
        cursor = None
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(query, params)

            if fetch:
                rows = cursor.fetchall()
                # Decimal → int conversion
                cleaned = []
                for row in rows:
                    cleaned.append(tuple(self._convert_decimal(v) for v in row))
                conn.commit()
                return cleaned

            conn.commit()
            return None

        except Error as err:
            logger.error(f"Query error: {err}")
            return None

        finally:
            if cursor:
                cursor.close()
            conn.close()

    def get_department_table_name(self, department_name: str) -> str:
        return DepartmentTables[department_name].value
    
    def get_table_name(self, department_name: str) -> str:
        """Alias for get_department_table_name for convenience."""
        return self.get_department_table_name(department_name)
    
    def get_department_high_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)
        if not table:
            raise ValueError(f"Unknown department: {department_name}")

        query = f"""
            SELECT SUM(high_count)
            FROM {table}
            WHERE date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_label_high_counts(self, label, department_name, date_from, date_to):
        table = self.get_table_name(department_name)
        if not table:
            raise ValueError(f"Unknown department: {department_name}")

        query = f"""
            SELECT SUM(high_count)
            FROM {table}
            WHERE label = %s AND date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_department_low_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(low_count)
            FROM {table}
            WHERE date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_label_low_counts(self, label, department_name, date_from, date_to):
        table = self.get_table_name(department_name)
        if not table:
            raise ValueError(f"Unknown department: {department_name}")

        query = f"""
            SELECT SUM(low_count)
            FROM {table}
            WHERE label = %s AND date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_department_medium_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(medium_count)
            FROM {table}
            WHERE date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_label_medium_counts(self, label, department_name, date_from, date_to):
        table = self.get_table_name(department_name)
        if not table:
            raise ValueError(f"Unknown department: {department_name}")

        query = f"""
            SELECT SUM(medium_count)
            FROM {table}
            WHERE label = %s AND date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_department_positive_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)
        if not table:
            raise ValueError(f"Unknown department: {department_name}")

        query = f"""
            SELECT SUM(positive_count)
            FROM {table}
            WHERE date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_label_positive_counts(self, label, department_name, date_from, date_to):
        table = self.get_table_name(department_name)
        if not table:
            raise ValueError(f"Unknown department: {department_name}")

        query = f"""
            SELECT SUM(positive_count)
            FROM {table}
            WHERE label = %s AND date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_department_negative_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(negative_count)
            FROM {table}
            WHERE date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_label_negative_counts(self, label, department_name, date_from, date_to):
        table = self.get_table_name(department_name)
        if not table:
            raise ValueError(f"Unknown department: {department_name}")

        query = f"""
            SELECT SUM(negative_count)
            FROM {table}
            WHERE label = %s AND date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_department_neutral_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(neutral_count)
            FROM {table}
            WHERE date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_label_neutral_counts(self, label, department_name, date_from, date_to):
        table = self.get_table_name(department_name)
        if not table:
            raise ValueError(f"Unknown department: {department_name}")

        query = f"""
            SELECT SUM(neutral_count)
            FROM {table}
            WHERE label = %s AND date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_department_total_count(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(positive_count + negative_count + neutral_count)
            FROM {table}
            WHERE date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_label_total_count(self, department_name, label, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(positive_count + negative_count + neutral_count)
            FROM {table}
            WHERE label = %s AND date_from >= %s AND date_from < %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_unique_reviews_count(self, date_from: datetime, date_to: datetime) -> int:
        """
        Get count of unique reviews from the reviews table within a date range.
        This counts actual reviews, not processed segments.
        """
        query = """
            SELECT COUNT(DISTINCT id) 
            FROM reviews 
            WHERE date >= %s AND date <= %s
        """
        result = self.execute(query, (date_from.date(), date_to.date()), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_processed_segments_count(self, date_from: datetime, date_to: datetime) -> int:
        """
        Get count of processed segments from the processed_reviews table within a date range.
        This counts segments (one review can have multiple segments).
        """
        query = """
            SELECT COUNT(*) 
            FROM processed_reviews 
            WHERE created_at >= %s AND created_at < %s
        """
        result = self.execute(query, (date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_unique_processed_reviews_count(self, date_from: datetime, date_to: datetime) -> int:
        """
        Get count of unique reviews that have been processed (have at least one segment).
        """
        query = """
            SELECT COUNT(DISTINCT r.id) 
            FROM reviews r
            INNER JOIN processed_reviews pr ON r.id = pr.review_id
            WHERE r.date >= %s AND r.date < %s
        """
        result = self.execute(query, (date_from.date(), date_to.date()), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_recent_high_priority_reviews_for_department(self, department_code: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Returns most recent HIGH priority processed review segments
        for a given department.
        """

        try:
            labels = DepartmentToLabels[department_code].value
        except KeyError:
            raise ValueError(f"Unknown department code: {department_code}")
                
        if not labels:
            return []

        placeholders = ", ".join(["%s"] * len(labels))

        query = f"""
            SELECT
                pr.label,
                r.review,
                pr.index as highlight_index,
                r.date,
                r.flight_number,
                r.route
            FROM processed_reviews pr
            JOIN reviews r ON pr.review_id = r.id
            WHERE pr.priority = 'HIGH'
            AND pr.label IN ({placeholders})
            ORDER BY r.date DESC
            LIMIT %s
        """

        params = labels + [limit]

        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Error as e:
            logger.error(
                f"Error fetching high priority reviews for department={department_code}: {e}"
            )
            raise
        finally:
            conn.close()

    def get_manager_high_priority_overview(self, limit_per_department: int = 3) -> Dict[str, List[Dict[str, Any]]]:
        """
        Returns recent HIGH priority reviews for each department.
        Used by manager dashboard.
        """
        result: Dict[str, List[Dict[str, Any]]] = {}

        for dept_enum in DepartmentToLabels:
            department_code = dept_enum.name
            labels = dept_enum.value

            if not labels:
                continue

            try:
                rows = self.get_recent_high_priority_reviews_for_department(department_code=department_code, limit=limit_per_department)
                result[department_code] = rows
            except Exception as e:
                logger.warning(
                    f"Skipping department {department_code} due to error: {e}"
                )
                result[department_code] = []

        return result

    def update_department_statistics(self, start_dt: datetime, end_dt: datetime):
        """
        Aggregates reviews processed within a specific time range and updates department statistics.
        """
        logger.info(f"Updating department statistics for range: {start_dt} - {end_dt}")
        
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            
            for dept_enum in DepartmentTables:
                dept_name = dept_enum.name
                table_name = dept_enum.value
                
                try:
                    labels = DepartmentToLabels[dept_name].value
                except KeyError:
                    continue
                
                if not labels:
                    continue
                
                # 1. Delete existing stats for this EXACT time range to allow re-runs
                delete_query = f"""
                DELETE FROM {table_name} 
                WHERE date_from = %s AND date_to = %s
                """
                cursor.execute(delete_query, (start_dt, end_dt))

                # 2. Aggregate data based on processed_reviews.created_at
                placeholders = ', '.join(['%s'] * len(labels))
                
                agg_query = f"""
                SELECT 
                    pr.label,
                    SUM(CASE WHEN pr.sentiment = 'POSITIVE' THEN 1 ELSE 0 END) as pos,
                    SUM(CASE WHEN pr.sentiment = 'NEGATIVE' THEN 1 ELSE 0 END) as neg,
                    SUM(CASE WHEN pr.sentiment = 'NEUTRAL' THEN 1 ELSE 0 END) as neu,
                    SUM(CASE WHEN pr.priority = 'HIGH' THEN 1 ELSE 0 END) as high,
                    SUM(CASE WHEN pr.priority = 'MEDIUM' THEN 1 ELSE 0 END) as med,
                    SUM(CASE WHEN pr.priority = 'LOW' THEN 1 ELSE 0 END) as low
                FROM processed_reviews pr
                WHERE pr.created_at >= %s AND pr.created_at < %s
                  AND pr.label IN ({placeholders})
                GROUP BY pr.label
                """
                
                params = [start_dt, end_dt] + labels
                cursor.execute(agg_query, params)
                results = cursor.fetchall()
                
                # 3. Insert new stats
                if results:
                    insert_query = f"""
                    INSERT INTO {table_name} 
                    (label, date_from, date_to, positive_count, negative_count, neutral_count, high_count, medium_count, low_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    insert_data = []
                    for row in results:
                        insert_data.append((
                            row[0], start_dt, end_dt, 
                            row[1], row[2], row[3], 
                            row[4], row[5], row[6]
                        ))
                    
                    cursor.executemany(insert_query, insert_data)
                    logger.info(f"Updated {table_name}: {cursor.rowcount} rows inserted for {start_dt}-{end_dt}")
            
            conn.commit()
            cursor.close()
            
        except Error as e:
            logger.error(f"Error updating department statistics: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # STATUS HELPERS
    # -------------------------------------------------------------------------
    def increment_review_status(self, review_id: int, max_status: int = 3) -> None:
        """
        Atomically increment review_status.status for a review.
        If the row does not exist, it will be created at 0 before incrementing.
        Caps at max_status to avoid runaway increments.
        """
        query = """
        INSERT INTO review_status (review_id, status)
        VALUES (%s, 0)
        ON DUPLICATE KEY UPDATE status = LEAST(status + 1, %s)
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(query, (review_id, max_status))
            conn.commit()
            cursor.close()
        except Error as e:
            logger.error(f"Error incrementing review_status for review_id={review_id}: {e}")
            conn.rollback()
            raise
        finally:
            conn.close()


    # -------------------------------------------------------------------------
    # ANOMALY DETECTION HELPERS
    # -------------------------------------------------------------------------
    def get_anomaly_detection_data(self):
        
        query = """
                SELECT
                    r.flight_number,
                    r.bidirectional_route,
                    r.origin_iata,
                    r.destination_iata,
                    pr.label,
                    CASE pr.sentiment
                        WHEN 'POSITIVE' THEN 1.0
                        WHEN 'NEUTRAL'  THEN 0.0
                        WHEN 'NEGATIVE' THEN -1.0
                    END AS sentiment_score
                FROM reviews r
                JOIN processed_reviews pr
                    ON pr.review_id = r.id
                WHERE pr.sentiment IN ('POSITIVE', 'NEUTRAL', 'NEGATIVE');
                """

        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Error as e:
            logger.error(
                f"Error fetching anomaly detection data: {e}"
            )
            raise
        finally:
            conn.close()
    
    def get_airport_coord(self, iata_code):
        query = """
            SELECT latitude, longitude
            FROM airport_coordinates
            WHERE iata_code = %s
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, (iata_code,))
            return cursor.fetchone()
        finally:
            conn.close()


    def ingest_airport_coord(self):
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()

            data = []

            with open("scripts/airports.csv", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    iata = row[4]
                    if iata == "\\N":
                        continue

                    lat = row[6]
                    lon = row[7]

                    if not lat or not lon:
                        continue

                    data.append((iata, lat, lon))

            if data:
                cursor.executemany("""
                    INSERT IGNORE INTO airport_coordinates (iata_code, latitude, longitude)
                    VALUES (%s, %s, %s)
                """, data)

            conn.commit()

        finally:
            cursor.close()
            conn.close()


    # -------------------------------------------------------------------------
    # CLEANUP
    # -------------------------------------------------------------------------

    def close(self):
        """Close all connections in pool."""
        if self.pool:
            logger.info("Closing MySQL connection pool")
            # Connection pool doesn't have explicit close in mysql-connector-python
            # Connections are closed automatically when no longer in use


if __name__ == "__main__":
    # Test MySQL connection
    try:
        db = MySQLDbService()
        print("MySQL database initialized successfully")
        print(f"Processed data rows: {db._get_row_count('reviews')}")
        print(f"Tickets: {db._get_row_count('tickets')}")
        print(f"Users: {db._get_row_count('user_data')}")
    except Exception as e:
        print(f"Error: {e}")
