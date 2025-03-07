import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            #pendingdata
            host="your_server_ip",
            user="your_user",
            password="your_password",
            database="your_database"
        )
        self.cursor = self.conn.cursor()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        self.conn.commit()

    def fetch_data(self, query, params=None):
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()
