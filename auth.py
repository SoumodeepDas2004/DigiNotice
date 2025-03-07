from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
from database import Database

db = Database()

class LoginPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout()

        self.label = QLabel("Enter Unique ID, Name & Password:")
        layout.addWidget(self.label)

        self.unique_id_input = QLineEdit()
        self.unique_id_input.setPlaceholderText("Unique ID (4-digit)")
        layout.addWidget(self.unique_id_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")
        layout.addWidget(self.name_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        self.setLayout(layout)

    def login(self):
        unique_id = self.unique_id_input.text()
        name = self.name_input.text()
        password = self.password_input.text()

        query = "SELECT * FROM users WHERE unique_id = %s AND name = %s AND password = %s"
        result = db.fetch_data(query, (unique_id, name, password))

        if result:
            self.main_window.stack.setCurrentWidget(self.main_window.notice_board_page)
        else:
            self.label.setText("Invalid Credentials!")
