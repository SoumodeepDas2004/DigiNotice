from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
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

        self.stack.addWidget(self.login_page)
        self.stack.addWidget(self.notice_board_page)
        self.stack.addWidget(self.admin_panel_page)

        self.stack.setCurrentWidget(self.login_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DigitalNoticeBoard()
    window.show()
    sys.exit(app.exec_())
