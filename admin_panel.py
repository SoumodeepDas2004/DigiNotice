from PyQt5.QtWidgets import QWidget, QVBoxLayout,QHBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget,QLineEdit,QListWidgetItem
from notice_manager import add_notice, get_all_notices, delete_notice
from auth import get_all_users, delete_user
from summarization import summarize_file
from PyQt5.QtCore import Qt

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
        self.layout=layout
        self.setLayout(self.layout)

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
            notice_id = selected_item.data(Qt.UserRole)  # Retrieve the stored notice ID

            if notice_id:
                delete_notice(notice_id)  # Call the function to delete from DB
                self.refresh_notices()  # Refresh the list after deletion
            else:
                print("❌ Error: Notice ID not found!")

            
    def refresh_notices(self):
        self.notice_list.clear()
        
        # Fetch all notices from the database (ensure your query returns ID too!)
        notices = get_all_notices()  # Modify this function to return (id, title, timestamp)
        
        for notice in notices:
            notice_id, title, summary,timestamp,file_path = notice  
            
            # Format display text
            item_text = f"📢 {title}-{summary} ({timestamp})"
            
            # Create QListWidgetItem and store ID
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, notice_id)  # 🔹 Store SQL notice ID in the item
        
            # Add item to the list
            self.notice_list.addItem(item)
    


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