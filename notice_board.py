import os
import shutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox,QHBoxLayout,QScrollArea
from notice_manager import get_latest_notices
from profile_page import ProfilePage  # ✅ Import your existing ProfilePage

class NoticeBoard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.layout = QVBoxLayout()
        self.notice_widgets = []  # ✅ Store notice widgets

        self.label = QLabel("📜 Welcome to the Notice Board")
        self.layout.addWidget(self.label)
        self.edit_profile_btn = QPushButton("Edit My Profile")
        self.edit_profile_btn.clicked.connect(self.open_profile_editor)
        self.layout.addWidget(self.edit_profile_btn)
        self.notice_labels = []  # ✅ List to store notice labels
        for _ in range(2):  # ✅ Show latest 3 notices
            notice_label = QLabel("")
            self.layout.addWidget(notice_label)
            self.notice_labels.append(notice_label)
        back_btn = QPushButton("🔙 Logout")
        back_btn.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.login_page))
        self.layout.addWidget(back_btn)
        self.setLayout(self.layout)


    def open_profile_editor(self):
        """Function to switch to the Profile Editing Page."""
        if not hasattr(self.main_window, "logged_in_user_id"):  # ✅ Check if logged-in ID exists
            QMessageBox.warning(self, "Error", "❌ No user logged in!")
            return

        unique_id = self.main_window.logged_in_user_id  # ✅ Get the stored user ID
        self.main_window.profile_page.load_user_data(unique_id)  # ✅ Load user details
        self.main_window.stack.setCurrentWidget(self.main_window.profile_page)  # ✅ Switch page


    def refresh_notices(self):
        """Fetch and display the latest notices with download buttons."""
        from notice_manager import get_latest_notices  

        latest_notices = get_latest_notices(3)

        # ✅ Remove existing notice labels and buttons before adding new ones
        for widget in self.notice_labels:
            widget.deleteLater()  # Properly remove from UI
        self.notice_labels.clear()

        # ✅ Find and remove old download buttons
        for i in reversed(range(self.layout.count())):
            item = self.layout.itemAt(i)
            if isinstance(item.widget(), QPushButton) and item.widget().text() == "⬇️ Download":
                item.widget().deleteLater()  # Remove old download buttons

        # ✅ Add new notices and buttons
        for title, content, file_path, notice_time in latest_notices:
            notice_label = QLabel(f"<b>{title}</b> at ({notice_time})->\n{content}")
            notice_label.setWordWrap(True)
            notice_label.setFixedWidth(500)
            self.layout.addWidget(notice_label)

            if file_path and os.path.exists(file_path):  
                download_btn = QPushButton("⬇️ Download")
                download_btn.clicked.connect(lambda checked, path=file_path: self.download_file(path))
                self.layout.addWidget(download_btn)

            self.notice_labels.append(notice_label)

        self.setMaximumWidth(800) 

    def download_file(self, file_path):
        """Opens the file location to let the user download it."""
        if os.path.exists(file_path):
            os.startfile(file_path)  # Opens the file in its default application
        else:
            print("❌ File not found:", file_path)

    def showEvent(self, event):
        """Refresh notices every time the page is loaded."""
        self.refresh_notices()
        
