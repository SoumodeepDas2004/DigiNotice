import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox, 
    QHBoxLayout, QScrollArea, QTextEdit, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from notice_manager import get_latest_notices, get_summarized_notices
from database import Database
from profile_page import ProfilePage

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
        # 🔹 Set Default Theme (Light Mode)
        self.apply_light_theme()
        
        
        self.setup_header_section()  # ✅ Profile, Edit Button
        self.setup_notice_section()  # ✅ Scrollable Notice List
        self.setup_summary_section() # ✅ Auto-Rotating Summary (Now with Fade Effect)
        self.setup_footer_section()  # ✅ Logout Button

    # ================== 🔹 HEADER SECTION ==================
    def setup_header_section(self):
        """Set up the header with profile picture, edit button, theme toggle, and title."""
        header_layout = QHBoxLayout()

        # 🔹 Profile Picture (Rounded)
        self.profile_pic_label = QLabel(self)
        self.profile_pic_label.setFixedSize(50, 50)
        self.profile_pic_label.setScaledContents(True)
        self.profile_pic_label.setStyleSheet("border-radius: 25px; border: 4px solid #4CAF50;")
        self.load_profile_picture()

                # 🔹 Edit Profile Button
        self.edit_profile_btn = QPushButton("Edit Profile")
        self.edit_profile_btn.setFixedSize(120, 30)
        self.edit_profile_btn.clicked.connect(self.open_edit_profile)

        # 🔹 Theme Toggle Button
        self.theme_toggle_btn = QPushButton("🌙 Dark Mode")
        self.theme_toggle_btn.setFixedSize(120, 30)
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)

        # ✅ Apply button styles AFTER the theme button exists
        self.edit_profile_btn.setStyleSheet(self.get_button_style())
        self.theme_toggle_btn.setStyleSheet(self.get_button_style())



        # 🔹 Notice Board Title
        title_label = QLabel("Notice Board")
        title_label.setFont(QFont('Arial', 15))

        # 🔹 Arrange Items in Layout
        header_layout.addWidget(self.profile_pic_label)
        header_layout.addWidget(self.edit_profile_btn)
        header_layout.addWidget(self.theme_toggle_btn)
        header_layout.addStretch()
        header_layout.addWidget(title_label)

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
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.notice_container = QWidget()
        self.notice_layout = QVBoxLayout()

        self.notice_container.setLayout(self.notice_layout)
        self.scroll_area.setWidget(self.notice_container)
        self.layout.addWidget(self.scroll_area)

        self.refresh_notices()

    # ================== 🔹 AUTO-ROTATING SUMMARY SECTION (FADE EFFECT) ==================
    def setup_summary_section(self):
        """Set up the auto-rotating summary display with a fade effect."""
        self.summary_display = QTextEdit()
        self.summary_display.setReadOnly(True)
        self.summary_display.setFixedHeight(80)
        self.layout.addWidget(self.summary_display)

        # ✅ Add Fade Effect Properly
        self.fade_effect = QGraphicsOpacityEffect()
        self.summary_display.setGraphicsEffect(self.fade_effect)
        self.fade_effect.setOpacity(1.0)  # ✅ Ensure it's fully visible initially

        # ✅ Timer for auto-rotation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.fade_out_summary)
        self.timer.start(3000)  # Change summary every 3 sec

        # ✅ Fetch summaries
        self.load_summaries()

    # ================== 🔹 FOOTER SECTION ==================
    def setup_footer_section(self):
        """Set up the footer with a logout button."""
        logout_btn = QPushButton("🔙 Logout")
        logout_btn.clicked.connect(self.logout)
        self.layout.addWidget(logout_btn)

    # ================== 🔹 REFRESH NOTICES ==================
    def refresh_notices(self):
        """Fetch and display the latest notices."""
        latest_notices = get_latest_notices(3)

        for i in reversed(range(self.notice_layout.count())):
            item = self.notice_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        for title, content, file_path, notice_time in latest_notices:
            notice_label = QLabel(f"<b>{title}</b> at ({notice_time})\n{content}")
            notice_label.setWordWrap(True)
            notice_label.setFixedWidth(500)
            self.notice_layout.addWidget(notice_label)

            if file_path and os.path.exists(file_path):  
                download_btn = QPushButton("⬇️ Download")
                download_btn.clicked.connect(lambda checked, path=file_path: self.download_file(path))
                self.notice_layout.addWidget(download_btn)

    # ================== 🔹 LOGOUT FUNCTION ==================
    def logout(self):
        """Logs out the user and returns to the login page."""
        print(f"🔴 Logging out User ID: {self.main_window.logged_in_user_id}")
        self.main_window.logged_in_user_id = None
        self.main_window.stack.setCurrentWidget(self.main_window.login_page)

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
                QPushButton {
                    background-color: #f0f0f0;
                    color: black;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #ddd;
                }
            """
        else:
            self.theme_toggle_btn.setText("🌙 Dark Mode")
            return """
                Q
                
                QPushButton {
                    background-color: ##020012;
                    color: white;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: ##2c0145;
                }
            """
    def toggle_theme(self):
        """Toggles between Light and Dark themes and updates button styles."""
        if self.theme_toggle_btn.text() == "🌙 Dark Mode":
            self.apply_dark_theme()
            self.theme_toggle_btn.setText("☀️ Light Mode")
        else:
            self.apply_light_theme()
            self.theme_toggle_btn.setText("🌙 Dark Mode")

        # ✅ Update button styles dynamically
        self.edit_profile_btn.setStyleSheet(self.get_button_style())
        self.theme_toggle_btn.setStyleSheet(self.get_button_style())
        # ================== 🔹 APPLY DARK THEME ==================
    def apply_dark_theme(self):
        """Applies the Dark Theme to the Notice Board."""
        self.setStyleSheet("""
            
            QWidget { background-color: #2E2E2E; color: white; }
            QLabel { color: white; }
            QHBoxLayout{background-color:#010f03;  border-radius: 5px;}
            QPushButton { background-color: #030336; color: white; border-radius: 5px; }
            QPushButton:hover { background-color: #440069;  }
            QTextEdit { background-color: #333; color: white; border: 1px solid #777; }
        """)

    # ================== 🔹 APPLY LIGHT THEME ==================
    def apply_light_theme(self):
        """Applies the Light Theme to the Notice Board."""
        self.setStyleSheet("""
            QWidget { background-color: white; color: black; }
            QLabel { color: black; }
            QPushButton { background-color: #f0f0f0; color: black; border-radius: 5px; }
            QPushButton:hover { background-color: #ddd; }
            QTextEdit { background-color: #f8f8f8; color: black; border: 1px solid #ccc; }
        """)
        