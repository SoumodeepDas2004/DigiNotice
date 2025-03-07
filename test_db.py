from database import Database

try:
    db = Database()
    print("✅ Connected to Local MySQL via Workbench Successfully!")
except Exception as e:
    print("❌ Connection Failed:", str(e))
