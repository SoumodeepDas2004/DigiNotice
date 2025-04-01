from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, 
    QListWidget, QLineEdit, QListWidgetItem
)
from PyQt5.QtGui import QPixmap, QLinearGradient, QPalette
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

        self.background_label = QLabel(self)
        self.bgimgpath = "assets/bgpics/bgadmin.jpg"
        self.set_background_image(self.bgimgpath)

        self.setStyleSheet('''QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #cdffd8, stop: 1 #8aadf1);
        color: black;
        border: white;
        border-radius: 20px;
        font-weight: bold;
        font-size: 20px;
    }
        QPushButton:hover{background-color: #00598A; color: white; font-weight: bolder; border: 2px solid #02f707; font-size: 20px; border-radius: 20px;}
    ''')

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
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        # 🔹 Admin Profile Picture
        self.profile_pic_label = QLabel()
        self.profile_pic_label.setFixedSize(50, 50)
        self.profile_pic_label.setScaledContents(True)
        self.profile_pic_label.setStyleSheet("border-radius: 25px; border: 4px solid black;")
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
        self.notice_label = QLabel("📜 Notices:")
        self.notice_label.setFixedSize(200,20)
        self.notice_label.setStyleSheet("QLabel{color: white; font-size: 18px; font-weight: bold;}")
        self.layout.addWidget(self.notice_label)

        # 🔹 List of Notices
        self.notice_list = QListWidget()
        self.notice_list.setFixedSize(1900, 200)
        self.notice_list.setStyleSheet("QListWidget{background-color: rgba(0,0,0,150); color: #dbbc09; font-weight: bold; border: 2px solid #02f707; border-radius: 10px;}")
        self.layout.addWidget(self.notice_list)
        self.refresh_notices()

        # 🔹 Upload Notice Section
        notice_upload_layout = QHBoxLayout()

        self.Nnoticename = QLineEdit()
        self.Nnoticename.setPlaceholderText("Enter Notice Name")
        self.Nnoticename.setFixedSize(750,50)
        self.Nnoticename.setStyleSheet('''QLineEdit{background-color: rgba(0,0,0,150); color: rgba(70, 229, 208, 1); border: 2px solid yellow; font-size: 16px;}
                            ''')

        upload_btn = QPushButton("📤 Upload Notice")
        upload_btn.setFixedSize(180,35)
        upload_btn.setStyleSheet("QPushButton{font-weight: normal; border: 2px solid #02f707; border-radius:15px;}")
        upload_btn.clicked.connect(self.upload_notice)

        self.notice_upload_label = QLabel("Notice Name:")
        self.notice_upload_label.setFixedSize(170,35)
        self.notice_upload_label.setAlignment(Qt.AlignCenter)
        self.notice_upload_label.setStyleSheet("QLabel{color: black; font-size: 18px; font-weight: bold; background-color: rgba(26, 228, 19, 0.61); border-radius: 10px; padding: 5px;}")
        notice_upload_layout.addWidget(self.notice_upload_label)
        notice_upload_layout.addWidget(self.Nnoticename)
        notice_upload_layout.addWidget(upload_btn)

        self.layout.addLayout(notice_upload_layout)

        # 🔹 Delete Notice Button
        self.delete_notice_layout = QHBoxLayout()
        delete_notice_btn = QPushButton("❌ Delete Selected Notice")
        delete_notice_btn.setFixedSize(800,50)
        delete_notice_btn.clicked.connect(self.delete_selected_notice)
        self.delete_notice_layout.addWidget(delete_notice_btn)
        self.layout.addLayout(self.delete_notice_layout)

    # ================== 🔹 USER MANAGEMENT SECTION ==================
    def setup_user_management(self):
        """Setup UI components for user management."""
        self.user_label = QLabel("👥 Users:")
        self.user_label.setFixedSize(200,20)
        self.user_label.setStyleSheet("QLabel{color: white; font-size: 18px; font-weight: bold;}")
        self.layout.addWidget(self.user_label)

        # 🔹 List of Users
        self.user_list = QListWidget()
        self.user_list.setFixedSize(1900, 200)
        self.user_list.setStyleSheet("QListWidget{background-color: rgba(0,0,0,150); color: yellow; font-weight:bold ; border:2px solid #02f707 ; border-radius: 10px;}")
        self.layout.addWidget(self.user_list)
        self.refresh_users()

        # 🔹 Delete User Button
        self.delete_user_layout = QHBoxLayout()
        delete_user_btn = QPushButton("❌ Delete Selected User")
        delete_user_btn.setFixedSize(800,50)
        delete_user_btn.clicked.connect(self.delete_selected_user)
        self.delete_user_layout.addWidget(delete_user_btn)
        self.layout.addLayout(self.delete_user_layout)

    # ================== 🔹 PROFILE & LOGOUT SECTION ==================
    def setup_profile_and_logout(self):
        """Setup Profile Edit & Logout buttons in a horizontal row."""
        profile_logout_layout = QHBoxLayout()

        profile_btn = QPushButton("📝 Edit My Profile")
        profile_btn.setStyleSheet('''
    QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #f85bc7, stop: 1 #3533cd);
        color: white;
        border: #7ed957;
        border-radius: 5px;
        font-weight: bold;
        font-size: 20px;
        border-radius: 20px;
    }
    QPushButton:hover{ 
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #10fff1, stop: 1 #022eaf); 
                                    color: white; 
                                    font-weight: bolder; 
                                    border: 5px solid #0cffd8; 
                                    font-size: 20px; 
                                    border-radius: 20px;}
                                ''')
        profile_btn.setFixedSize(200,40)
        profile_btn.clicked.connect(self.open_profile_editor)
        profile_logout_layout.addWidget(profile_btn)

        logout_btn = QPushButton("🔙 Logout")
        logout_btn.setStyleSheet('''QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #edd05c, stop: 1 #ff914d);
        color: black;
        border: white;
        border-radius: 5px;
        font-weight: bold;
        font-size: 20px;
        border-radius: 20px;
    }
        QPushButton:hover{        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #d6a4b0, stop: 1 #1ddb0d); 
                                    font-weight: bolder; 
                                    border: 5px solid #0cffd8; 
                                    font-size: 20px; 
                                    border-radius: 20px;}
    ''')
        logout_btn.setFixedSize(200,40)
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
            item_text = f"📢 {title}\t({timestamp}):\n {summary}"

            # Create QListWidgetItem and store ID
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, notice_id)  # 🔹 Store SQL notice ID in the item
            self.notice_list.addItem(item)
            self.notice_list.setWordWrap(True)

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

    # ✅ Function to set a full-window background image
    def set_background_image(self, image_path):
        if not os.path.exists(image_path):
            print("Error: Image not found! Check the file path.")
            return

        bg_image = QPixmap(image_path)
        if bg_image.isNull():
            print("Error: Image not loaded. Check the file format or path.")
        else:
            self.background_label.setPixmap(bg_image.scaled(
                self.width(), self.height(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
            ))
            self.background_label.setGeometry(0,0, self.width(), self.height())
    
    # ✅ Dynamically update background image on window resize
    def resizeEvent(self, event):
        self.set_background_image(self.bgimgpath)  # Reapply scaling
        super().resizeEvent(event)