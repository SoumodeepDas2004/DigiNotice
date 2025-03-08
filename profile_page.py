from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox
from database import Database
import hashlib  # ✅ Added for password hashing
from auth import is_valid_password
db = Database()

class ProfilePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        self.label = QLabel("📝 Edit Your Profile")
        layout.addWidget(self.label)

        self.unique_id_input = QLineEdit()
        self.unique_id_input.setPlaceholderText("Unique ID (Cannot Change)")
        self.unique_id_input.setReadOnly(True)  # Unique ID should not be editable
        layout.addWidget(self.unique_id_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter New Name")
        layout.addWidget(self.name_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter New Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        update_btn = QPushButton("Update Profile")
        update_btn.clicked.connect(self.update_profile)
        layout.addWidget(update_btn)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.notice_board_page))
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def load_user_data(self, unique_id):
        """Loads user data into the input fields."""
        query = "SELECT name, password FROM users WHERE unique_id = %s"
        result = db.fetch_data(query, (unique_id,))
        if result:
            self.unique_id_input.setText(unique_id)
            self.name_input.setText(result[0][0])  # Load name
            self.password_input.setText("")  # Keep password field empty for security

    def update_profile(self):
        """Updates the user's profile information securely."""
        unique_id = self.unique_id_input.text()
        new_name = self.name_input.text()
        new_password = self.password_input.text()

        if new_name and new_password:
            if not is_valid_password(new_password):
                QMessageBox.warning(self, "Error", "❌ Password must be alphanumeric with 1-2 special characters!")
                return

            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()  # ✅ Hash password

            query = "UPDATE users SET name = %s, password = %s WHERE unique_id = %s"
            db.execute_query(query, (new_name, hashed_password, unique_id))

            QMessageBox.information(self, "Success", "✅ Profile Updated Successfully!")
        else:
            QMessageBox.warning(self, "Error", "❌ Fields cannot be empty!")
