import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, 
    QHBoxLayout, QScrollArea, QTextEdit, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from utils import get_latest_notices, get_summarized_notices
from database import Database
from profile_page import ProfilePage
from digiBot_ui import DigiBot

db = Database()

class NoticeBoard(QWidget):
    def __init__(self, main_window, uniqueid=None):
        super().__init__()
      
        self.main_window = main_window
        self.uniqueid = uniqueid  
        self.profile_pic_path = "profile_pics/default.jpg"  
        
        # 🔹 Main Layout
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)  
        # 🔹 UI Sections
        
        self.background_label = QLabel(self)
        self.bgimgpath = "assets/bgpics/bgnoticeboardLight.jpg"
        self.set_background_image(self.bgimgpath)
        
        self.setup_header_section()  # ✅ Profile, Edit Button

        self.setup_notice_section()  # ✅ Scrollable Notice List
        self.setup_summary_section() # ✅ Auto-Rotating Summary (Now with Fade Effect)

        # 🔹 Set Default Theme (Light Mode)
        self.apply_light_theme()

    # ================== 🔹 HEADER SECTION ==================
    def setup_header_section(self):
        """Set up the header with profile picture, edit button, theme toggle, and title."""
        header_layout = QHBoxLayout()

        # 🔹 Profile Picture (Rounded)
        self.profile_pic_label = QLabel(self)
        self.profile_pic_label.setFixedSize(60, 60)
        self.profile_pic_label.setScaledContents(True)
        self.profile_pic_label.setStyleSheet("border-radius: 25px; border: 4px solid #4CAF50;")
        self.load_profile_picture()

                # 🔹 Edit Profile Button
        self.edit_profile_btn = QPushButton("Edit Profile")
        self.edit_profile_btn.setFixedSize(180, 35)
        self.edit_profile_btn.clicked.connect(self.open_edit_profile)

        # 🔹 Theme Toggle Button
        self.theme_toggle_btn = QPushButton("🌙 Dark Mode")
        self.theme_toggle_btn.setFixedSize(180, 35)
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)

        # ✅ Apply button styles AFTER the theme button exists
        self.edit_profile_btn.setStyleSheet(self.get_button_style())
        self.theme_toggle_btn.setStyleSheet(self.get_button_style())

        """Set up a logout button."""
        self.logout_btn = QPushButton("🔙 Logout")
        self.logout_btn.setFixedSize(180, 35)
        self.logout_btn.clicked.connect(self.main_window.logout)

        # ✅ Set up a Help / Support button
        self.help_btn = QPushButton("❓Help")
        self.help_btn.setStyleSheet('''QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #cdffd8, stop: 1 #8aadf1);
        color: black;
        font-size: 20px;
        font-weight: normal;
        border: 2px solid #02f707; 
        border-radius: 15px;
    }
        QPushButton:hover{background-color: #00598A; color: white; font-weight: bold; border: 2px solid #02f707; font-size: 20px; border-radius: 15px;}
        ''')
        self.help_btn.setFixedSize(180, 35)
        self.help_btn.clicked.connect(self.show_digibot)
        

        # 🔹 Notice Board Title
        self.title_label = QLabel("Notice Board")
        self.title_label.setFont(QFont("Canva Sans",30,italic=True))
        self.title_label.setFixedSize(400,80)
        self.title_label.setAlignment(Qt.AlignCenter)
        

        # 🔹 Arrange Items in Layout
        header_layout.addWidget(self.profile_pic_label)
        header_layout.addWidget(self.edit_profile_btn)
        header_layout.addWidget(self.theme_toggle_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.help_btn)
        header_layout.addWidget(self.logout_btn)
        header_layout.addWidget(self.title_label)

        self.layout.addLayout(header_layout)
    #edit profile func
    def open_edit_profile(self):
        """Opens the Profile Page if a user is logged in."""
        if not self.main_window.logged_in_user_id:
            QMessageBox.warning(self, "Error", "❌ No user logged in!")
            return

        # ✅ Ensure Profile Page is created
        if not hasattr(self.main_window, "profile_page"):
            print("⚠️ Profile Page is None! Creating it now...")
            self.main_window.profile_page = ProfilePage(self.main_window)
            self.main_window.stack.addWidget(self.main_window.profile_page)

        print(f"✅ Opening Profile Page for User: {self.main_window.logged_in_user_id}")
        self.main_window.profile_page.load_user_data(self.main_window.logged_in_user_id)
        self.main_window.stack.setCurrentWidget(self.main_window.profile_page)
    # ================== 🔹 LOAD PROFILE PICTURE ==================
    def load_profile_picture(self):
        """Load and refresh the user's profile picture."""
        query = "SELECT profile_pic_path FROM users WHERE unique_id = %s"
        result = db.fetch_data(query, (self.uniqueid,))

        if result and result[0][0]:  
            self.profile_pic_path = result[0][0]  
        else:
            self.profile_pic_path = "profile_pics/default.jpg"  
        
        if os.path.exists(self.profile_pic_path):
            pixmap = QPixmap(self.profile_pic_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.profile_pic_label.setPixmap(pixmap)
        else:
            self.profile_pic_label.setPixmap(QPixmap("profile_pics/default.jpg"))  

    # ================== 🔹 NOTICE DISPLAY SECTION ==================
    def setup_notice_section(self):
        """Set up the section where notices are displayed."""
        
        
        self.notice_scroll = QHBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.notice_container = QWidget()
        self.notice_layout = QVBoxLayout()
        
        
        self.nLabelHLAY=QHBoxLayout()
        self.nLabel=QLabel("NOTICES")
        self.nLabel.setFixedSize(180,60)
        self.nLabel.setFont(QFont("Arial", 40))
        self.nLabel.setAlignment(Qt.AlignCenter)
        self.nLabelHLAY.setAlignment(Qt.AlignCenter)
        
        
        self.nLabelHLAY.addWidget(self.nLabel)
        self.notice_layout.addLayout(self.nLabelHLAY)

        self.notice_container.setLayout(self.notice_layout)
        self.scroll_area.setWidget(self.notice_container)
        self.scroll_area.setFixedSize(1600,700)
        self.scroll_area.setAlignment(Qt.AlignHCenter )
        self.notice_scroll.addWidget(self.scroll_area)
        self.layout.addLayout(self.notice_scroll)
        self.refresh_notices()

    # ================== 🔹 AUTO-ROTATING SUMMARY SECTION (FADE EFFECT) ==================
    def setup_summary_section(self):
        """Set up the auto-rotating summary display with a fade effect."""
        self.summary_container = QHBoxLayout()
        self.summary_display = QTextEdit()
        self.summary_display.setReadOnly(True)
        self.summary_display.setFixedSize(1700,200)
        self.summary_display.setStyleSheet("QTextEdit{ padding:3px;  }")
        self.summary_display.setAlignment(Qt.AlignCenter)
        self.summary_container.setAlignment(Qt.AlignCenter)
        self.summary_container.addWidget(self.summary_display)
        self.layout.addLayout(self.summary_container)

        # ✅ Add Fade Effect Properly
        self.fade_effect = QGraphicsOpacityEffect()
        self.summary_display.setGraphicsEffect(self.fade_effect)
        self.fade_effect.setOpacity(1.0)  # ✅ Ensure it's fully visible initially

        # ✅ Timer for auto-rotation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fade_out_summary)
        self.timer.start(5000)  # Change summary every 5 sec

        # ✅ Fetch summaries
        self.load_summaries()

    # ================== 🔹 REFRESH NOTICES ==================
    def refresh_notices(self):
        """Fetch and display the latest notices."""
        latest_notices = get_latest_notices(3)

        for i in reversed(range(self.notice_layout.count())):
            item = self.notice_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
        n=1
        for title, content, file_path, notice_time in latest_notices:
            notice_label = QLabel(f"{n}<b>📃: {title}</b> at ({notice_time})\n{content}")
            notice_label.setAlignment(Qt.AlignLeft)
            notice_label.setWordWrap(True)
            self.notice_level_container = QHBoxLayout()
            notice_label.setFixedWidth(1300)
            self.notice_level_container.addWidget(notice_label)
            self.notice_layout.addLayout(self.notice_level_container)
            
            n+=1

            if file_path and os.path.exists(file_path):  
                download_btn = QPushButton("⬇️ Download")
                self.download_btn_container = QHBoxLayout()
                download_btn.setFixedSize(180, 35)
                download_btn.clicked.connect(lambda checked, path=file_path: self.download_file(path))
                self.download_btn_container.addWidget(download_btn)
                self.notice_layout.addLayout(self.download_btn_container)
            self.notice_layout.setContentsMargins(1,1,1,2)
            self.notice_layout.setSpacing(1)
            
    def download_file(self, file_path):
        """Opens the file location to let the user download it."""
        if os.path.exists(file_path):
            try:
                os.startfile(file_path)  # ✅ Open in default application
            except Exception as e:
                QMessageBox.warning(self, "Error", f"❌ Cannot open file: {e}")
        else:
            QMessageBox.warning(self, "Error", "❌ File not found!")

    # ================== 🔹 LOAD & LOOP SUMMARIES ==================
    def load_summaries(self):
        """Fetch latest summaries and start rotating them in a loop."""
        self.summaries = get_summarized_notices(5)
        self.current_summary_index = 0

        if self.summaries:
            self.summary_display.setText(self.summaries[self.current_summary_index])

    # ================== 🔹 FADE OUT SUMMARY ==================
    def fade_out_summary(self):
        """Fade out effect before changing the summary."""
        self.animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.animation.setDuration(300)  
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.change_summary_text)
        self.animation.start()

    # ================== 🔹 CHANGE SUMMARY TEXT & LOOP ==================

    # --slide_out_summary effect commented--
    '''def slide_out_summary(self):
        """Slide out text effect before changing the summary."""
        self.animation = QPropertyAnimation(self.summary_display, b"pos")
        self.animation.setDuration(500)  # Smooth slide-out
        self.animation.setStartValue(self.summary_display.pos())  # Start position
        self.animation.setEndValue(self.summary_display.pos() + QPoint(-self.summary_display.width(), 0))  # Move left

        self.animation.finished.connect(self.change_summary_text)  # Call after animation
        self.animation.start()'''

    '''def change_summary_text(self):
        """Update the summary text and slide it back in."""
        self.current_summary_index = (self.current_summary_index + 1) % len(self.summaries)  
        self.summary_display.setText(self.summaries[self.current_summary_index])

        self.animation = QPropertyAnimation(self.summary_display, b"pos")
        self.animation.setDuration(500)  # Smooth slide-in
        self.animation.setStartValue(self.summary_display.pos() + QPoint(self.summary_display.width(), 0))  # Start from right
        self.animation.setEndValue(self.summary_display.pos())  # Move back to original position

        self.animation.start()'''

    def change_summary_text(self):
        """Update the summary and fade it back in smoothly in a loop."""
        self.current_summary_index = (self.current_summary_index + 1) % len(self.summaries)  
        self.summary_display.setText(self.summaries[self.current_summary_index])

        self.animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.animation.setDuration(900)  
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
    # ================== 🔹 THEME TOGGLE FUNCTION ==================
    def get_button_style(self):
        """Returns button styles based on the current theme."""
        if self.theme_toggle_btn.text() == "🌙 Dark Mode":
            
            self.theme_toggle_btn.setText("☀️ Light Mode")
            return """
        QPushButton{
        background-color: black;
        color: white;
        font-size: 20px;
        font-weight: normal;
        border: 2px solid #02f707; 
        border-radius: 15px;
    }
        QPushButton:hover{background-color:#085b4c; color: white; font-weight: bold; 
        border: 2px solid #7FFF00 ; font-size: 20px; border-radius: 15px;} 
        """
        else:
            self.theme_toggle_btn.setText("🌙 Dark Mode")
            return    """ 
        QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #cdffd8, stop: 1 #8aadf1);
        color: black;
        font-size: 20px;
        font-weight: normal;
        border: 2px solid #02f707; 
        border-radius: 15px;
    }
        QPushButton:hover{background-color: #00598A; color: white; font-weight: bold; border: 2px solid #02f707; font-size: 20px; border-radius: 15px;}
        """            
        
    def toggle_theme(self):
        """Toggles between Light and Dark themes and updates button styles."""
        if self.theme_toggle_btn.text() == "🌙 Dark Mode":
            self.apply_dark_theme()
            self.theme_toggle_btn.setText("☀️ Light Mode")
            self.bgimgpath = "assets/bgpics/bgnoticeboardDark.jpg"
            self.set_background_image(self.bgimgpath)

        else:
            self.apply_light_theme()
            self.theme_toggle_btn.setText("🌙 Dark Mode")
            self.bgimgpath = "assets/bgpics/bgnoticeboardLight.jpg"
            self.set_background_image(self.bgimgpath)

        # ✅ Update button styles dynamically
        """self.edit_profile_btn.setStyleSheet(self.get_button_style())
           self.theme_toggle_btn.setStyleSheet(self.get_button_style())"""
        # ================== 🔹 APPLY DARK THEME ==================
    def apply_dark_theme(self):
        """Applies the Dark Theme to the Notice Board."""
        self.edit_profile_btn.setStyleSheet('''
        QPushButton{
        background-color: black;
        color: white;
        font-size: 20px;
        font-weight: normal;
        border: 2px solid #02f707; 
        border-radius: 15px;
    }
        QPushButton:hover{background-color:#085b4c; color: white; font-weight: bold; border: 2px solid #7FFF00 ; font-size: 20px; border-radius: 15px;}
        ''')

        self.theme_toggle_btn.setStyleSheet('''QPushButton {
        background-color: black;
        color: white;
        font-size: 20px;
        font-weight: normal;
        border: 2px solid #02f707; 
        border-radius: 15px;
                                                            }
        QPushButton:hover{background-color:#085b4c; color: white; font-weight: bold; border: 2px solid #7FFF00 ; font-size: 20px; border-radius: 15px;}
        ''')
        self.logout_btn.setStyleSheet('''QPushButton {
        background-color: black;
        color: white;
        font-size: 20px;
        font-weight: normal;
        border: 2px solid #02f707; 
        border-radius: 15px;
    }
        QPushButton:hover{background-color:#085b4c; color: white; font-weight: bold; border: 2px solid #7FFF00 ; font-size: 20px; border-radius: 15px;}
        ''')
        self.nLabel.setStyleSheet("color: white; font-weight:bold;  ")

        self.notice_container.setStyleSheet('''QWidget {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #000000 , stop: 1 #042201);
        color: white;
        font-size: 20px;
        font-weight: normal;
        border: 2px solid #02f707; 
        border-radius: 15px;}
        QScrollArea{background-color: rgba( 255, 255, 255, 0);}
        QPushButton{background-color: DarkTurquoise; color: black; border: 2px solid red; border-radius: 15px;}
        QPushButton:hover {background-color: red; color: white; border: 2px solid green; border-radius: 15px;}
        ''')
        self.title_label.setStyleSheet(''' QLabel{
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ff0e0e, stop: 1 #5500ff);
        color: white;
        font-weight: bold;
        border: 1px solid #919191; 
        border-radius: 10px;
    }''')
        self.summary_display.setStyleSheet('''                           
    QTextEdit{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #18053d, stop: 1 #085b4c);
                color: white ;
                font-size: 20px;
                font-weight: normal;
                border: 2px solid #02f707; 
                border-radius: 15px;
                width: 300px;
                padding: 25px;
            }''')

    # ================== 🔹 APPLY LIGHT THEME ==================
    def apply_light_theme(self):
        """Applies the Light Theme to the Notice Board."""
        self.edit_profile_btn.setStyleSheet('''QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #cdffd8, stop: 1 #8aadf1);
        color: black;
        font-size: 20px;
        font-weight: normal;
        border: 2px solid #02f707; 
        border-radius: 15px;
    }
        QPushButton:hover{background-color: #00598A; color: white; font-weight: bold; border: 2px solid #02f707; font-size: 20px; border-radius: 15px;}
        ''')

        self.theme_toggle_btn.setStyleSheet('''QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #cdffd8, stop: 1 #8aadf1);
        color: black;
        font-size: 20px;
        font-weight: normal;
        border: 2px solid #02f707; 
        border-radius: 15px;
    }
        QPushButton:hover{background-color: #00598A; color: white; font-weight: bold; border: 2px solid #02f707; font-size: 20px; border-radius: 15px;}
        ''')
        self.logout_btn.setStyleSheet('''QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #cdffd8, stop: 1 #8aadf1);
        color: black;
        font-size: 20px;
        font-weight: normal;
        border: 2px solid #02f707; 
        border-radius: 15px;
    }
        QPushButton:hover{background-color: #00598A; color: white; font-weight: bold; border: 2px solid #02f707; font-size: 20px; border-radius: 15px;}
        ''')
        self.nLabel.setStyleSheet("color: black; font-weight:bold;")
        self.notice_container.setStyleSheet('''QWidget {
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #fffcff, stop: 1 #f6e93f);
            color: black;
            font-size: 20px;
            font-weight: normal;
            border: 2px solid #02f707; 
            border-radius: 15px;}
            QPushButton{background-color: DarkTurquoise; color: black; border: 2px solid red; border-radius: 15px;}
            QPushButton:hover {background-color: red; color: white; border: 2px solid green; border-radius: 15px;}
            ''')
        self.title_label.setStyleSheet(''' QLabel{
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #ad0808, stop: 1 #290374);
            color: white;
            font-weight: bold;
            border: 2px solid #02f707; 
            border-radius: 10px;
    }''')
        self.summary_display.setStyleSheet('''
                QScrollBar::handle:vertical {
                    background-color: black;
                    min-height: 20px;
                    border-radius: 5px;
                } 
                QTextEdit{
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #73dfda, stop: 1 #ef569b);
                color: black;
                font-size: 20px;
                font-weight: normal;
                border: 2px solid #02f707; 
                border-radius: 15px;
                width: 300px;
                padding: 25px;
            }''')

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

    # ✅ To use the Bot instance created in main.py
    def show_digibot(self):
        self.main_window.chatbot_widget.show()
