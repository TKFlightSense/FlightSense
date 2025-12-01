import mysql.connector
from mysql.connector import Error
from decimal import Decimal

"""
# Bağlantı parametreleri
config = {
    'host': 'localhost',      # Docker port yönlendirmesi sayesinde localhost
    'user': 'root',           # Kullanıcı adı
    'password': 'sevgi523253', # Şifreniz (Docker run komutunda belirlediğiniz)
    # 'database': 'my_app_db' # Şimdilik veritabanı adı belirtmiyoruz, ilk önce oluşturacağız.
}

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        # Bağlantı oluşturuluyor
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Veritabanı bağlantısı başarılı!")
        return connection
    except Error as err:
        print(f"Hata: '{err}'")
        return connection

# Bağlantıyı kurma
connection = create_server_connection(config['host'], config['user'], config['password'])


def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Veritabanı başarıyla oluşturuldu/kullanılıyor.")
    except Error as err:
        # Hata kodu 1007 genellikle veritabanının zaten var olduğu anlamına gelir.
        if err.errno == 1007:
            print("Veritabanı zaten mevcut, kullanmaya devam ediliyor.")
        else:
            print(f"Veritabanı oluşturma/kullanma hatası: '{err}'")

# Veritabanı oluşturma sorgusu
create_db_query = "CREATE DATABASE my_app_db"
create_database(connection, create_db_query)

# Artık tüm işlemleri bu veritabanı içinde yapmak için bağlantıyı güncelleyebiliriz
connection.database = 'my_app_db'

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit() # Değişiklikleri kalıcı hale getirir (CREATE, INSERT, UPDATE, DELETE için gereklidir)
        print("Sorgu başarıyla çalıştırıldı.")
    except Error as err:
        print(f"Sorgu çalıştırma hatası: '{err}'")

def create_table_with_indexes(connection):
    create_table_query = """"""
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
        
        -- İndeks Tanımları (Table Level)
        INDEX idx_label (label),
        INDEX idx_analysis_range (label, date_from, date_to)
    );
    """"""
    
    cursor = connection.cursor()
    try:
        cursor.execute(create_table_query)
        connection.commit()
        print("Tablo 'kabin_hizmetleri' (indekslerle birlikte) başarıyla oluşturuldu.")
    except Error as err:
        print(f"Tablo oluşturma hatası: '{err}'")

create_table_with_indexes(connection)

def create_table_with_indexes(connection):
    create_table_query = """"""
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
        
        -- İndeks Tanımları (Table Level)
        INDEX idx_label (label),
        INDEX idx_analysis_range (label, date_from, date_to)
    );
    """"""
    
    cursor = connection.cursor()
    try:
        cursor.execute(create_table_query)
        connection.commit()
        print("Tablo 'ikram_ucak_ici' (indekslerle birlikte) başarıyla oluşturuldu.")
    except Error as err:
        print(f"Tablo oluşturma hatası: '{err}'")

create_table_with_indexes(connection)

def create_table_with_indexes(connection):
    create_table_query = """"""
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
        
        -- İndeks Tanımları (Table Level)
        INDEX idx_label (label),
        INDEX idx_analysis_range (label, date_from, date_to)
    );
    """"""
    
    cursor = connection.cursor()
    try:
        cursor.execute(create_table_query)
        connection.commit()
        print("Tablo 'yer_isletme_bagaj' (indekslerle birlikte) başarıyla oluşturuldu.")
    except Error as err:
        print(f"Tablo oluşturma hatası: '{err}'")

create_table_with_indexes(connection)

def create_table_with_indexes(connection):
    create_table_query = """""""
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
        
        -- İndeks Tanımları (Table Level)
        INDEX idx_label (label),
        INDEX idx_analysis_range (label, date_from, date_to)
    );
    """""""
    
    cursor = connection.cursor()
    try:
        cursor.execute(create_table_query)
        connection.commit()
        print("Tablo 'tgs' (indekslerle birlikte) başarıyla oluşturuldu.")
    except Error as err:
        print(f"Tablo oluşturma hatası: '{err}'")

create_table_with_indexes(connection)
"""

# db.py
import mysql.connector
from mysql.connector import Error

DEPARTMENT_TABLES = {
    "KABIN": "kabin_hizmetleri",
    "IUIUB": "ikram_ucak_ici",
    "BMCOGM": "yer_isletme_bagaj",
    "TGS": "tgs"
}

class Database:
    def __init__(self, host="localhost", user="root", password="", database="my_app_db"):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "auth_plugin": "mysql_native_password",
        }
        self.connection = None

    def connect(self):
        """Yeni bağlantı kurar."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            print("MySQL bağlantısı başarılı.")
        except Error as err:
            print(f"Bağlantı hatası: {err}")
            self.connection = None
        return self.connection
    
    def _convert_decimal(self, value):
        """Decimal → int/float dönüştürücü"""
        if isinstance(value, Decimal):
            # Eğer virgülsüz bir sayı (ör: 19.0) ise int yap
            if value == value.to_integral_value():
                return int(value)
            return float(value)
        return value

    def execute(self, query, params=None, fetch=False):
        if self.connection is None:
            self.connect()

        cursor = self.connection.cursor()

        try:
            cursor.execute(query, params)

            if fetch:
                rows = cursor.fetchall()
                # Decimal → int dönüşümü uygulayalım
                cleaned = []
                for row in rows:
                    cleaned.append(tuple(self._convert_decimal(v) for v in row))
                self.connection.commit()
                return cleaned

            self.connection.commit()
            return None

        except Error as err:
            print(f"Sorgu hatası: {err}")
            return None

        finally:
            cursor.close()


    def get_table_name(self, department_name: str) -> str:
        return DEPARTMENT_TABLES.get(department_name)
    
    def get_department_high_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)
        if not table:
            raise ValueError(f"Unknown department: {department_name}")

        query = f"""
            SELECT SUM(high_count)
            FROM {table}
            WHERE date_from >= %s AND date_to <= %s
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
            WHERE label = %s AND date_from >= %s AND date_to <= %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_department_low_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(low_count)
            FROM {table}
            WHERE date_from >= %s AND date_to <= %s
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
            WHERE label = %s AND date_from >= %s AND date_to <= %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_department_medium_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(medium_count)
            FROM {table}
            WHERE date_from >= %s AND date_to <= %s
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
            WHERE label = %s AND date_from >= %s AND date_to <= %s
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
            WHERE date_from >= %s AND date_to <= %s
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
            WHERE label = %s AND date_from >= %s AND date_to <= %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_department_negative_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(negative_count)
            FROM {table}
            WHERE date_from >= %s AND date_to <= %s
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
            WHERE label = %s AND date_from >= %s AND date_to <= %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_department_neutral_counts(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(neutral_count)
            FROM {table}
            WHERE date_from >= %s AND date_to <= %s
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
            WHERE label = %s AND date_from >= %s AND date_to <= %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0
    
    def get_department_total_count(self, department_name, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(positive_count + negative_count + neutral_count)
            FROM {table}
            WHERE date_from >= %s AND date_to <= %s
        """

        result = self.execute(query, (date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def get_label_total_count(self, department_name, label, date_from, date_to):
        table = self.get_table_name(department_name)

        query = f"""
            SELECT SUM(positive_count + negative_count + neutral_count)
            FROM {table}
            WHERE label = %s AND date_from >= %s AND date_to <= %s
        """

        result = self.execute(query, (label, date_from, date_to), fetch=True)
        return result[0][0] if result and result[0][0] is not None else 0

    def close(self):
        if self.connection:
            self.connection.close()
            print("MySQL bağlantısı kapatıldı.")

