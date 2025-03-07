from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget
from notice_manager import add_notice, get_all_notices, delete_notice
from auth import get_all_users, delete_user
from summarization import summarize_file

class AdminPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        self.title = QLabel("🔧 Admin Panel")
        layout.addWidget(self.title)

        # 🔹 Notice Management
        self.notice_list = QListWidget()
        layout.addWidget(QLabel("📜 Notices:"))
        layout.addWidget(self.notice_list)
        self.refresh_notices()

        upload_btn = QPushButton("📤 Upload Notice")
        upload_btn.clicked.connect(self.upload_notice)
        layout.addWidget(upload_btn)

        delete_notice_btn = QPushButton("❌ Delete Selected Notice")
        delete_notice_btn.clicked.connect(self.delete_selected_notice)
        layout.addWidget(delete_notice_btn)

        # 🔹 User Management
        self.user_list = QListWidget()
        layout.addWidget(QLabel("👥 Users:"))
        layout.addWidget(self.user_list)
        self.refresh_users()

        delete_user_btn = QPushButton("❌ Delete Selected User")
        delete_user_btn.clicked.connect(self.delete_selected_user)
        layout.addWidget(delete_user_btn)

        # 🔹 Profile Management Button (For Admin's Own Profile)
        profile_btn = QPushButton("📝 Edit My Profile")
        profile_btn.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.profile_page))
        layout.addWidget(profile_btn)

        # 🔹 Logout Button
        back_btn = QPushButton("🔙 Logout")
        back_btn.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.login_page))
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def refresh_notices(self):
        self.notice_list.clear()
        notices = get_all_notices()
        for notice in notices:
            self.notice_list.addItem(f"{notice[0]}: {notice[1]}")  # ID: Title

    def upload_notice(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Notice", "", "PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            summary = summarize_file(file_path)
            add_notice(file_path, "Content extracted from file", summary)
            self.refresh_notices()

    def delete_selected_notice(self):
        selected_item = self.notice_list.currentItem()
        if selected_item:
            notice_id = selected_item.text().split(":")[0]  # Extract ID from text
            delete_notice(notice_id)
            self.refresh_notices()

    def refresh_users(self):
        self.user_list.clear()
        users = get_all_users()
        for user in users:
            self.user_list.addItem(f"{user[0]} - {user[1]}")  # Unique ID - Name

    def delete_selected_user(self):
        selected_item = self.user_list.currentItem()
        if selected_item:
            unique_id = selected_item.text().split(" - ")[0]  # Extract Unique ID
            delete_user(unique_id)
            self.refresh_users()