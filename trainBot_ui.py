import json
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox

BRAIN_FILE = "brain.json"
UNKNOWN_FILE = "unknown.txt"

class TrainBotUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 Train DigiBot")
        self.setFixedSize(500, 500)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.question_list = QListWidget()
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Type answer for selected question...")
        self.submit_btn = QPushButton("Add Answer")
        self.submit_btn.clicked.connect(self.save_answer)

        self.layout.addWidget(QLabel("❓ Unknown Questions:"))
        self.layout.addWidget(self.question_list)
        self.layout.addWidget(self.answer_input)
        self.layout.addWidget(self.submit_btn)

        self.load_unknown_questions()
        self.brain = self.load_brain()

    def load_unknown_questions(self):
        if os.path.exists(UNKNOWN_FILE):
            with open(UNKNOWN_FILE, "r") as f:
                lines = list(set([line.strip("()\n").lower() for line in f if line.strip()]))
                self.question_list.addItems(lines)
        else:
            QMessageBox.information(self, "Info", "✅ No unknown questions found.")

    def load_brain(self):
        if os.path.exists(BRAIN_FILE):
            with open(BRAIN_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_brain(self):
        with open(BRAIN_FILE, "w") as f:
            json.dump(self.brain, f, indent=4)

    def save_answer(self):
        selected = self.question_list.currentItem()
        answer = self.answer_input.text().strip()
        if not selected:
            QMessageBox.warning(self, "Error", "Please select a question.")
            return
        if not answer:
            QMessageBox.warning(self, "Error", "Answer cannot be empty.")
            return

        question = selected.text()
        self.brain[question] = answer
        self.save_brain()

        self.question_list.takeItem(self.question_list.currentRow())
        self.answer_input.clear()

        QMessageBox.information(self, "Saved", f"✅ Learned answer for:\n\n{question}")

        if self.question_list.count() == 0:
            self.clear_unknown_file()
            QMessageBox.information(self, "Done", "✅ All unknown questions trained!")

    def clear_unknown_file(self):
        open(UNKNOWN_FILE, "w").close()
