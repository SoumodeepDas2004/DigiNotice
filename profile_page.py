import os
import hashlib
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QMessageBox, 
    QHBoxLayout, QFileDialog
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from database import Database
import shutil

#from PyQt5.QtWidgets import QApplication

db = Database()

class ProfilePage(QWidget):
    def __init__(self, parent_window=None, uniqueid=None):  
        super().__init__(parent_window)
        self.main_widget = parent_window  
        self.uniqueid = uniqueid if uniqueid else self.get_logged_in_user_id()

        print(f"🟢 ProfilePage initialized with User ID: {self.uniqueid}")  

        if not self.uniqueid:
            print("⚠️ ERROR: No Unique ID found!")
        # 🔹 Main Layout and UI
        self.background_label = QLabel(self)
        self.bgimgpath = "assets/bgpics/bgEditProfile.jpg"
        self.set_background_image(self.bgimgpath)
        
        
        layout = QVBoxLayout()
        detailsWid=QWidget()
        detailsWid.setFixedSize(self.maximumWidth(), 600)
        
        detailwidlayout=QVBoxLayout()
        #title setup 
        self.title=QLabel("🛡️ Account Control")
        
        self.title.setFixedSize(500,60)
        self.title.setStyleSheet("font-size: 40px; font-weight: bold; color: white; background-color:rgba(13, 127, 255, 0.2); padding: 3px;  border: 3px solid #5ce1e6;border-radius: 10px;}")
        self.title.setAlignment(Qt.AlignCenter)

        self.titleHbox=QHBoxLayout()
        self.titleHbox.setAlignment(Qt.AlignLeft)
        self.titleHbox.addWidget(self.title)
        layout.addLayout(self.titleHbox)
        #givng style to countainer of details
        detailsWid.setStyleSheet("""{
            background-color:black;
            border: 3px solid #ffde59; 
            border-radius: 10px;
            }""") 
        # 🔹 Profile Picture Section
        self.setup_profile_picture_section(detailwidlayout)

        # 🔹 User Info Section (ID, Name, Password)
        self.setup_user_info_section(detailwidlayout)

        # 🔹 Buttons (Update Profile, Back)
        self.setup_buttons(detailwidlayout)
        
        detailsWid.setLayout(detailwidlayout)
        
        layout.addWidget(detailsWid)
        self.setLayout(layout)
    #check Uid
    def get_logged_in_user_id(self):
        if self.main_widget and hasattr(self.main_widget, "logged_in_user_id"):
            return self.main_widget.logged_in_user_id
        return None
    # ================== 🔹 PROFILE PICTURE SECTION ==================
    def setup_profile_picture_section(self, layout):
        

        """Set up the profile picture display and upload button."""
        self.profile_pic_label = QLabel(self)
        self.profile_pic_label.setFixedSize(150, 150)
        self.profile_pic_label.setScaledContents(True)
        self.pfpHbox=QHBoxLayout()
        self.pfpHbox.addWidget(self.profile_pic_label)
        layout.addLayout(self.pfpHbox)
            # upload button  pfp
        self.pfpuploadhbox=QHBoxLayout()
        self.upload_pic_btn = QPushButton("📸 Update Profile Picture")
        self.upload_pic_btn.setStyleSheet(""" QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #8c52ff, stop: 1 #5ce1e6);
        color: black;
        font-size: 20px;
        font-weight: bold;
        border: 2px solid #02f707; 
        border-radius: 15px;
        padding:5px;
                }
        QPushButton:hover{background-color: #00598A; color: white; font-weight: bold; border: 2px solid #02f707; font-size: 25px; border-radius: 15px;}
        """            )
        self.upload_pic_btn.clicked.connect(self.upload_profile_picture)
        self.upload_pic_btn.setFixedSize(320,70)
        self.pfpuploadhbox.addWidget(self.upload_pic_btn)
        layout.addLayout(self.pfpuploadhbox)

    # ================== 🔹 USER INFO SECTION ==================
    def setup_user_info_section(self, layout):
        """Set up the input fields for Unique ID, Name, and Password."""
        self.unique_id_input = QLineEdit()
        self.unique_id_input.setReadOnly(True)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter New Name")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter New Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        self.unique_id_input.setFixedSize(210,40)
        self.unique_id_input.setAlignment(Qt.AlignCenter)

        self.name_input.setFixedSize(210,40)
        self.name_input.setAlignment(Qt.AlignCenter)

        self.password_input.setFixedSize(230,40)
        self.password_input.setAlignment(Qt.AlignCenter)

        
        
        
        # Layout for user info
        user_info_layout = QHBoxLayout()
        # user_info_layout.setAlignment(Qt.AlignCenter)
        user_info_layout.addWidget(self.unique_id_input)
        user_info_layout.addWidget(self.name_input)
        user_info_layout.addWidget(self.password_input)
        self.setStyleSheet("""QLineEdit{
            font-weight:bold;
            font-size:20px;
            border: solid 1px #02f707;
            
            border-radius:10px;
            
            }""")
        
        layout.addLayout(user_info_layout)

    # ================== 🔹 BUTTON SECTION ==================
    def setup_buttons(self, layout):
        """Set up buttons for updating profile and going back."""
        update_btn = QPushButton("Update Profile Details")
        fotbutHbox=QHBoxLayout()
        update_btn.setStyleSheet("""  QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #8c52ff, stop: 1 #5ce1e6);
        color: black;
        font-size: 22px;
        font-weight: bold;
        border: 2px solid #02f707; 
        border-radius: 15px;
    }
        QPushButton:hover{background-color: #00598A; color: white; font-weight: bold; border: 2px solid #02f707; font-size: 25px; border-radius: 15px;}
        """            )
        update_btn.clicked.connect(self.update_profile)

        back_btn = QPushButton("Back")
        back_btn.setStyleSheet("""  QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #8c52ff, stop: 1 #5ce1e6);
        color: black;
        font-size: 22px;
        font-weight: bold;
        border: 2px solid #02f707; 
        border-radius: 15px;
    }
        QPushButton:hover{background-color: #00598A; color: white; font-weight: bold; border: 2px solid #02f707; font-size: 25px; border-radius: 15px;}
        """            )
        back_btn.clicked.connect(self.go_back)
        update_btn.setFixedSize(320,50)
        back_btn.setFixedSize(210,50)
        fotbutHbox.addWidget(update_btn)
        fotbutHbox.addSpacing(15)
        fotbutHbox.addWidget(back_btn)
        layout.addLayout(fotbutHbox)

    # ================== 🔹 PROFILE PICTURE UPLOAD ==================
    def upload_profile_picture(self):
        """Allows the user to upload a profile picture and updates the database."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Profile Picture", "", "Images (*.png *.jpg *.jpeg)")
        
        if file_path:
            unique_id = self.unique_id_input.text().strip()
            if not unique_id:
                QMessageBox.warning(self, "Error", "❌ Unique ID is missing!")
                return
            
            new_path = f"profile_pics/{unique_id}.jpg"  # ✅ Store as user_id.jpg
            os.makedirs("profile_pics", exist_ok=True)
            shutil.copy(file_path, new_path)  # ✅ Save the new profile picture

            # ✅ Update the profile picture path in the database
            query = "UPDATE users SET profile_pic_path = %s WHERE unique_id = %s"
            db.execute_query(query, (new_path, unique_id))
            
            self.profile_pic_path = new_path  # ✅ Store the new path
            self.profile_pic_label.setPixmap(QPixmap(self.profile_pic_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

            QMessageBox.information(self, "Success", "✅ Profile picture updated successfully!")

    # ================== 🔹 LOAD USER DATA ==================
    def load_user_data(self,unique_id):
        """Loads user data into the input fields."""
        #unique_id = self.main_window.logged_in_user_id  # ✅ Get user ID from main.py
        print("✅ Profile Loaded for User:", unique_id)
        
        query = "SELECT name, password, profile_pic_path FROM users WHERE unique_id = %s"
        result = db.fetch_data(query, (unique_id,))

        if result:
            self.unique_id_input.setText(unique_id)
            self.name_input.setText(result[0][0])  # Load name
            self.password_input.setText("")  # Keep password field empty for security
            self.profile_pic_path = result[0][2] or "profile_pics/default.jpg"  # Load profile picture
            self.profile_pic_label.setPixmap(QPixmap(self.profile_pic_path))

    # ================== 🔹 UPDATE PROFILE ==================
    def update_profile(self):
        """Updates the user's profile information securely."""
        unique_id = self.unique_id_input.text()  # ✅ Get user ID from input
        new_name = self.name_input.text()
        new_password = self.password_input.text()

        if new_name and new_password:
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            query = "UPDATE users SET name = %s, password = %s WHERE unique_id = %s"
            db.execute_query(query, (new_name, hashed_password, unique_id))  # ✅ Use the correct user ID

            QMessageBox.information(self, "Success", "✅ Profile Updated Successfully!")
        else:
            QMessageBox.warning(self, "Error", "❌ Fields cannot be empty!")

    # ================== 🔹 GO BACK ==================
    def go_back(self):
        """Redirect the user to the correct page after editing their profile."""
        if hasattr(self.main_widget, "logged_in_user_id"):
            if self.main_widget.logged_in_user_id == "0001":  # ✅ If admin (ID = 0001)
                self.main_widget.stack.setCurrentWidget(self.main_widget.admin_panel_page)
            else:
                self.main_widget.stack.setCurrentWidget(self.main_widget.notice_board_page)
        else:
            print("❌ Error: No user logged in!")
            
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
