from database import Database
import os
import mimetypes

db = Database()

# 🔹 Add Notice
def add_notice(title, content, summary, file_path):
    query = "INSERT INTO notices (title, content, summary, file_path) VALUES (%s, %s, %s, %s)"
    db.execute_query(query, (title, content, summary, file_path))

# 🔹 Get Latest Notices (for Notice Board)
def get_latest_notices(limit=3):
    print("🔍 Fetching notices from database...")
    query = "SELECT title, content, file_path, summary, created_at FROM notices ORDER BY created_at DESC LIMIT %s"
    notices = db.fetch_data(query, (limit,))

    print(f"✅ Notices Fetched: {notices}")  # <-- Debugging
    processed_notices = []

    for title, content, file_path, summary, notice_time in notices:
        print(f"📜 Processing: {title}, {file_path}")  # <-- Debugging

        if content == "Content extracted from file" and file_path:
            if os.path.exists(file_path):
                file_type, _ = mimetypes.guess_type(file_path)

                if file_type and file_type.startswith("text"):  # Read only text files
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            content = file.read()
                    except UnicodeDecodeError:
                        content = "❌ Error: File encoding not supported (Not UTF-8)."
                    except Exception as e:
                        content = f"❌ Error reading file: {e}"
                else:
                    content = " ".join(summary.split()[:15]) + "..."  # ✅ Show first 15 words of summary
            else:
                content = "❌ File not found"

        processed_notices.append((title, content, file_path, notice_time))

    print(f"✅ Processed Notices: {processed_notices}")  # <-- Debugging
    return processed_notices

# 🔹 Get Summarized Notices (for Rotating Summaries)
def get_summarized_notices(limit=5):
    query = "SELECT COALESCE(summary, 'No summary available') FROM notices ORDER BY created_at DESC LIMIT %s"
    results = db.fetch_data(query, (limit,))
    return [row[0] for row in results]  # Extract summaries from results

# 🔹 Get All Notices (for Admin Panel)
def get_all_notices():
    query = "SELECT id, title, summary, created_at, file_path FROM notices ORDER BY created_at DESC"
    return db.fetch_data(query)

# 🔹 Delete Notice by ID
def delete_notice(notice_id):
    """Deletes a notice and resets IDs properly."""
    try:
        delete_query = "DELETE FROM notices WHERE id = %s;"
        db.execute_query(delete_query, (notice_id,))  # ✅ No need for multi=True

        print(f"✅ Notice with ID {notice_id} deleted successfully!")
        refreshid()  # ✅ Reset ID after deletion

    except Exception as err:
        print(f"❌ Error deleting notice: {err}")

# 🔹 Reset Notice IDs After Deletion
def refreshid():
    """Resets the notice IDs properly after deletion."""
    reset_queries = [
        "CREATE TABLE temp_notices AS SELECT title, content, summary, file_path, created_at FROM notices ORDER BY id;",
        "DROP TABLE notices;",
        """CREATE TABLE notices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            content TEXT,
            summary TEXT,
            file_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        "INSERT INTO notices (title, content, summary, file_path, created_at) SELECT title, content, summary, file_path, created_at FROM temp_notices;",
        "DROP TABLE temp_notices;"
    ]

    for query in reset_queries:
        try:
            db.execute_query(query)
        except Exception as e:
            print(f"❌ Error in ID Reset: {e}")
