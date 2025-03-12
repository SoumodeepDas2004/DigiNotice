import os
import shutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QScrollArea
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from notice_manager import get_latest_notices
from profile_page import ProfilePage  # ✅ Import your existing ProfilePage


class NoticeBoard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # 🔹 Main Layout
        self.layout = QVBoxLayout()
        self.notice_labels = []  # ✅ List to store notice labels
        self.notice_widgets = []  # ✅ Store notice widgets

        # 🔹 Header Section
        self.setup_header_section()

        # 🔹 Notices Display Section
        self.setup_notice_section()

        # 🔹 Footer Section (Logout Button)
        self.setup_footer_section()

        self.setLayout(self.layout)

    # ================== 🔹 HEADER SECTION ==================
    def setup_header_section(self):
        """Set up the header with title and profile edit button."""
        self.label = QLabel("📜 Welcome to the Notice Board")
        self.label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter) # Center align both vertically and horizontally
        self.label.setFont(QFont("Arial", 24))
        self.layout.addWidget(self.label)

        self.edit_profile_btn = QPushButton("Edit Profile")
        self.edit_profile_btn.setFixedSize(100, 30)
        self.edit_profile_btn.setStyleSheet("""
    QPushButton {
        color: #00ff00; /* Green text */
        font-weight: bold;
        background-color: #ffffff; /* White background */
    }
    QPushButton:hover {
    background-color: #1de6b2;
    color: white;
}
""")
        self.edit_profile_btn.clicked.connect(self.open_profile_editor)
        self.layout.addWidget(self.edit_profile_btn)

    # ================== 🔹 NOTICE DISPLAY SECTION ==================
    def setup_notice_section(self):
        """Set up the section where the latest notices are displayed."""
        self.scroll_area = QScrollArea()  # ✅ Scrollable area for notices
        self.scroll_area.setWidgetResizable(True)
        self.notice_container = QWidget()
        self.notice_layout = QVBoxLayout()

        for _ in range(2):  # ✅ Show latest 2 notices initially
            notice_label = QLabel("")
            self.notice_layout.addWidget(notice_label)
            self.notice_labels.append(notice_label)

        self.notice_container.setLayout(self.notice_layout)
        self.scroll_area.setWidget(self.notice_container)
        self.layout.addWidget(self.scroll_area)

    # ================== 🔹 FOOTER SECTION ==================
    def setup_footer_section(self):
        """Set up the footer with a logout button."""
        back_btn = QPushButton("🔙 Logout")
        back_btn.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.login_page))
        self.layout.addWidget(back_btn)

    # ================== 🔹 PROFILE EDIT FUNCTION ==================
    def open_profile_editor(self):
        """Function to switch to the Profile Editing Page."""
        if not hasattr(self.main_window, "logged_in_user_id"):  # ✅ Check if logged-in ID exists
            QMessageBox.warning(self, "Error", "❌ No user logged in!")
            return

        unique_id = self.main_window.logged_in_user_id  # ✅ Get the stored user ID
        self.main_window.profile_page.load_user_data(unique_id)  # ✅ Load user details
        self.main_window.stack.setCurrentWidget(self.main_window.profile_page)  # ✅ Switch page

    # ================== 🔹 REFRESH NOTICES ==================
    def refresh_notices(self):
        """Fetch and display the latest notices with download buttons."""
        latest_notices = get_latest_notices(3)

        # ✅ Remove existing notice labels and buttons before adding new ones
        for widget in self.notice_labels:
            widget.deleteLater()  # Properly remove from UI
        self.notice_labels.clear()

        # ✅ Find and remove old download buttons
        for i in reversed(range(self.notice_layout.count())):
            item = self.notice_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()  # Remove old widgets

        # ✅ Add new notices and buttons
        for title, content, file_path, notice_time in latest_notices:
            notice_label = QLabel(f"<b>{title}</b> at ({notice_time})->\n{content}")
            notice_label.setWordWrap(True)
            notice_label.setFixedWidth(500)
            self.notice_layout.addWidget(notice_label)

            if file_path and os.path.exists(file_path):  
                download_btn = QPushButton("⬇️ Download")
                download_btn.clicked.connect(lambda checked, path=file_path: self.download_file(path))
                self.notice_layout.addWidget(download_btn)

            self.notice_labels.append(notice_label)

        self.setMaximumWidth(800)

    # ================== 🔹 DOWNLOAD FILE FUNCTION ==================
    def download_file(self, file_path):
        """Opens the file location to let the user download it."""
        if os.path.exists(file_path):
            os.startfile(file_path)  # Opens the file in its default application
        else:
            print("❌ File not found:", file_path)

    # ================== 🔹 SHOW EVENT ==================
    def showEvent(self, event):
        """Refresh notices every time the page is loaded."""
        self.refresh_notices()
