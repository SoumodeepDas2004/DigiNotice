from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
from database import Database
import hashlib
import re

db = Database()

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

# 🔹 Login Page UI (QWidget for StackedWidget)
class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()
        
        self.label = QLabel("Enter Unique ID & Password:")
        layout.addWidget(self.label)

        self.unique_id_input = QLineEdit()
        self.unique_id_input.setPlaceholderText("Unique ID (4-digit)")
        layout.addWidget(self.unique_id_input)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name(Compulsory for registration)")
        layout.addWidget(self.name_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)
        layout.addWidget(register_btn)

        self.setLayout(layout)

    def login(self):
        unique_id = self.unique_id_input.text()
        password = self.password_input.text()
        
        print(f"🔍 Attempting login with ID: {unique_id}")  # Debugging statement

        if unique_id.isdigit() and len(unique_id) == 4:
            user_data = login_user(unique_id, password)  # ✅ Now gets user details
            
            print(f"🟢 login_user() returned: {user_data}")  # Debugging statement
            
            if user_data:
                self.main_window.login_success(user_data[0], user_data[1])  # ✅ Call login_success()
            else:
                self.label.setText("❌ Invalid Credentials!")
                print("❌ Login failed!")
        else:
            self.label.setText("❌ Unique ID must be 4 digits!")


    def register(self):
        unique_id = self.unique_id_input.text()
        name = self.name_input.text()
        password = self.password_input.text()

        if unique_id.isdigit() and len(unique_id) == 4:
            message = register_user(unique_id, name, password)  # ✅ Get success/error message
            self.label.setText(message)  # ✅ Show the message in the UI
        else:
            self.label.setText("❌ Unique ID must be 4 digits!")
