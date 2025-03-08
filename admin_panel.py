from PyQt5.QtWidgets import QWidget, QVBoxLayout,QHBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget,QLineEdit
from notice_manager import add_notice, get_latest_notices, delete_notice
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
        
        r=QHBoxLayout()
        self.Nnoticename=QLineEdit()
        self.Nnoticename.setPlaceholderText("Enter Notice Name")
        upload_btn = QPushButton("📤 Upload Notice")
        upload_btn.clicked.connect(self.upload_notice) 
        r.addWidget(QLabel("Notice Name"))
        r.addWidget(self.Nnoticename)
        r.addWidget(upload_btn)
        layout.addLayout(r)
        
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

    def upload_notice(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Notice", "", "PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            Noticename = self.Nnoticename.text()
            summary = summarize_file(file_path)
            add_notice(Noticename, "Content extracted from file", summary, file_path)  # ✅ Now storing file path
            self.refresh_notices()


    def delete_selected_notice(self):
        """Deletes the selected notice and refreshes the UI."""
        selected_item = self.notice_list.currentItem()
        
        if selected_item:
            notice_text = selected_item.text()  # Example: "📢 Notice-3 (2025-03-08 16:30)"
            
            try:
                notice_id = int(notice_text.split()[1].split("-")[1])  # ✅ Extract number part safely
                delete_notice(notice_id)  # ✅ Ensure `notice_id` is an integer
                self.refresh_notices()  # ✅ Refresh UI
                self.main_window.notice_board_page.refresh_notices()
            except (ValueError, IndexError):
                print("❌ Error: Could not extract a valid notice ID!")
            
    def refresh_notices(self):
        """Fetch and display the latest notices after deletion."""
        self.notice_list.clear()  # ✅ Only clear notice list, not entire layout

        latest_notices = get_latest_notices(5)  # ✅ Fetch latest notices

        for notice in latest_notices:
            title, content, file_path, notice_time = notice  # ✅ Unpack values correctly
            self.notice_list.addItem(f"📢 {title} ({notice_time})")  # ✅ Display title & time

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