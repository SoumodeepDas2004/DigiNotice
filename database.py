import mysql.connector

class Database:
    def __init__(self):
        """Initialize the database connection and ensure DB & tables exist."""
        self.create_database_if_not_exists()
        self.connect_db()
        self.create_tables_if_not_exist()

    def connect_db(self):
        """Establish a new database connection."""
        try:
            self.conn = mysql.connector.connect(
                host="127.0.0.1",
                user="admin092004",
                password="@Admin2004",
                database="notice_board_db",
                auth_plugin='mysql_native_password',  # <- this is important
                autocommit=True  # ✅ Auto-commit changes
            )
            self.cursor = self.conn.cursor()
            print("✅ Database Connection Successful!")
        except mysql.connector.Error as e:
            print("❌ Database Connection Failed:", e)

    def create_database_if_not_exists(self):
        """Creates the database if it does not exist."""
        temp_conn = mysql.connector.connect(
            host="127.0.0.1",
            user="admin092004",
            password="@Admin2004",
            auth_plugin='mysql_native_password',  # <- this is important

        )
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute("CREATE DATABASE IF NOT EXISTS notice_board_db;")
        temp_conn.close()

    def create_tables_if_not_exist(self):
        """Creates required tables if they do not exist."""
        user_table_query = """
        CREATE TABLE IF NOT EXISTS users (
            unique_id INT PRIMARY KEY,
            name VARCHAR(255),
            password VARCHAR(255),
            profile_pic_path VARCHAR(255) DEFAULT 'profile_pics/default.jpg'
        );
        """
        notice_table_query = """
        CREATE TABLE IF NOT EXISTS notices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            content TEXT,
            summary TEXT,
            file_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute_query(user_table_query)
        self.execute_query(notice_table_query)

    def execute_query(self, query, values=None, multi=False):
        """Executes INSERT, UPDATE, DELETE queries safely."""
        try:
            self.cursor.execute(query, values or (), multi)
            self.conn.commit()
        except mysql.connector.Error as e:
            print("❌ Database Query Error:", e)
            self.reconnect()  # ✅ Auto-reconnect on failure

    def fetch_data(self, query, params=None):
        """Fetches data from the database."""
        try:
            self.cursor.execute(query, params or ())
            return self.cursor.fetchall()
        except mysql.connector.Error as e:
            print("❌ Database Fetch Error:", e)
            self.reconnect()
            return []

    def reconnect(self):
        """Reconnect to the database in case of lost connection."""
        print("🔄 Reconnecting to Database...")
        self.connect_db()

    def close_connection(self):
        """Closes the database connection properly."""
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("🔴 Database Connection Closed.")

# ✅ Create a global instance of the database
db = Database()
