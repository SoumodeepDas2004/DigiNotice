from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, 
    QListWidget, QLineEdit, QListWidgetItem, QComboBox, QTextEdit, QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from utils import add_notice, get_all_notices, delete_notice, print_all_notices
from utils import get_all_users, delete_user, summarize_text, validate_category
from utils import summarize_file
from trainBot_ui import TrainBotUI
import os
from utils import clear_layout  # if not already imported
import shutil
import time  
from cloudinary_config import cloudinary
from database import Database
db = Database()

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
            self.title.setFixedSize(300, 80)
            self.title.setAlignment(Qt.AlignCenter)
            self.title.setStyleSheet("""
                QLabel {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #045e28, stop: 1 #17bb2c);
                    color: white;
                    font-size: 25px;
                    font-weight: bold;
                }
            """)

            # 🔹 Admin Profile Picture
            self.profile_pic_label = QLabel()
            self.profile_pic_label.setFixedSize(50, 50)
            self.profile_pic_label.setScaledContents(True)
            self.profile_pic_label.setStyleSheet("border-radius: 25px; border: 4px solid black;")

            # 🔹 Load admin profile pic from DB (Cloudinary URL)
            self.load_user_data("0001")  # 👈 Ensure this user exists in DB

            # 🔹 Assemble layout
            header_layout.addWidget(self.title)
            header_layout.addStretch()
            header_layout.addWidget(self.profile_pic_label)

            self.layout.addLayout(header_layout)
        
        
    def set_default_profile_picture(self):
        """Fallback profile picture if loading fails."""
        self.profile_pic_label.setPixmap(QPixmap("profile_pics/default.jpg").scaled(
            50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
   
        
        
        
        
    def load_user_data(self, unique_id):
        """Loads user name and profile picture from DB."""
        self.unique_id = unique_id  # Store for future use

        query = "SELECT name, profile_pic_path FROM users WHERE unique_id = %s"
        user = db.fetch_data(query, (unique_id,))
        
        if user:
            name, profile_pic_url = user[0]
            if profile_pic_url:
                self.set_profile_picture_from_url(profile_pic_url)
            else:
                self.set_default_profile_picture()
        else:
            print("❌ Admin user not found in database.")
            self.set_default_profile_picture()
            
    def set_profile_picture_from_url(self, url):
        """Sets profile picture from a Cloudinary URL."""
        from urllib.request import urlopen
        from PyQt5.QtGui import QImage

        try:
            image_data = urlopen(url).read()
            image = QImage()
            image.loadFromData(image_data)
            pixmap = QPixmap(image)
            self.profile_pic_label.setPixmap(pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            print(f"❌ Error loading image from URL: {e}")
            self.set_default_profile_picture()


    # ================== 🔹 NOTICE MANAGEMENT SECTION ==================
    def setup_notice_management(self):
        """Setup UI components for notice management."""
        
        self.notice_label = QLabel("📜 Notices:")
        self.notice_label.setFixedSize(200,50)
        self.notice_label.setStyleSheet("padding: 5px; border: 1px solid #4CAF50; border-radius: 7px; font:20px; color: white; font-weight:bold;")
        self.layout.addWidget(self.notice_label)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notice by title...")
        self.search_input.setStyleSheet("padding: 3px; border: 1px solid #4CAF50; border-radius: 7px; font:17px;")
        self.search_input.setFixedSize(1400,50)
        search_button = QPushButton("🔍 Search")
        search_button.clicked.connect(self.perform_search)
        search_button.setFixedSize(200, 40)
        search_button.setStyleSheet("border-radius:5px")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)

        self.layout.addLayout(search_layout)
        # 🔹 List of Notices
        self.notice_list = QListWidget()
        self.notice_list.setFixedSize(1900, 300)
        self.notice_list.setStyleSheet( """
                                QListWidget{background-color: rgba(0,0,0,150); color: #dbbc09; font-weight: bold; border: 2px solid #02f707; border-radius: 10px; font-size: 20px; padding :5px;} 
                                QListWidget::item{padding: 2px; border: 1px solid red; margin: 3px;}
                                        """)
        self.layout.addWidget(self.notice_list)
        self.refresh_notices()

        # 🔹 Upload Notice Section
        notice_upload_layout = QHBoxLayout()

        self.Nnoticename = QLineEdit()
        self.Nnoticename.setAlignment(Qt.AlignCenter)
        self.Nnoticename.setPlaceholderText("Enter Notice Name")
        self.Nnoticename.setFixedSize(650,50)
        self.Nnoticename.setStyleSheet('''QLineEdit{background-color: rgba(0,0,0,150); color: rgba(70, 229, 208, 1); border: 2px solid yellow; font-size: 16px;}
                            ''')

        
        upload_btn = QPushButton("📤 Upload Notice")
        upload_btn.setFixedSize(200,36)
        upload_btn.setStyleSheet("QPushButton{font-weight: bold; border: 2px solid #02f707; border-radius:15px;}")
        upload_btn.clicked.connect(self.upload_notice)

        # Category Dropdown (Add this before Upload Button)
        self.category_dropdown = QComboBox()
        self.category_dropdown.setFixedSize(200,40)
        self.category_dropdown.addItem("All")
        self.category_dropdown.addItems(["Academics", "Events", "Exams", "Circulars", "Deadlines"])
        
        self.notice_upload_label = QLabel("Notice Name:")
        self.notice_upload_label.setFixedSize(190,35)
        self.notice_upload_label.setAlignment(Qt.AlignCenter)
        self.notice_upload_label.setStyleSheet("QLabel{color: black; font-size: 18px; font-weight: bold; background-color: rgba(26, 228, 19, 0.61); border-radius: 10px; padding: 5px;}")
        notice_upload_layout.addWidget(self.notice_upload_label)
        notice_upload_layout.addWidget(self.Nnoticename)
        notice_upload_layout.addWidget(upload_btn)
        notice_upload_layout.addWidget(self.category_dropdown)

        self.layout.addLayout(notice_upload_layout)

        # 🔹 Delete Notice Button
        self.delete_notice_layout = QHBoxLayout()
        delete_notice_btn = QPushButton("❌ Delete Selected Notice")
        delete_notice_btn.setFixedSize(800,45)
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
        self.user_list.setFixedSize(1900,150)
        self.user_list.setSelectionMode(QListWidget.SingleSelection)
        self.user_list.setFocusPolicy(Qt.StrongFocus)
        self.user_list.setStyleSheet(   """
                                        QListWidget{background-color: rgba(0,0,0,150); color: yellow; font-weight:bold ; border:2px solid #02f707 ; border-radius: 10px;display: flex;align-items: center;}
                                        QListWidget::item{padding: 2px; border: 1px solid red; margin: 3px; display: flex;align-items: center; }
                                        QListWidget::item:selected {background-color: #00ff88;color: black;}
                                        """)
        
        self.layout.addWidget(self.user_list)
        self.refresh_users()

        # 🔹 Delete User Button
        self.delete_user_layout = QHBoxLayout()
        delete_user_btn = QPushButton("❌ Delete Selected User")
        delete_user_btn.setFixedSize(800,45)
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
        color: black;
        border: #7ed957;
        border-radius: 5px;
        font-weight: bold;
        font-size: 20px;
        border:2px solid #ff0000 ;
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
        border:2px solid #ff0000 ;
        border-radius: 20px;
    }
        QPushButton:hover{        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #d6a4b0, stop: 1 #1ddb0d); 
                                    font-weight: bolder; 
                                    color: white;
                                    border: 5px solid #0cffd8; 
                                    font-size: 20px; 
                                    border:2px solid #00ff40	 ;
                                    border-radius: 20px;}
    ''')
        logout_btn.setFixedSize(200,40)
        logout_btn.clicked.connect(self.logout)
        profile_logout_layout.addWidget(logout_btn)

        train_bot_button = QPushButton("🧠 Train DigiBot")
        train_bot_button.setStyleSheet('''QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #22C398, stop: 1 #FD7D2D);
        color: black;
        border: white;
        border-radius: 5px;
        font-weight: bold;
        font-size: 20px;
        border:2px solid #ff0000 ;
        border-radius: 20px;
    }
        QPushButton:hover{        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #54991C, stop: 1 #801B59); 
                                    font-weight: bolder; 
                                    color: white;
                                    border: 5px solid #0cffd8; 
                                    font-size: 20px; 
                                    border:2px solid #00ff40	 ;
                                    border-radius: 20px;}
    ''')
        train_bot_button.setFixedSize(200, 40)
        train_bot_button.clicked.connect(self.open_train_bot)
        profile_logout_layout.addWidget(train_bot_button)

        self.layout.addLayout(profile_logout_layout)

    # ================== 🔹 NOTICE MANAGEMENT FUNCTIONS ==================
    def upload_notice(self):
        """Handles the process of uploading a new notice."""
        Noticename = self.Nnoticename.text().strip()

        if not Noticename:
            QMessageBox.warning(self, "Missing Title", "❌ Please enter a notice title before uploading.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Notice", "", "PDF Files (*.pdf);;Image Files (*.png *.jpg *.jpeg)")

        if file_path:
              # 🔹 Create destination folder if not exists
            os.makedirs("noticesdata", exist_ok=True)

            # 🔹 Create safe and unique file name
            safe_title = "_".join(Noticename.lower().split())
            timestamp = str(int(time.time()))
            ext = os.path.splitext(file_path)[1]
            new_filename = f"{safe_title}_{timestamp}{ext}"
            new_path = os.path.join("noticesdata", new_filename)

            try:
                shutil.copy(file_path, new_path)
            except Exception as e:
                QMessageBox.critical(self, "Copy Failed", f"❌ Error copying file:\n{e}")
                return

            category = self.category_dropdown.currentText()
            summary = summarize_file(file_path)
            # ✅ Convert to relative path before saving
            relative_path = os.path.relpath(new_path).replace("\\", "/")
            add_notice(Noticename, "Content extracted from file", summary, relative_path, category)
            self.refresh_notices()
            QMessageBox.information(self, "Success", "✅ Notice uploaded successfully!")

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
        n=1
        for notice in notices:
            notice_id, title, summary, timestamp, file_path = notice
            item_text = f"{n}📢: {title}\t({timestamp}):\n {summary}"
            n+=1
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
        self.user_list.setItemAlignment(Qt.AlignHCenter)

    def delete_selected_user(self):
        """Deletes the selected user from the database with confirmation."""
        selected_item = self.user_list.currentItem()

        if not selected_item:
            QMessageBox.warning(self, "No User Selected", "❌ Please select a user to delete.")
            return
        print("✔️ Selected:", selected_item.text())  # ✅ See if it prints

        # Extract unique ID from format "unique_id - name"
        unique_id = selected_item.text().split(" - ")[0].strip()

        confirm = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete user '{unique_id}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                delete_user(unique_id)  # Call your utils.py function
                QMessageBox.information(self, "Deleted", f"✅ User '{unique_id}' deleted successfully.")
                self.refresh_users()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Failed to delete user:\n{e}")


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

    # Method for trainBot
    def open_train_bot(self):
        self.train_bot_ui = TrainBotUI()
        self.train_bot_ui.show()
    

    def select_file(self):
        """Open a file dialog to select a file."""
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(self, "Select a file")
        if file_path:
            self.file_path = file_path  # Store the selected file path
            print(f"File selected: {file_path}")
    
    def add_notice(self):
        """Handle adding a new notice to the database."""
        category = self.category_dropdown.currentText()
        if not validate_category(category):
            QMessageBox.warning(self, "Invalid Category", f"'{category}' is not a valid category.")
            return

        title = self.title_input.text()
        content = self.content_input.toPlainText()
        file_path = self.file_path if hasattr(self, 'file_path') else None
        summary = summarize_text(content)

        try:
            add_notice(title, content, summary, file_path, category)
            QMessageBox.information(self, "Success", "Notice added successfully.")
             # ✅ DEBUG: Print all notices to verify category is saved
            print_all_notices()
            self.title_input.clear()
            self.content_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add notice: {e}")
    def perform_search(self):
        query = self.search_input.text().strip().lower()
        query_words = query.split()

        self.notice_list.clear()

        if not query_words:
            self.refresh_notices()
            return

        all_notices = get_all_notices()
        matched_notices = []

        for notice_id, title, summary, created_at, file_path in all_notices:
            title_words = title.lower().split()
            common_words = set(query_words) & set(title_words)
            match_percent = (len(common_words) / len(query_words)) * 100

            if match_percent >= 75:
                item_text = f"📢 {title} - {summary} ({created_at})"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, notice_id)
                matched_notices.append(item)

        if matched_notices:
            for item in matched_notices:
                self.notice_list.addItem(item)
        else:
            no_result_item = QListWidgetItem("❌ No matching notices found.")
            no_result_item.setFlags(Qt.NoItemFlags)
            self.notice_list.addItem(no_result_item)
