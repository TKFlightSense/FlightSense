import mysql.connector
from mysql.connector import Error, pooling
import pandas as pd
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import logging
import os
from decimal import Decimal

from models.labels import ALL_LABELS
from models.enums.enums import DepartmentTables, DepartmentToLabels
from datetime import date, datetime, time

# Set up logging
logging.basicConfig(level=logging.INFO)
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
        self._create_review_details_table()
        self._create_statistics_table()
        self._create_user_table()
        self._create_tickets_table()
        self._create_cagri_merkezi_table()
        self._create_ikram_ucak_ici_table()
        self._create_kabin_hizmetleri_table()
        self._create_rez_biletleme_table()
        self._create_tgs_table()
        self._create_yer_isletme_bagaj_table()
        self._create_gelir_yonetimi_table()
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
            INDEX idx_date (date),
            INDEX idx_flight_number (flight_number),
            INDEX idx_pnr (pnr)
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

    def _create_statistics_table(self):
        """Create statistics table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS statistics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            label_type VARCHAR(255) NOT NULL,
            starting_datetime DATETIME NOT NULL,
            ending_datetime DATETIME NOT NULL,
            positive_count INT DEFAULT 0,
            negative_count INT DEFAULT 0,
            neutral_count INT DEFAULT 0,
            `low_priority` INT DEFAULT 0,
            `medium_priority` INT DEFAULT 0,
            `high_priority` INT DEFAULT 0,
            INDEX idx_label_type (label_type),
            INDEX idx_starting_datetime (starting_datetime),
            INDEX idx_ending_datetime (ending_datetime)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'statistics' created/verified")
        except Error as e:
            logger.error(f"Error creating statistics table: {e}")
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

    # -------------------------------------------------------------------------
    # PROCESSED DATA OPERATIONS
    # -------------------------------------------------------------------------

    def push_processed_data(self, df: pd.DataFrame) -> int:
        """Push DataFrame to processed_data table."""
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()

            query = """
            INSERT INTO reviews (review, date, flight_number, pnr)
            VALUES (%s, %s, %s, %s)
            """

            data = []
            for _, row in df.iterrows():
                data.append((
                    row.get("review"),
                    row.get("date"),
                    row.get("flight_number"),
                    row.get("pnr"),
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
