from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from profile_page import ProfilePage  # Import Profile Page
from notice_board import NoticeBoard
from admin_panel import AdminPanel
from auth import LoginPage
import sys

class DigitalNoticeBoard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital Notice Board")
        self.setGeometry(100, 100, 900, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.login_page = LoginPage(self)
        self.notice_board_page = NoticeBoard(self)
        self.admin_panel_page = AdminPanel(self)
        self.profile_page = ProfilePage(self)  # ✅ Add Profile Page

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.notice_board_page)
        self.stack.addWidget(self.admin_panel_page)
        self.stack.addWidget(self.profile_page)  # ✅ Add Profile Page to Stack

        self.stack.setCurrentWidget(self.login_page)  # Start at login page

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DigitalNoticeBoard()
    window.show()
    sys.exit(app.exec_())
