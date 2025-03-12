from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget, QLineEdit, QListWidgetItem
from notice_manager import add_notice, get_all_notices, delete_notice
from auth import get_all_users, delete_user
from summarization import summarize_file
from PyQt5.QtCore import Qt

class AdminPanel(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # 🔹 Main Layout
        self.layout = QVBoxLayout()
        
        # 🔹 Title Section
        self.title = QLabel("🔧 Admin Panel")
        self.layout.addWidget(self.title)

        # 🔹 Notice Management Section
        self.setup_notice_management()

        # 🔹 User Management Section
        self.setup_user_management()

        # 🔹 Profile and Logout Section
        self.setup_profile_and_logout()

        self.setLayout(self.layout)

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

        notice_upload_layout.addWidget(QLabel("Notice Name"))
        notice_upload_layout.addWidget(self.Nnoticename)
        notice_upload_layout.addWidget(upload_btn)

        self.layout.addLayout(notice_upload_layout)

        # 🔹 Delete Notice Button
        delete_notice_btn = QPushButton("❌ Delete Selected Notice")
        delete_notice_btn.clicked.connect(self.delete_selected_notice)
        self.layout.addWidget(delete_notice_btn)

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

    def setup_profile_and_logout(self):
        """Setup UI components for admin profile and logout."""
        profile_btn = QPushButton("📝 Edit My Profile")
        profile_btn.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.profile_page))
        self.layout.addWidget(profile_btn)

        back_btn = QPushButton("🔙 Logout")
        back_btn.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.login_page))
        self.layout.addWidget(back_btn)

    # 🔹 Notice Management Functions
    def upload_notice(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Notice", "", "PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            Noticename = self.Nnoticename.text()
            summary = summarize_file(file_path)
            add_notice(Noticename, "Content extracted from file", summary, file_path)  # ✅ Now storing file path
            self.refresh_notices()

    def delete_selected_notice(self):
        selected_item = self.notice_list.currentItem()
        if selected_item:
            notice_id = selected_item.data(Qt.UserRole)  # Retrieve stored notice ID
            if notice_id:
                delete_notice(notice_id)  # Call function to delete from DB
                self.refresh_notices()
            else:
                print("❌ Error: Notice ID not found!")

    def refresh_notices(self):
        self.notice_list.clear()
        notices = get_all_notices()  # Modify function to return (id, title, timestamp)
        
        for notice in notices:
            notice_id, title, summary, timestamp, file_path = notice
            item_text = f"📢 {title} - {summary} ({timestamp})"
            
            # Create QListWidgetItem and store ID
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, notice_id)  # 🔹 Store SQL notice ID in the item
            self.notice_list.addItem(item)

    # 🔹 User Management Functions
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
