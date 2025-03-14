import os
import shutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, 
    QHBoxLayout, QScrollArea
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from notice_manager import get_latest_notices
from database import Database
from profile_page import ProfilePage
db = Database()

class NoticeBoard(QWidget):
    def __init__(self, main_window, uniqueid=None):
        super().__init__()
        self.main_window = main_window  # ✅ Store reference to main window
        self.uniqueid = uniqueid  # ✅ Store logged-in user ID
        self.profile_pic_path = "profile_pics/default.jpg"  # ✅ Default Profile Picture

        # 🔹 Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)  # ✅ Corrected layout setting

        # 🔹 UI Sections
        self.setup_header_section()  # ✅ Profile, Edit Button
        self.setup_notice_section()  # ✅ Notice List
        self.setup_footer_section()  # ✅ Logout Button

    # ================== 🔹 HEADER SECTION ==================
    def setup_header_section(self):
        """Set up the header with profile picture, edit button, and title."""
        header_layout = QHBoxLayout()

        # 🔹 Profile Picture (Rounded)
        self.profile_pic_label = QLabel(self)
        self.profile_pic_label.setFixedSize(50, 50)  # ✅ Set image size
        self.profile_pic_label.setScaledContents(True)
        self.profile_pic_label.setStyleSheet("border-radius: 25px; border: 2px solid #4CAF50;")
        self.load_profile_picture()  # ✅ Load user profile picture

        # 🔹 Edit Profile Button
        self.edit_profile_btn = QPushButton("Edit Profile")
        self.edit_profile_btn.setFixedSize(120, 30)
        self.edit_profile_btn.setStyleSheet("""
            QPushButton {
                color: #00ff00;
                font-weight: bold;
                background-color: #ffffff;
            }
            QPushButton:hover {
                background-color: #1de6b2;
                color: white;
            }
        """)
        self.edit_profile_btn.clicked.connect(self.open_edit_profile)

        # 🔹 Notice Board Title
        title_label = QLabel("Notice Board")
        title_label.setFont(QFont('Arial', 15))

        # 🔹 Arrange Items in Layout
        header_layout.addWidget(self.profile_pic_label)
        header_layout.addWidget(self.edit_profile_btn)
        header_layout.addStretch()  # ✅ Push title to the right
        header_layout.addWidget(title_label)

        self.layout.addLayout(header_layout)

        # 🔹 Welcome Label
        welcome_label = QLabel("📜 Welcome to the Notice Board")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setFont(QFont("Arial", 24))
        self.layout.addWidget(welcome_label)

    # ================== 🔹 LOAD PROFILE PICTURE ==================
    def load_profile_picture(self):
        """Load and refresh the user's profile picture."""
        query = "SELECT profile_pic_path FROM users WHERE unique_id = %s"
        result = db.fetch_data(query, (self.uniqueid,))

        if result and result[0][0]:  
            self.profile_pic_path = result[0][0]  
            print(self.profile_pic_path)
        else:
            self.profile_pic_path = "profile_pics/default.jpg"  # Use default if no picture
        
        if os.path.exists(self.profile_pic_path):
            pixmap = QPixmap(self.profile_pic_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.profile_pic_label.setPixmap(pixmap)
        else:
            self.profile_pic_label.setPixmap(QPixmap("profile_pics/default.jpg"))  # Fallback image

    # ================== 🔹 NOTICE DISPLAY SECTION ==================
    def setup_notice_section(self):
        """Set up the section where notices are displayed."""
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.notice_container = QWidget()
        self.notice_layout = QVBoxLayout()

        self.notice_container.setLayout(self.notice_layout)
        self.scroll_area.setWidget(self.notice_container)
        self.layout.addWidget(self.scroll_area)

        # ✅ Load Notices Initially
        self.refresh_notices()

    # ================== 🔹 FOOTER SECTION ==================
    def setup_footer_section(self):
        """Set up the footer with a logout button."""
        logout_btn = QPushButton("🔙 Logout")
        logout_btn.clicked.connect(self.logout)
        self.layout.addWidget(logout_btn)

    # ================== 🔹 REFRESH NOTICES ==================
    def refresh_notices(self):
        """Fetch and display the latest notices."""
        latest_notices = get_latest_notices(3)

        # ✅ Clear previous notices
        for i in reversed(range(self.notice_layout.count())):
            item = self.notice_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        # ✅ Add new notices
        for title, content, file_path, notice_time in latest_notices:
            notice_label = QLabel(f"<b>{title}</b> at ({notice_time})\n{content}")
            notice_label.setWordWrap(True)
            notice_label.setFixedWidth(500)
            self.notice_layout.addWidget(notice_label)

            if file_path and os.path.exists(file_path):  
                download_btn = QPushButton("⬇️ Download")
                download_btn.clicked.connect(lambda checked, path=file_path: self.download_file(path))
                self.notice_layout.addWidget(download_btn)
    def download_file(self, file_path):
            """Opens the file location to let the user download it."""
            if os.path.exists(file_path):
                os.startfile(file_path)  # ✅ Open in default application
            else:
                QMessageBox.warning(self, "Error", "❌ File not found!")

    # ================== 🔹 OPEN PROFILE PAGE ==================
    def open_edit_profile(self):
        """Opens the Profile Page if a user is logged in."""
        if not self.main_window.logged_in_user_id:
            QMessageBox.warning(self, "Error", "❌ No user logged in!")
            return

        # ✅ Ensure Profile Page is created
        if not hasattr(self.main_window, "profile_page"):
            print("⚠️ Profile Page is None! Creating it now...")
            self.main_window.profile_page = ProfilePage(self.main_window)
            self.main_window.stack.addWidget(self.main_window.profile_page)

        print(f"✅ Opening Profile Page for User: {self.main_window.logged_in_user_id}")
        self.main_window.profile_page.load_user_data(self.main_window.logged_in_user_id)
        self.main_window.stack.setCurrentWidget(self.main_window.profile_page)

    # ================== 🔹 LOGOUT FUNCTION ==================
    def logout(self):
        """Logs out the user and returns to the login page."""
        print(f"🔴 Logging out User ID: {self.main_window.logged_in_user_id}")
        self.main_window.logged_in_user_id = None
        self.main_window.stack.setCurrentWidget(self.main_window.login_page)

    # ================== 🔹 SHOW EVENT ==================
    def showEvent(self, event):
        """Refresh notices and update profile picture every time the page is loaded."""
        self.refresh_notices()
        self.load_profile_picture()
