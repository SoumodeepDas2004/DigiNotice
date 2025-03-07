from database import Database

db = Database()

def upload_notice(title, content):
    query = "INSERT INTO notices (title, content) VALUES (%s, %s)"
    db.execute_query(query, (title, content))

def get_notices():
    query = "SELECT title, content FROM notices ORDER BY id DESC"
    return db.fetch_data(query)