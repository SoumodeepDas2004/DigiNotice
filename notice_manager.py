from database import Database

db = Database()

def upload_notice(title, content):
    query = "INSERT INTO notices (title, content) VALUES (%s, %s)"
    db.execute_query(query, (title, content))

def get_latest_notices():
    query = "SELECT title, content FROM notices ORDER BY id DESC"
    return db.fetch_data(query)

from database import Database

db = Database()

# 🔹 Add Notice
def add_notice(title, content, summary):
    query = "INSERT INTO notices (title, content, summary) VALUES (%s, %s, %s)"
    db.execute_query(query, (title, content, summary))

# 🔹 Get Latest Notices (for Notice Board)
def get_latest_notices(limit=3):
    query = "SELECT title, content FROM notices ORDER BY created_at DESC LIMIT %s"
    return db.fetch_data(query, (limit,))

# 🔹 Get Summarized Notices (for Rotating Summaries)
def get_summarized_notices(limit=5):
    query = "SELECT summary FROM notices ORDER BY created_at DESC LIMIT %s"
    results = db.fetch_data(query, (limit,))
    return [row[0] for row in results]  # Extract summaries from results

# 🔹 Get All Notices (for Admin Panel)
def get_all_notices():
    query = "SELECT id, title, content FROM notices ORDER BY created_at DESC"
    return db.fetch_data(query)

# 🔹 Delete Notice by ID
def delete_notice(notice_id):
    query = "DELETE FROM notices WHERE id = %s"
    db.execute_query(query, (notice_id,))