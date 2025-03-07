from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer,QDateTime
from notice_manager import get_latest_notices, get_summarized_notices

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from notice_manager import get_latest_notices

class NoticeBoard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        self.label = QLabel("📜 Welcome to the Notice Board")
        layout.addWidget(self.label)

        self.notice_labels = []  # ✅ List to store notice labels
        for _ in range(3):  # ✅ Show latest 3 notices
            notice_label = QLabel("")
            layout.addWidget(notice_label)
            self.notice_labels.append(notice_label)

        back_btn = QPushButton("🔙 Logout")
        back_btn.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.login_page))
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def refresh_notices(self):
        """Fetch and display the latest notices."""
        print("🔄 Refreshing Notices...")  # Debugging print

        latest_notices = get_latest_notices(3)
        print("🔍 Notices Fetched:", latest_notices)  # Debugging print

        for i, notice in enumerate(latest_notices):
            
            self.notice_labels[i].setText(f"📢 {notice[0]}: {notice[1]}")  # ✅ Show Title & Content

    def showEvent(self, event):
        """Refresh notices every time the page is loaded."""
        print("🟢 Notice Board Loaded!")
        self.refresh_notices()
