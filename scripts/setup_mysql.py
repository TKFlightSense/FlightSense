"""
MySQL Database Setup Script for FlightSense

This script automates the creation of the MySQL database, user, and initial tables.
Run this script with MySQL root privileges.

Usage:
    python scripts/setup_mysql.py

Requirements:
    - MySQL server installed and running
    - mysql-connector-python installed
    - Root MySQL credentials
"""

import os
import sys
import getpass
import mysql.connector
from mysql.connector import Error

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuration
DEFAULT_DB_NAME = "flightsense"
DEFAULT_DB_USER = "flightsense"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 3306


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def get_input(prompt, default=None, password=False):
    """Get user input with optional default value"""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if password:
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value if value else default


def test_root_connection(host, port, root_password):
    """Test connection to MySQL as root"""
    try:
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user='root',
            password=root_password
        )
        if connection.is_connected():
            print("[OK] Successfully connected to MySQL server")
            return connection
    except Error as e:
        print(f"[ERROR] Error connecting to MySQL: {e}")
        return None


def create_database(connection, db_name):
    """Create the FlightSense database"""
    try:
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE %s", (db_name,))
        result = cursor.fetchone()
        
        if result:
            print(f"[WARNING] Database '{db_name}' already exists")
            overwrite = get_input("Do you want to drop and recreate it? (yes/no)", "no")
            if overwrite.lower() in ['yes', 'y']:
                cursor.execute(f"DROP DATABASE {db_name}")
                print(f"[INFO] Dropped existing database '{db_name}'")
            else:
                print("[INFO] Using existing database")
                return True
        
        # Create database
        cursor.execute(
            f"CREATE DATABASE {db_name} "
            f"CHARACTER SET utf8mb4 "
            f"COLLATE utf8mb4_unicode_ci"
        )
        print(f"[OK] Created database '{db_name}'")
        
        cursor.close()
        return True
        
    except Error as e:
        print(f"[ERROR] Error creating database: {e}")
        return False


def create_user(connection, db_name, db_user, db_password):
    """Create the FlightSense MySQL user"""
    try:
        cursor = connection.cursor()
        
        # Check if user exists
        cursor.execute(
            "SELECT user, host FROM mysql.user WHERE user = %s AND host = 'localhost'",
            (db_user,)
        )
        result = cursor.fetchone()
        
        if result:
            print(f"[WARNING] User '{db_user}'@'localhost' already exists")
            recreate = get_input("Do you want to drop and recreate the user? (yes/no)", "no")
            if recreate.lower() in ['yes', 'y']:
                cursor.execute(f"DROP USER '{db_user}'@'localhost'")
                print(f"[INFO] Dropped existing user '{db_user}'@'localhost'")
            else:
                print("[INFO] Using existing user")
                # Update password
                cursor.execute(
                    f"ALTER USER '{db_user}'@'localhost' IDENTIFIED BY %s",
                    (db_password,)
                )
                print(f"[INFO] Updated password for '{db_user}'@'localhost'")
        
        if not result or recreate.lower() in ['yes', 'y']:
            # Create user
            cursor.execute(
                f"CREATE USER '{db_user}'@'localhost' IDENTIFIED BY %s",
                (db_password,)
            )
            print(f"[OK] Created user '{db_user}'@'localhost'")
        
        # Grant privileges
        cursor.execute(
            f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'localhost'"
        )
        cursor.execute("FLUSH PRIVILEGES")
        print(f"[OK] Granted all privileges on '{db_name}' to '{db_user}'@'localhost'")
        
        cursor.close()
        return True
        
    except Error as e:
        print(f"[ERROR] Error creating user: {e}")
        return False


def create_tables(host, port, db_name, db_user, db_password):
    """Create all FlightSense tables"""
    try:
        # Connect as the new user
        connection = mysql.connector.connect(
            host=host,
            port=port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        if not connection.is_connected():
            print("[ERROR] Failed to connect as new user")
            return False
        
        print(f"[OK] Connected to database '{db_name}' as '{db_user}'")
        
        cursor = connection.cursor()
        
        # Create reviews table (formerly processed_data)
        cursor.execute("""
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
        """)
        print("[OK] Created table 'reviews'")

        # Create processed_reviews table (segments)
        cursor.execute("""
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
        """)
        print("[OK] Created table 'processed_reviews'")
        
        # Create tickets table
        cursor.execute("""
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
        """)
        print("[OK] Created table 'tickets'")
        
        # Create statistics table
        cursor.execute("""
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
        """)
        print("[OK] Created table 'statistics'")
        
        # Create user_data table
        cursor.execute("""
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
        """)
        print("[OK] Created table 'user_data'")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Error as e:
        print(f"[ERROR] Error creating tables: {e}")
        return False


def update_env_file(host, port, db_name, db_user, db_password):
    """Update or create .env file with MySQL configuration"""
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    env_example_path = os.path.join(os.path.dirname(__file__), '..', '.env.example')
    
    # Read existing .env or create from .env.example
    if os.path.exists(env_path):
        print(f"[INFO] Found existing .env file at {env_path}")
        with open(env_path, 'r') as f:
            env_content = f.read()
    elif os.path.exists(env_example_path):
        print(f"[INFO] Creating .env from .env.example")
        with open(env_example_path, 'r') as f:
            env_content = f.read()
    else:
        print("[WARNING] No .env or .env.example found, creating minimal .env")
        env_content = ""
    
    # Update MySQL configuration
    mysql_config = f"""
# MySQL Database Configuration (Generated by setup_mysql.py)
USE_MYSQL=true
MYSQL_HOST={host}
MYSQL_PORT={port}
MYSQL_DATABASE={db_name}
MYSQL_USER={db_user}
MYSQL_PASSWORD={db_password}
"""
    
    # Remove old MySQL configuration if present
    lines = env_content.split('\n')
    new_lines = []
    skip_mysql = False
    
    for line in lines:
        if line.strip().startswith('# MySQL Database Configuration'):
            skip_mysql = True
            continue
        if skip_mysql and line.strip().startswith('MYSQL_'):
            continue
        if skip_mysql and (line.strip() == '' or line.strip().startswith('#') and 'MySQL' not in line):
            skip_mysql = False
        if not skip_mysql:
            new_lines.append(line)
    
    # Append new MySQL configuration
    env_content = '\n'.join(new_lines).strip() + '\n' + mysql_config
    
    # Write back to .env
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print(f"[OK] Updated .env file with MySQL configuration")
    print(f"   File location: {os.path.abspath(env_path)}")


def main():
    """Main setup function"""
    print_section("FlightSense MySQL Setup")
    print("\nThis script will:")
    print("  1. Create MySQL database")
    print("  2. Create MySQL user with appropriate privileges")
    print("  3. Create all required tables")
    print("  4. Update .env file with configuration")
    print("\n[WARNING] You will need MySQL root credentials to proceed.\n")
    
    # Get MySQL root credentials
    print_section("Step 1: MySQL Root Connection")
    host = get_input("MySQL host", DEFAULT_HOST)
    port = int(get_input("MySQL port", str(DEFAULT_PORT)))
    root_password = get_input("MySQL root password", password=True)
    
    # Test connection
    connection = test_root_connection(host, port, root_password)
    if not connection:
        print("\n[ERROR] Setup failed: Could not connect to MySQL")
        return False
    
    # Get database configuration
    print_section("Step 2: Database Configuration")
    db_name = get_input("Database name", DEFAULT_DB_NAME)
    db_user = get_input("Database user", DEFAULT_DB_USER)
    db_password = get_input("Database password (min 8 chars)", password=True)
    
    if len(db_password) < 8:
        print("[ERROR] Password must be at least 8 characters")
        return False
    
    # Create database
    print_section("Step 3: Creating Database")
    if not create_database(connection, db_name):
        connection.close()
        return False
    
    # Create user
    print_section("Step 4: Creating User")
    if not create_user(connection, db_name, db_user, db_password):
        connection.close()
        return False
    
    connection.close()
    
    # Create tables
    print_section("Step 5: Creating Tables")
    if not create_tables(host, port, db_name, db_user, db_password):
        return False
    
    # Update .env file
    print_section("Step 6: Updating Environment File")
    update_env_file(host, port, db_name, db_user, db_password)
    
    # Success summary
    print_section("Setup Complete!")
    print(f"""
Database Configuration:
  Host:     {host}
  Port:     {port}
  Database: {db_name}
  User:     {db_user}

Tables Created:
  [OK] processed_data  (feedback storage)
  [OK] tickets         (Jira ticket tracking)
  [OK] statistics      (analytics data)
  [OK] user_data       (authentication)

Next Steps:
  1. Review .env file and configure other settings (LLM, Jira, JWT)
  2. Install Python dependencies: pip install -r requirements.txt
  3. Start the application: python app.py
  4. Test health endpoint: curl http://localhost:8000/health

For more information, see docs/DEPLOYMENT.md
""")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[WARNING] Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
