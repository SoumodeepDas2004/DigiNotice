from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from notice_manager import get_latest_notices, get_summarized_notices
from PyQt5.QtCore import QTimer,QDateTime
class NoticeBoard(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        self.title = QLabel("📢 Digital Notice Board")
        layout.addWidget(self.title)

        self.notice_labels = [QLabel() for _ in range(3)]
        for label in self.notice_labels:
            layout.addWidget(label)

        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)

        self.back_button = QPushButton("Logout")
        self.back_button.clicked.connect(lambda: self.main_window.stack.setCurrentWidget(self.main_window.login_page))
        layout.addWidget(self.back_button)

        self.refresh_notices()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_summary)
        self.timer.start(4000)
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
