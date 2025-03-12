import os
import hashlib
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, 
    QHBoxLayout, QFileDialog
)
from PyQt5.QtGui import QPixmap
from database import Database
from auth import is_valid_password
import shutil
db = Database()

class ProfilePage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.profile_pic_path = "profile_pics\default.jpg"  # Store profile picture path

        # 🔹 Main Layout
        layout = QVBoxLayout()

        # 🔹 Profile Picture Section
        self.setup_profile_picture_section(layout)

        # 🔹 User Info Section (ID, Name, Password)
        self.setup_user_info_section(layout)

        # 🔹 Buttons (Update Profile, Back)
        self.setup_buttons(layout)

        self.setLayout(layout)

    # ================== 🔹 PROFILE PICTURE SECTION ==================
    def setup_profile_picture_section(self, layout):
        """Set up the profile picture display and upload button."""
        self.profile_pic_label = QLabel(self)
        self.profile_pic_label.setFixedSize(100, 100)
        self.profile_pic_label.setScaledContents(True)
        layout.addWidget(self.profile_pic_label)

        self.upload_pic_btn = QPushButton("📸 Upload Profile Picture")
        self.upload_pic_btn.clicked.connect(self.upload_profile_picture)
        layout.addWidget(self.upload_pic_btn)

    # ================== 🔹 USER INFO SECTION ==================
    def setup_user_info_section(self, layout):
        """Set up the input fields for Unique ID, Name, and Password."""
        self.unique_id_input = QLineEdit()
        self.unique_id_input.setPlaceholderText("Unique ID (Cannot Change)")
        self.unique_id_input.setReadOnly(True)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter New Name")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter New Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        # Layout for user info
        user_info_layout = QHBoxLayout()
        user_info_layout.addWidget(self.unique_id_input)
        user_info_layout.addWidget(self.name_input)
        user_info_layout.addWidget(self.password_input)

        layout.addLayout(user_info_layout)

    # ================== 🔹 BUTTON SECTION ==================
    def setup_buttons(self, layout):
        """Set up buttons for updating profile and going back."""
        update_btn = QPushButton("Update Profile")
        update_btn.clicked.connect(self.update_profile)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.go_back)

        layout.addWidget(update_btn)
        layout.addWidget(back_btn)

    # ================== 🔹 PROFILE PICTURE UPLOAD ==================
    def upload_profile_picture(self):
        """Allows the user to upload a profile picture."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            # Store the profile picture path
            unique_id = self.unique_id_input.text()
            new_path = f"profile_pics/{unique_id}.jpg"  # Store as user_id.jpg
            os.makedirs("profile_pics", exist_ok=True)
            shutil.copy(file_path, new_path)

            self.profile_pic_path = new_path
            self.profile_pic_label.setPixmap(QPixmap(self.profile_pic_path))

    # ================== 🔹 LOAD USER DATA ==================
    def load_user_data(self, unique_id):
        """Loads user data into the input fields."""
        query = "SELECT name, password, profile_pic_path FROM users WHERE unique_id = %s"
        result = db.fetch_data(query, (unique_id,))
        if result:
            self.unique_id_input.setText(unique_id)
            self.name_input.setText(result[0][0])  # Load name
            self.password_input.setText("")  # Keep password field empty for security
            self.profile_pic_path = result[0][2] or "profile_pics/default.jpg"  # Load profile picture
            self.profile_pic_label.setPixmap(QPixmap(self.profile_pic_path))

    # ================== 🔹 UPDATE PROFILE ==================
    def update_profile(self):
        """Updates the user's profile information securely."""
        unique_id = self.unique_id_input.text()
        new_name = self.name_input.text()
        new_password = self.password_input.text()

        if new_name and new_password:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            query = "UPDATE users SET name = %s, password = %s, profile_pic_path = %s WHERE unique_id = %s"
            db.execute_query(query, (new_name, hashed_password, self.profile_pic_path, unique_id))

            QMessageBox.information(self, "Success", "✅ Profile Updated Successfully!")
        else:
            QMessageBox.warning(self, "Error", "❌ Fields cannot be empty!")

    # ================== 🔹 GO BACK ==================
    def go_back(self):
        """Redirect the user to the correct page after editing their profile."""
        if hasattr(self.main_window, "logged_in_user_id"):
            if self.main_window.logged_in_user_id == "0001":  # ✅ If admin (ID = 0001)
                self.main_window.stack.setCurrentWidget(self.main_window.admin_panel_page)
            else:
                self.main_window.stack.setCurrentWidget(self.main_window.notice_board_page)
        else:
            print("❌ Error: No user logged in!")
