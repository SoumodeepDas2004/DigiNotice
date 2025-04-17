import json
import os
import queue
import spacy
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QThread, pyqtSignal,Qt
import time
from PyQt5.QtGui import QPixmap,QIcon
# Load spaCy model
nlp = spacy.load("en_core_web_md")

# File paths
BRAIN_FILE = "brain.json"
UNKNOWN_FILE = "unknown.txt"

class VoiceRecognitionThread(QThread):
    """Worker thread for offline speech recognition using Vosk."""
    recognized_text = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            model_path = "vosk-model-small-en-in-0.4"  # Adjust to your extracted model path
            if not os.path.exists(model_path):
                self.error_occurred.emit("Model not found. Please check the path.")
                return

            model = Model(model_path)
            recognizer = KaldiRecognizer(model, 16000)
            q = queue.Queue()

            def callback(indata, frames, time, status):
                if status:
                    print("Status:", status)
                q.put(bytes(indata))

            with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                       channels=1, callback=callback):
                print("🎤 Listening...")
                timeout = time.time() + 10  # Stop after 10 seconds
                while time.time() < timeout:
                    data = q.get()
                    if recognizer.AcceptWaveform(data):
                        result = recognizer.Result()
                        text = json.loads(result).get("text", "")
                        self.recognized_text.emit(text)
                        return

        except Exception as e:
            self.error_occurred.emit(f"Speech recognition failed: {str(e)}")


class DigiBot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("💬 DigiBot Help Desk")
        self.setFixedSize(900, 600)
        self.setWindowIcon(QIcon("assets/bgpics/digibotbg.jpg"))
        #bg pic set
        self.background_label = QLabel(self)
        self.bgimgpath = "assets/bgpics/digibotbg.jpg"
        self.set_background_image(self.bgimgpath)
        
        # Layout setup
        layout = QVBoxLayout()
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #c4c2dd, stop: 1  #f10000); font-size: 15px; padding: 10px;")
        #adressing bot
        self.adressing=QLabel("🤖 Welcome to DigiNotice. How can I assist you today?")
        self.adressing.setStyleSheet("color:white; font-weight:bold; font-size: 16px")
        
        #chat button part
        self.input_box = QLineEdit()
        self.input_box.setFixedSize(500,40)
        self.input_box.setStyleSheet("background-color: #d9b688; font-weight: bold; border: 2px solid #02f707; font-size: 12px; border-radius: 5px;")
        self.input_box.setPlaceholderText("Type your question here...")
        self.input_box.returnPressed.connect(self.process_input)

        self.send_btn = QPushButton(" ⏩ Send")
        self.send_btn.clicked.connect(self.process_input)
        self.send_btn.setFixedHeight(40)
        self.send_btn.setStyleSheet("""
                                    QPushButton{background-color: ##d759eb;  border: 1px solid #000000;  border-radius: 8px;}
                                    QPushButton:hover{background-color: #71d247; font-weight: bold; border: 2px solid #02f707; font-size: 14px; border-radius: 8px;}""")
       
        self.voice_btn = QPushButton("🎤 Speak")
        self.voice_btn.setFixedHeight(40)

        self.voice_btn.clicked.connect(self.listen_voice)
        self.voice_btn.setStyleSheet("""
                                    QPushButton{background-color: #d759eb;  border: 1px solid #000000;  border-radius: 8px;}
                                    QPushButton:hover{background-color: #71d247; font-weight: bold; border: 2px solid #02f707; font-size: 14px; border-radius: 5px;}""")

        # Arrange widgets
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.input_box)
        btn_layout.addWidget(self.send_btn)
        btn_layout.addWidget(self.voice_btn)

        layout.addWidget(self.adressing)
        layout.addWidget(self.chat_display)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        # Load bot brain
        self.brain = self.load_brain()

        # Initialize the worker thread for voice recognition
        self.voice_thread = VoiceRecognitionThread()
        self.voice_thread.recognized_text.connect(self.handle_recognized_text)
        self.voice_thread.error_occurred.connect(self.handle_error)

    def load_brain(self):
        """Loads predefined question-answer pairs from brain.json."""
        if os.path.exists(BRAIN_FILE):
            with open(BRAIN_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_unknown(self, query):
        """Saves unknown query to unknown.txt for future training."""
        query = query.lower().strip()
        if query:
            with open(UNKNOWN_FILE, "a", encoding='utf-8') as f:
                f.write(f"{query}\n")

    def get_response(self, user_query):
        """Returns the most relevant answer using semantic similarity."""
        print(f"You said: {user_query}")
        user_doc = nlp(user_query)
        best_match = None
        highest_similarity = 0

        for question in self.brain:
            question_doc = nlp(question)
            similarity = user_doc.similarity(question_doc)
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match = question

        if highest_similarity >= 0.75:
            return self.brain[best_match]
        else:
            self.save_unknown(user_query)
            return "❓ I don't know that yet, but I'll learn it soon!"

    def process_input(self):
        """Handles text input from user."""
        user_input = self.input_box.text().strip()
        if not user_input:
            return
        self.chat_display.append(f"🧑 : {user_input}")
        response = self.get_response(user_input)
        self.chat_display.append(f"🤖 : {response}\n")
        self.input_box.clear()

    def listen_voice(self):
        """Starts the voice recognition process in a separate thread."""
        self.chat_display.append("🎤 Listening...Ask me your Query")
        self.voice_thread.start()

    def handle_recognized_text(self, text):
        """Handles the recognized text from the voice thread."""
        self.chat_display.append(f"🧑 You (voice): {text}")
        
        response = self.get_response(text)
        self.chat_display.append(f"🤖 Bot: {response}\n")

    def handle_error(self, error_message):
        """Handles errors from the voice recognition thread."""
        QMessageBox.warning(self, "Error", error_message)
    # ✅ To use the Bot instance created in main.py
    def show_digibot(self):
        self.main_window.chatbot_widget.show()
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



