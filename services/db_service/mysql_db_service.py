import mysql.connector
from mysql.connector import Error, pooling
import pandas as pd
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import logging
import os

from models.labels import ALL_LABELS

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
        self.user = user or os.getenv("MYSQL_USER", "root")
        self.password = password or os.getenv("MYSQL_PASSWORD", "")

        self.pool = None
        self._create_connection_pool(pool_size)
        self._create_database_if_not_exists()
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
        self._create_processed_data_table()
        self._create_statistics_table()
        self._create_user_table()
        self._create_tickets_table()
        logger.info("All MySQL tables created/verified successfully")

    # -------------------------------------------------------------------------
    # TABLE CREATION
    # -------------------------------------------------------------------------

    def _create_processed_data_table(self):
        """Create processed_data table in MySQL."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS processed_data (
            id INT AUTO_INCREMENT PRIMARY KEY,
            review TEXT,
            labels VARCHAR(500),
            date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_labels (labels(255)),
            INDEX idx_date (date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            logger.info("Table 'processed_data' created/verified")
        except Error as e:
            logger.error(f"Error creating processed_data table: {e}")
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
            FOREIGN KEY (processed_data_id) REFERENCES processed_data(id) ON DELETE SET NULL
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
        # NOTE: The requested columns use datetime ranges and counts per label/priority.
        # Assumption: column names with hyphens are converted to snake_case
        # (starting_datetime, ending_datetime) because hyphens are invalid in
        # unquoted SQL identifiers and are error-prone. If you prefer different
        # names, adjust accordingly.
        create_table_query = """
        CREATE TABLE IF NOT EXISTS statistics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            label_type VARCHAR(255) NOT NULL,
            starting_datetime DATETIME NOT NULL,
            ending_datetime DATETIME NOT NULL,
            positive_count INT DEFAULT 0,
            negative_count INT DEFAULT 0,
            neutral_count INT DEFAULT 0,
            low_priority INT DEFAULT 0,
            medium_priority INT DEFAULT 0,
            high_priority INT DEFAULT 0,
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
            INSERT INTO processed_data (review, labels, date)
            VALUES (%s, %s, %s)
            """

            data = []
            for _, row in df.iterrows():
                data.append((
                    row.get("review"),
                    row.get("labels"),
                    row.get("date"),
                ))

            cursor.executemany(query, data)
            conn.commit()
            rows_inserted = cursor.rowcount
            cursor.close()
            logger.info(f"Inserted {rows_inserted} rows into processed_data")
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
        query = "SELECT * FROM processed_data WHERE 1=1"
        params = []

        if label_type:
            query += " AND labels LIKE %s"
            params.append(f"%{label_type}%")

        if date_from:
            query += " AND date >= %s"
            params.append(date_from)

        if date_to:
            query += " AND date <= %s"
            params.append(date_to)

        query += " ORDER BY created_at DESC"

        if limit:
            query += " LIMIT %s"
            params.append(limit)

        conn = self._get_connection()
        try:
            conn.database = self.database
            df = pd.read_sql_query(query, conn, params=params if params else None)
            return df
        except Error as e:
            logger.error(f"Error retrieving processed data: {e}")
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

    def get_sentiment_distribution(self) -> pd.DataFrame:
        """Get sentiment distribution (placeholder for MySQL)."""
        query = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN labels LIKE '%baggage%' THEN 1 ELSE 0 END) as negative,
            SUM(CASE WHEN labels NOT LIKE '%baggage%' THEN 1 ELSE 0 END) as neutral
        FROM processed_data
        """
        conn = self._get_connection()
        try:
            conn.database = self.database
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()

    def get_statistics_data(self, limit: int = 10) -> pd.DataFrame:
        """Get recent statistics."""
        # Order by starting_datetime (new schema) rather than old 'date' column
        query = f"SELECT * FROM statistics ORDER BY starting_datetime DESC LIMIT {limit}"
        conn = self._get_connection()
        try:
            conn.database = self.database
            return pd.read_sql_query(query, conn)
        finally:
            conn.close()

    def _get_row_count(self, table_name: str) -> int:
        """Get row count for a table."""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        conn = self._get_connection()
        try:
            conn.database = self.database
            cursor = conn.cursor()
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else 0
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
        print("✅ MySQL database initialized successfully")
        print(f"📊 Processed data rows: {db._get_row_count('processed_data')}")
        print(f"🎫 Tickets: {db._get_row_count('tickets')}")
        print(f"👥 Users: {db._get_row_count('user_data')}")
    except Exception as e:
        print(f"❌ Error: {e}")
