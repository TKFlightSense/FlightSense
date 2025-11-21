import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional, List, Tuple
import logging

from models.labels import ALL_LABELS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DbService:
    def __init__(self, db_path: str = "../../data/processed/FlightSense.db"):
        """
        Initialize database connection and create tables if they don't exist.

        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_directory_exists()
        self.connection = None
        self.cursor = None
        self._connect_to_db()
        self._create_tables()
        self._check_if_first_run()
        self._initialize_default_data()

    # -------------------------------------------------------------------------
    # INIT HELPERS
    # -------------------------------------------------------------------------

    def _check_if_first_run(self) -> bool:
        """Check if database is being initialized for the first time."""
        count = self._get_row_count("processed_data")
        return count == 0

    def _initialize_default_data(self):
        """Ingest default CSV on first run."""
        if self._check_if_first_run():
            default_csv_path = "../../data/raw/labeled_data.csv"
            if Path(default_csv_path).exists():
                logger.info("First run detected. Ingesting default data...")
                self._ingest_preprocessed_csv(default_csv_path, "processed_data")
            else:
                logger.warning(f"Default CSV not found: {default_csv_path}")

    def _ensure_directory_exists(self):
        """Create the directory for the database if it doesn't exist."""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Database directory ensured: {db_dir}")

    def _connect_to_db(self):
        """Establish connection to SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def _create_tables(self):
        """Create all necessary tables if they don't exist."""
        self._create_processed_data_table()
        self._create_statistics_table()
        self._create_user_table()
        self._create_tickets_table()  # Jira Ticket Table
        logger.info("All tables created/verified successfully")

    # -------------------------------------------------------------------------
    # TICKETS TABLE (Jira clone)
    # -------------------------------------------------------------------------

    def _create_tickets_table(self):
        """
        Table to store 'Jira-like' tickets.
        This is your Jira clone — you can later sync real Jira keys here.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            processed_data_id INTEGER,           -- FK to processed_data.id (optional)
            primary_label TEXT,                  -- main label used for routing
            department TEXT,                     -- e.g. 'GroundOps', 'Catering'
            summary TEXT NOT NULL,
            description TEXT NOT NULL,
            external_key TEXT,                   -- real Jira key when you integrate
            source TEXT DEFAULT 'mock',          -- 'mock' or 'jira'
            status TEXT DEFAULT 'OPEN',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        logger.info("Table 'tickets' created/verified")

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
        query = """
        INSERT INTO tickets (
            processed_data_id, primary_label, department,
            summary, description, external_key, source, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(
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
        self.connection.commit()
        ticket_id = self.cursor.lastrowid
        logger.info(
            f"Inserted ticket id={ticket_id} for processed_data_id={processed_data_id}"
        )
        return ticket_id

    def get_tickets_for_processed_id(self, processed_data_id: int) -> pd.DataFrame:
        query = "SELECT * FROM tickets WHERE processed_data_id = ?"
        return pd.read_sql_query(query, self.connection, params=[processed_data_id])

    def get_open_tickets(self, limit: Optional[int] = None) -> pd.DataFrame:
        query = "SELECT * FROM tickets WHERE status = 'OPEN' ORDER BY created_at DESC"
        if limit:
            query += f" LIMIT {limit}"
        return pd.read_sql_query(query, self.connection)

    # -------------------------------------------------------------------------
    # PROCESSED DATA TABLE
    # -------------------------------------------------------------------------

    def _create_processed_data_table(self):
        """
        Create table for labeled/processed flight data.

        Columns:
          - review: raw customer feedback text
          - labels: comma-separated fine-grained labels
                    e.g. 'baggage_lost,inflight_experience_food_beverage'
          - date: date of the feedback
          - created_at: timestamp when record was created
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS processed_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT,
            labels TEXT,
            date DATE, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("Table 'processed_data' created/verified")
        except sqlite3.Error as e:
            logger.error(f"Error creating processed_data table: {e}")
            raise

    # -------------------------------------------------------------------------
    # STATISTICS TABLE
    # -------------------------------------------------------------------------

    def _create_statistics_table(self):
        """
        Daily statistics table - simplified version.
        Each row represents one day for one category.
        Subcategory counts are stored as a concatenated string.
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            category TEXT NOT NULL,
            positive INTEGER DEFAULT 0,
            negative INTEGER DEFAULT 0,

            -- Subcategory breakdown as concatenated string
            -- Format: "subcategory1count1;subcategory2count2;subcategory3count3"
            -- Example: "food_beverage25;seat_comfort18;entertainment10"
            subcategory_counts TEXT,

            -- Constraints
            UNIQUE(date, category)
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()
        logger.info("Table 'statistics' created/verified")

    # -------------------------------------------------------------------------
    # USER TABLE
    # -------------------------------------------------------------------------

    def _create_user_table(self):
        """Create table for user data with authentication."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            department TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
        """
        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            logger.info("Table 'user_data' created/verified")
        except sqlite3.Error as e:
            logger.error(f"Error creating user_data table: {e}")
            raise

    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        role: str = "viewer",
        department: Optional[str] = None,
    ) -> int:
        """Create a new user."""
        try:
            query = """
            INSERT INTO user_data (username, email, password_hash, role, department)
            VALUES (?, ?, ?, ?, ?)
            """
            self.cursor.execute(
                query, (username, email, password_hash, role, department)
            )
            self.connection.commit()
            user_id = self.cursor.lastrowid
            logger.info(f"Created user: {username} with ID: {user_id}")
            return user_id
        except sqlite3.IntegrityError as e:
            logger.error(f"User already exists: {e}")
            raise ValueError("Username or email already exists")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            self.connection.rollback()
            raise

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username including password hash."""
        try:
            query = "SELECT * FROM user_data WHERE username = ? AND is_active = 1"
            result = self.cursor.execute(query, (username,)).fetchone()
            if result:
                columns = [desc[0] for desc in self.cursor.description]
                return dict(zip(columns, result))
            return None
        except Exception as e:
            logger.error(f"Error retrieving user: {e}")
            raise

    def update_last_login(self, username: str) -> None:
        """Update user's last login timestamp."""
        try:
            query = """
            UPDATE user_data 
            SET last_login = CURRENT_TIMESTAMP 
            WHERE username = ?
            """
            self.cursor.execute(query, (username,))
            self.connection.commit()
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            raise

    # -------------------------------------------------------------------------
    # CSV INGEST / PUSH
    # -------------------------------------------------------------------------

    def _ingest_preprocessed_csv(
        self,
        path: str = "data/raw/labeled_data.csv",
        table_name: str = "processed_data",
    ) -> None:
        """
        Ingest CSV file into the specified table.

        Args:
            path: Path to the CSV file
            table_name: Target table name (default: 'processed_data')
        """
        try:
            if not Path(path).exists():
                raise FileNotFoundError(f"CSV file not found: {path}")

            # Read CSV
            df = pd.read_csv(path)
            logger.info(f"Loaded CSV with {len(df)} rows from {path}")

            # Insert into database
            df.to_sql(table_name, self.connection, if_exists="append", index=False)
            self.connection.commit()
            logger.info(
                f"Successfully ingested {len(df)} rows into '{table_name}' table"
            )

        except FileNotFoundError as e:
            logger.error(str(e))
            raise
        except pd.errors.EmptyDataError:
            logger.error(f"CSV file is empty: {path}")
            raise
        except Exception as e:
            logger.error(f"Error ingesting CSV: {e}")
            self.connection.rollback()
            raise

    def push_processed_data(self, df: pd.DataFrame) -> int:
        """
        Push a DataFrame to the processed_data table.

        Args:
            df: DataFrame containing processed data

        Returns:
            Number of rows inserted
        """
        try:
            initial_count = self._get_row_count("processed_data")
            df.to_sql(
                "processed_data", self.connection, if_exists="append", index=False
            )
            self.connection.commit()
            final_count = self._get_row_count("processed_data")
            rows_inserted = final_count - initial_count
            logger.info(f"Pushed {rows_inserted} rows to processed_data table")
            return rows_inserted
        except Exception as e:
            logger.error(f"Error pushing processed data: {e}")
            self.connection.rollback()
            raise

    def push_statistics_data(self, df: pd.DataFrame) -> int:
        """
        Push a DataFrame to the statistics table.

        Args:
            df: DataFrame containing statistics data

        Returns:
            Number of rows inserted
        """
        try:
            initial_count = self._get_row_count("statistics")
            df.to_sql("statistics", self.connection, if_exists="append", index=False)
            self.connection.commit()
            final_count = self._get_row_count("statistics")
            rows_inserted = final_count - initial_count
            logger.info(f"Pushed {rows_inserted} rows to statistics table")
            return rows_inserted
        except Exception as e:
            logger.error(f"Error pushing statistics data: {e}")
            self.connection.rollback()
            raise

    # -------------------------------------------------------------------------
    # QUERY HELPERS – STRING-BASED API
    # -------------------------------------------------------------------------

    def get_processed_data(
        self,
        limit: Optional[int] = None,
        label_type: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Retrieve processed data from the database.

        Args:
            limit: Maximum number of rows to return
            label_type:
                If provided, we treat it as a fine-grained label and filter
                'labels' text column with LIKE '%label_type%'.
            date_from: Filter by start date (YYYY-MM-DD)
            date_to: Filter by end date (YYYY-MM-DD)

        Returns:
            DataFrame containing the requested data
        """
        try:
            query = "SELECT * FROM processed_data WHERE 1=1"
            params: List = []

            if label_type:
                query += " AND labels LIKE ?"
                params.append(f"%{label_type}%")

            if date_from:
                query += " AND date >= ?"
                params.append(date_from)

            if date_to:
                query += " AND date <= ?"
                params.append(date_to)

            if limit:
                query += f" LIMIT {limit}"

            df = pd.read_sql_query(query, self.connection, params=params)
            logger.info(f"Retrieved {len(df)} rows from processed_data table")
            return df
        except Exception as e:
            logger.error(f"Error retrieving processed data: {e}")
            raise

    def get_statistics_data(
        self,
        category: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Retrieve statistics data from the statistics table.

        Args:
            category: Filter by category (e.g. 'inflight_experience')
            date_from: Filter by start date (YYYY-MM-DD)
            date_to: Filter by end date (YYYY-MM-DD)
            limit: Maximum number of rows to return

        Returns:
            DataFrame containing the requested statistics
        """
        try:
            query = "SELECT * FROM statistics WHERE 1=1"
            params: List = []

            if category:
                query += " AND category = ?"
                params.append(category)

            if date_from:
                query += " AND date >= ?"
                params.append(date_from)

            if date_to:
                query += " AND date <= ?"
                params.append(date_to)

            query += " ORDER BY date DESC"

            if limit:
                query += f" LIMIT {limit}"

            df = pd.read_sql_query(query, self.connection, params=params)
            logger.info(f"Retrieved {len(df)} rows from statistics table")
            return df
        except Exception as e:
            logger.error(f"Error retrieving statistics data: {e}")
            raise

    def get_label_distribution(self) -> pd.DataFrame:
        """
        Compute distribution of fine-grained labels based on the 'labels' text column.

        Returns a DataFrame with columns:
          - label
          - count
          - total_reviews  (same for all rows)
        """
        try:
            # total number of reviews
            total_query = "SELECT COUNT(*) as total_reviews FROM processed_data"
            total_df = pd.read_sql_query(total_query, self.connection)
            total_reviews = int(total_df["total_reviews"].iloc[0]) if not total_df.empty else 0

            rows = []
            for label in ALL_LABELS:
                query = "SELECT COUNT(*) as cnt FROM processed_data WHERE labels LIKE ?"
                df = pd.read_sql_query(query, self.connection, params=[f"%{label}%"])
                cnt = int(df["cnt"].iloc[0]) if not df.empty else 0
                rows.append(
                    {
                        "label": label,
                        "count": cnt,
                        "total_reviews": total_reviews,
                    }
                )

            return pd.DataFrame(rows)
        except Exception as e:
            logger.error(f"Error getting label distribution: {e}")
            raise

    # -------------------------------------------------------------------------
    # USER DATA HELPER
    # -------------------------------------------------------------------------

    def get_user_data(self, username: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieve user data from the database.

        Args:
            username: Filter by username

        Returns:
            DataFrame containing user data
        """
        try:
            if username:
                query = "SELECT * FROM user_data WHERE username = ?"
                df = pd.read_sql_query(query, self.connection, params=[username])
            else:
                query = "SELECT * FROM user_data"
                df = pd.read_sql_query(query, self.connection)

            logger.info(f"Retrieved {len(df)} rows from user_data table")
            return df
        except Exception as e:
            logger.error(f"Error retrieving user data: {e}")
            raise

    # -------------------------------------------------------------------------
    # GENERIC HELPERS
    # -------------------------------------------------------------------------

    def _get_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table."""
        query = f"SELECT COUNT(*) FROM {table_name}"
        result = self.cursor.execute(query).fetchone()
        return result[0]

    def execute_query(self, query: str, params: Optional[Tuple] = None) -> List:
        """
        Execute a custom SQL query.

        Args:
            query: SQL query string
            params: Query parameters (optional)

        Returns:
            Query results
        """
        try:
            if params:
                result = self.cursor.execute(query, params).fetchall()
            else:
                result = self.cursor.execute(query).fetchall()
            self.connection.commit()
            return result
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            self.connection.rollback()
            raise

    def clear_table(self, table_name: str) -> None:
        """
        Clear all data from a table (use with caution!).

        Args:
            table_name: Name of the table to clear
        """
        try:
            confirm = input(
                f"Are you sure you want to clear table '{table_name}'? (yes/no): "
            )
            if confirm.lower() in ("yes", "y"):
                self.cursor.execute(f"DELETE FROM {table_name}")
                self.connection.commit()
                logger.info(f"Table '{table_name}' cleared successfully")
            else:
                logger.info("Operation cancelled")
        except Exception as e:
            logger.error(f"Error clearing table: {e}")
            self.connection.rollback()
            raise

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        """
        Get schema information for a table.

        Args:
            table_name: Name of the table

        Returns:
            DataFrame containing table schema
        """
        try:
            query = f"PRAGMA table_info({table_name})"
            df = pd.read_sql_query(query, self.connection)
            return df
        except Exception as e:
            logger.error(f"Error getting table info: {e}")
            raise

    # -------------------------------------------------------------------------
    # CONTEXT MANAGER
    # -------------------------------------------------------------------------

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = DbService()

    print("\nProcessed Data Table Schema:")
    print(db.get_table_info("processed_data"))

    df = db.get_processed_data(limit=10)
    print(df.to_string())

    print("\nLabel distribution:")
    print(db.get_label_distribution().to_string())

    db.close()