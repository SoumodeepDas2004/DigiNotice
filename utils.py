from database import Database
import hashlib
import re


#add helping function from pages with gui
db = Database()

""" from auth.py"""
def is_valid_password(password):
    return bool(re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()-_])[A-Za-z\d!@#$%^&*()-_]{6,}$", password))

# 🔹 Register User
def register_user(unique_id, name, password):
    """Check if the unique_id already exists before inserting and validate password."""
    
    # ❌ Check if password follows the required pattern
    if not is_valid_password(password):
        return "❌ Password must have at least 6 characters, including a letter, a number, and a special character!"
    
    # ✅ Check if the unique_id already exists
    check_query = "SELECT unique_id FROM users WHERE unique_id = %s"
    result = db.fetch_data(check_query, (unique_id,))

    if result:  # If result is not empty, the ID is taken
        return "❌ This ID is already taken!"

    # ✅ Hash password and store in database
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  
    query = "INSERT INTO users (unique_id, name, password) VALUES (%s, %s, %s)"
    db.execute_query(query, (unique_id, name, hashed_password))
    
    return "✅ User Registered Successfully!"

# 🔹 Login User (Now returns user details instead of just True/False)
def login_user(unique_id, password):
    """Hashes input password and compares it with the hashed password stored in DB."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # ✅ Hash input password

    query = "SELECT unique_id, name FROM users WHERE unique_id = %s AND password = %s"
    result = db.fetch_data(query, (unique_id, hashed_password))  # ✅ Fetch user details

    return result[0] if result else None  # ✅ Return user data instead of just True/False

# 🔹 Get All Users (For Admin Panel)
def get_all_users():
    query = "SELECT unique_id, name FROM users ORDER BY unique_id ASC"
    return db.fetch_data(query)

# 🔹 Delete User by Unique ID (Admin Function)
def delete_user(unique_id):
    query = "DELETE FROM users WHERE unique_id = %s"
    db.execute_query(query, (unique_id,))
