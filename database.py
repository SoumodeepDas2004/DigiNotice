import mysql.connector

class Database:
    def __init__(self):
        """Initialize the database connection."""
        self.connect_db()

    def connect_db(self):
        """Establish a new database connection."""
        try:
            self.conn = mysql.connector.connect(
                host="127.0.0.1",
                user="admin092004",
                password="@Admin2004",
                database="notice_board_db",
                autocommit=True  # ✅ Auto-commit changes
            )
            self.cursor = self.conn.cursor()
            print("✅ Database Connection Successful!")
        except mysql.connector.Error as e:
            print("❌ Database Connection Failed:", e)

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
