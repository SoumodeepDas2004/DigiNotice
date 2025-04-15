from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFrame,QHBoxLayout
from database import Database
import hashlib
import re
import os
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from utils import is_valid_password,register_user,login_user,get_all_users,delete_user

# 🔹 Login Page UI (QWidget for StackedWidget)
class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setWindowTitle("Login Page")
        self.setGeometry(400,500,900,600)
        self.background_label = QLabel(self)
        self.bgimgpath = "assets/bgpics/bglogin.jpg"
        self.set_background_image(self.bgimgpath)

        self.login_frame = QFrame(self)
        self.login_frame.setStyleSheet("""
    QFrame{
        background-color: rgba(0, 0, 0, 170);  
        border-radius: 10px;  
        border: 4px solid rgba(0, 140, 255, 0.8); 
        
    }
""")
        self.login_frame.setGeometry(700, 250, 500, 500)

        layout = QVBoxLayout()
         
        self.wlabel = QLabel("Welcome")
        self.wlabel.setStyleSheet("color: white; background-color: transparent; font-weight: bold; border: 0px solid rgba(0, 140, 255, 0.8);")
        self.wlabel.setFont(QFont("Comic Sans MS", 30,italic=True))
        self.wlabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.wlabel)

        self.label = QLabel("Enter Your Unique ID & Password")
        self.label.setFixedSize(470, 50)
        self.label.setStyleSheet("color: white; font-weight: bold; border: 0px solid rgba(0, 140, 255, 0.8);")
        self.label.setFont(QFont("Arial", 10))
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        self.unique_id_input = QLineEdit()
        self.unique_id_input.setPlaceholderText("Unique ID (4-digit)")
        self.unique_id_input.setStyleSheet("background-color: white; border-radius: 5px;")
        self.unique_id_input.setFixedSize( 475, 30)
        layout.addWidget(self.unique_id_input)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name(Compulsory for registration)")
        self.name_input.setStyleSheet("background-color: white; border-radius: 5px;")
        self.name_input.setFixedSize( 475, 30)
        layout.addWidget(self.name_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setStyleSheet("background-color: white; border-radius: 5px;")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedSize( 475, 30)
        layout.addWidget(self.password_input)
        
        login_btn_hbox=QHBoxLayout()
        login_btn = QPushButton("Login")
        login_btn.setFont(QFont("Arial", 10))
        login_btn.setStyleSheet('''QPushButton{background-color: #008CBA; color: white; border-radius: 5px; padding: 5px;}                        
                                QPushButton:hover{background-color: #00598A; color: white; font-weight: bold; border: 2px solid #02f707;}''')
        login_btn.setFixedSize(80,40)
        login_btn.clicked.connect(self.login)
        login_btn_hbox.addWidget(login_btn)
        layout.addLayout(login_btn_hbox)
        
        register_btn_hbox=QHBoxLayout()
        register_btn = QPushButton("Register")
        register_btn.setFont(QFont("Arial", 10))
        register_btn.setStyleSheet('''QPushButton{background-color: #4CAF50; color: white; border-radius: 5px; padding: 5px; }
                                    QPushButton:hover{background-color: #127f1b; color: white; font-weight: bold; border: 2px solid #05a6eb;}''')
        register_btn.setFixedSize(80,40)
        register_btn.clicked.connect(self.register)
        register_btn_hbox.addWidget(register_btn)
        layout.addLayout(register_btn_hbox)
        self.login_frame.setLayout(layout)

    def login(self):
        unique_id = self.unique_id_input.text()
        password = self.password_input.text()
        
        print(f"🔍 Attempting login with ID: {unique_id}")  # Debugging statement

        if unique_id.isdigit() and len(unique_id) == 4:
            user_data = login_user(unique_id, password)  # ✅ Now gets user details
            
            print(f"🟢 login_user() returned: {user_data}")  # Debugging statement
            
            if user_data:
                self.main_window.login_success(user_data[0], user_data[1])  # ✅ Call login_success()
            else:
                self.label.setText("❌ Invalid Credentials!")
                print("❌ Login failed!")
        else:
            self.label.setText("❌ Unique ID must be 4 digits!")


    def register(self):
        unique_id = self.unique_id_input.text()
        name = self.name_input.text()
        password = self.password_input.text()
        
        if not name:
            self.label.setText("❌ Name cannot be empty!")
            return
        
        if unique_id.isdigit() and len(unique_id) == 4:
            message = register_user(unique_id, name, password)  # ✅ Get success/error message
            self.label.setText(message)  # ✅ Show the message in the UI
        else:
            self.label.setText("❌ Unique ID(4 Integer digits) must be given!")
        return 

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
