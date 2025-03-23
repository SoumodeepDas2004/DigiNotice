from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, 
    QListWidget, QLineEdit, QListWidgetItem
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from notice_manager import add_notice, get_all_notices, delete_notice
from auth import get_all_users, delete_user
from summarization import summarize_file
import os

class AdminPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.uniqueid = "0001"

        # 🔹 Main Layout
        self.layout = QVBoxLayout()

        # 🔹 Header Section (Title + Profile Picture)
        self.setup_header_section()

        # 🔹 Notice Management Section
        self.setup_notice_management()

        # 🔹 User Management Section
        self.setup_user_management()

        # 🔹 Profile & Logout Section (Better Layout)
        self.setup_profile_and_logout()

        self.setLayout(self.layout)

    # ================== 🔹 HEADER SECTION ==================
    def setup_header_section(self):
        """Setup Admin Panel Title & Profile Picture."""
        header_layout = QHBoxLayout()

        self.title = QLabel("🔧 Admin Panel")
        self.title.setStyleSheet("font-size: 18px; font-weight: bold;")

        # 🔹 Admin Profile Picture
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(50, 50)
        self.profile_pic_label.setScaledContents(True)
        self.load_admin_profile_picture()

        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(self.profile_pic_label)

        self.layout.addLayout(header_layout)

    def load_admin_profile_picture(self):
        """Loads the admin's profile picture or default image."""
        profile_pic_path = f"profile_pics/{self.uniqueid}.jpg"
        if not os.path.exists(profile_pic_path):
            profile_pic_path = "profile_pics/default.jpg"
        self.profile_pic_label.setPixmap(QPixmap(profile_pic_path))

    # ================== 🔹 NOTICE MANAGEMENT SECTION ==================
    def setup_notice_management(self):
        """Setup UI components for notice management."""
        self.layout.addWidget(QLabel("📜 Notices:"))

        # 🔹 List of Notices
        self.notice_list = QListWidget()
        self.layout.addWidget(self.notice_list)
        self.refresh_notices()

        # 🔹 Upload Notice Section
        notice_upload_layout = QHBoxLayout()

        self.Nnoticename = QLineEdit()
        self.Nnoticename.setPlaceholderText("Enter Notice Name")

        upload_btn = QPushButton("📤 Upload Notice")
        upload_btn.clicked.connect(self.upload_notice)

        notice_upload_layout.addWidget(QLabel("Notice Name:"))
        notice_upload_layout.addWidget(self.Nnoticename)
        notice_upload_layout.addWidget(upload_btn)

        self.layout.addLayout(notice_upload_layout)

        # 🔹 Delete Notice Button
        delete_notice_btn = QPushButton("❌ Delete Selected Notice")
        delete_notice_btn.clicked.connect(self.delete_selected_notice)
        self.layout.addWidget(delete_notice_btn)

    # ================== 🔹 USER MANAGEMENT SECTION ==================
    def setup_user_management(self):
        """Setup UI components for user management."""
        self.layout.addWidget(QLabel("👥 Users:"))

        # 🔹 List of Users
        self.user_list = QListWidget()
        self.layout.addWidget(self.user_list)
        self.refresh_users()

        # 🔹 Delete User Button
        delete_user_btn = QPushButton("❌ Delete Selected User")
        delete_user_btn.clicked.connect(self.delete_selected_user)
        self.layout.addWidget(delete_user_btn)

    # ================== 🔹 PROFILE & LOGOUT SECTION ==================
    def setup_profile_and_logout(self):
        """Setup Profile Edit & Logout buttons in a horizontal row."""
        profile_logout_layout = QHBoxLayout()

        profile_btn = QPushButton("📝 Edit My Profile")
        profile_btn.clicked.connect(self.open_profile_editor)
        profile_logout_layout.addWidget(profile_btn)

        logout_btn = QPushButton("🔙 Logout")
        logout_btn.clicked.connect(self.logout)
        profile_logout_layout.addWidget(logout_btn)

        self.layout.addLayout(profile_logout_layout)

    # ================== 🔹 NOTICE MANAGEMENT FUNCTIONS ==================
    def upload_notice(self):
        """Handles the process of uploading a new notice."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Notice", "", "PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            Noticename = self.Nnoticename.text()
            summary = summarize_file(file_path)
            add_notice(Noticename, "Content extracted from file", summary, file_path)  # ✅ Store file path
            self.refresh_notices()

    def delete_selected_notice(self):
        """Deletes a selected notice and refreshes both the admin & user notice board."""
        selected_item = self.notice_list.currentItem()
        if selected_item:
            notice_id = selected_item.data(Qt.UserRole)  # Retrieve stored notice ID
            if notice_id:
                delete_notice(notice_id)  # Delete from DB
                self.refresh_notices()
                self.main_window.notice_board_page.refresh_notices()  # ✅ Update user notice board too
            else:
                print("❌ Error: Notice ID not found!")

    def refresh_notices(self):
        """Fetches and displays the latest notices."""
        self.notice_list.clear()
        notices = get_all_notices()

        for notice in notices:
            notice_id, title, summary, timestamp, file_path = notice
            item_text = f"📢 {title} - {summary} ({timestamp})"

            # Create QListWidgetItem and store ID
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, notice_id)  # 🔹 Store SQL notice ID in the item
            self.notice_list.addItem(item)

    # ================== 🔹 USER MANAGEMENT FUNCTIONS ==================
    def refresh_users(self):
        """Fetches and displays the list of users."""
        self.user_list.clear()
        users = get_all_users()
        for user in users:
            self.user_list.addItem(f"{user[0]} - {user[1]}")  # Unique ID - Name

    def delete_selected_user(self):
        """Deletes a selected user."""
        selected_item = self.user_list.currentItem()
        if selected_item:
            unique_id = selected_item.text().split(" - ")[0]  # Extract Unique ID
            delete_user(unique_id)
            self.refresh_users()

    # ================== 🔹 PROFILE MANAGEMENT ==================
    def open_profile_editor(self):
        """Opens the admin profile editing page."""
        self.main_window.profile_page.load_user_data(self.uniqueid)  # ✅ Ensure admin data is loaded
        self.main_window.stack.setCurrentWidget(self.main_window.profile_page)
        
    def logout(self):
        
        """Logs out the user and returns to the login page."""
        print(f"🔴 Logging out User ID: {self.main_window.logged_in_user_id}")
        self.main_window.logged_in_user_id = None
        self.main_window.stack.setCurrentWidget(self.main_window.login_page)