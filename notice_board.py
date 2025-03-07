from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer,QDateTime
from notice_manager import get_latest_notices, get_summarized_notices

class NoticeBoard(QWidget):
    def _init_(self, main_window):
        super()._init_()
        self.main_window = main_window
        layout = QVBoxLayout()

        self.title = QLabel("📢 Digital Notice Board")
        layout.addWidget(self.title)

        # *Main Notices (Latest 3)*
        self.notice_labels = [QLabel() for _ in range(3)]
        for label in self.notice_labels:
            layout.addWidget(label)

        # *Summarized Notices (Latest 5 - Changing Every 4 Seconds)*
        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)

        # Button to go back to Login Page
        self.back_button = QPushButton("Logout")
        self.back_button.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.login_page))
        layout.addWidget(self.back_button)

        self.refresh_notices()

        # Timer for Summarized Notices
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_summary)
        self.timer.start(4000)  # Change every 4 seconds
        self.summary_index = 0

        self.setLayout(layout)

    def refresh_notices(self):
        latest_notices = get_latest_notices(3)
        for i, notice in enumerate(latest_notices):
            self.notice_labels[i].setText(f"{notice[0]}: {notice[1]}")

        self.summarized_notices = get_summarized_notices(5)
        if self.summarized_notices:
            self.summary_label.setText(self.summarized_notices[0])

    def update_summary(self):
        if self.summarized_notices:
            self.summary_index = (self.summary_index + 1) % len(self.summarized_notices)
            self.summary_label.setText(self.summarized_notices[self.summary_index])