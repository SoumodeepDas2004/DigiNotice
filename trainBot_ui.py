import json
import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox
from PyQt5.QtGui import QPixmap,QIcon
from PyQt5.QtCore import Qt
BRAIN_FILE = "brain.json"
UNKNOWN_FILE = "unknown.txt"

class TrainBotUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠DigiBot Trainer")
        self.setFixedSize(900, 600)
        self.setWindowIcon(QIcon("assets/icon_file/boticon.jpg"))
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        #bg pic set
        self.background_label = QLabel(self)
        self.bgimgpath = "assets/bgpics/digibotbg.jpg"
        self.set_background_image(self.bgimgpath)
        
        self.setStyleSheet('''
                        
                        ''')
        
        self.addressing=QLabel("❓ Unknown Questions:")
        self.addressing.setStyleSheet("color:white; font-weight:bold; font-size: 16px")
        self.question_list = QListWidget()
        self.question_list.setStyleSheet("""
                                        QListWidget{background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #4cf175, stop: 1 #9969f8  ); font-size: 15px; padding: 10px;}
                                        QListWidget::item{padding:2px; border: 1px solid red; margin: 3px;   text-align: center;}
                                        """)
        
        
        self.answer_input = QLineEdit()
        self.answer_input.setStyleSheet("""QLineEdit{background-color: #ffb2fa; font-weight: bold; border: 2px solid #02f707; font-size: 12px; border-radius: 5px; padding:2px;}""")
        self.answer_input.setFixedSize(870,40)
        self.answer_input.setPlaceholderText("Type answer for selected question...")
        self.answer_input.setAlignment(Qt.AlignCenter)
        
        self.submit_btn = QPushButton("Add Answer")
        self.submit_btn.setStyleSheet("""
                                            QPushButton{background-color: #a0e2ac;  border: 1px solid #000000;  border-radius: 10px;}
                                            QPushButton:hover{background-color: #71d247; font-weight: bold; border: 2px solid #02f707; font-size: 14px; border-radius: 8px;}""")
            
        self.submit_btn.setFixedHeight(40)
        self.submit_btn.clicked.connect(self.save_answer)
        
        self.layout.addWidget(self.addressing)
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
        
        
    #background ui setup func
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
