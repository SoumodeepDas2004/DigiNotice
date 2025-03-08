from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
from database import Database
import hashlib,re
db = Database()

def is_valid_password(password):
    return bool(re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()-_])[A-Za-z\d!@#$%^&*()-_]{6,}$", password))

# 🔹 Register User
def register_user(unique_id, name, password):
    """Check if the unique_id already exists before inserting."""
    check_query = "SELECT unique_id FROM users WHERE unique_id = %s"
    result = db.fetch_data(check_query, (unique_id,))

    if result:  # ✅ If result is not empty, the ID already exists
        return "❌ This ID is already taken!"

    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # ✅ Hash password
    query = "INSERT INTO users (unique_id, name, password) VALUES (%s, %s, %s)"
    db.execute_query(query, (unique_id, name, hashed_password))
    
    return "✅ User Registered Successfully!"

# 🔹 Login User
def login_user(unique_id, name, password):
    """Hashes input password and compares it with the hashed password stored in DB"""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # ✅ Hash input password

    query = "SELECT * FROM users WHERE unique_id = %s AND name = %s AND password = %s"
    result = db.fetch_data(query, (unique_id, name, hashed_password))  # ✅ Compare hashed password
    
    return bool(result)  # Returns True if user exists

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

        self.label = QLabel("Enter Unique ID, Name & Password:")
        layout.addWidget(self.label)

        self.unique_id_input = QLineEdit()
        self.unique_id_input.setPlaceholderText("Unique ID (4-digit)")
        layout.addWidget(self.unique_id_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")
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
        name = self.name_input.text()
        password = self.password_input.text()  # ✅ Get password input

        if unique_id.isdigit() and len(unique_id) == 4:
            if login_user(unique_id, name, password):  # ✅ Pass all three arguments
                self.main_window.logged_in_user_id = unique_id  # ✅ Store logged-in user ID
                if unique_id == "0001":  # Example: Admin has Unique ID 0001
                    self.main_window.stack.setCurrentWidget(self.main_window.admin_panel_page)
                else:
                    self.main_window.stack.setCurrentWidget(self.main_window.notice_board_page)
            else:
                self.label.setText("❌ Invalid Credentials!")
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