from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from profile_page import ProfilePage  
from notice_board import NoticeBoard
from admin_panel import AdminPanel
from auth import LoginPage
from PyQt5.QtGui import QIcon
import sys

class DigitalNoticeBoard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DigiNotice")
        self.setGeometry(300, 300, 800, 600)
        self.showMaximized()

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # ✅ Initially, No User is Logged in
        self.logged_in_user_id = None  
        self.logged_in_user_name = None  

        # ✅ Create Login Page
        self.login_page = LoginPage(self)
        self.stack.addWidget(self.login_page)
        self.stack.setCurrentWidget(self.login_page)  # Start at login page

        
    def print_stack_widgets(self):
        """Print all widgets currently in QStackedWidget for debugging."""
        print("\n🔹 Widgets in QStackedWidget:")
        for i in range(self.stack.count()):
            widget = self.stack.widget(i)
            print(f"   - Widget {i}: {widget}")
        print("\n")

    def login_success(self, unique_id, name):
        """Called after a successful login. Initializes user-specific pages."""
        self.logged_in_user_id = unique_id  
        self.logged_in_user_name = name  

        print(f"✅ Login Success! User: {name} (ID: {unique_id})")
        self.profile_page = ProfilePage(self, unique_id)

        # ✅ Add Profile page to stack
        self.stack.addWidget(self.profile_page)
        
        self.notice_board_page = NoticeBoard(self, unique_id)
        self.stack.addWidget(self.notice_board_page)

        # ✅ Redirect to appropriate page
        if unique_id == "0001":  
            self.admin_panel_page = AdminPanel(self)  # ✅ Create admin panel
            self.stack.addWidget(self.admin_panel_page)
            self.stack.setCurrentWidget(self.admin_panel_page)  # Redirect to admin panel
        else:
            # ✅ Add & Create user-specific pages dynamically

            self.stack.setCurrentWidget(self.notice_board_page) 


    def logout(self):
        
        """Handle logout and return to login page."""
        self.logged_in_user_id = None
        self.logged_in_user_name = None

        print("🚪 Logged out successfully!")

        self.stack.setCurrentWidget(self.login_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DigitalNoticeBoard()
    icon = QIcon("assets\icon_file\icon.jpg")
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec_())
