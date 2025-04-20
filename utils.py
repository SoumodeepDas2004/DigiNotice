from database import Database
import hashlib
import re
import mimetypes
import os

import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for Images
import cv2  # OpenCV for image handling
import re
import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer


#add helping function from pages with gui
db = Database()

""" from auth.py"""

def is_valid_password(password):
    return bool(re.fullmatch(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*()-_])[A-Za-z\d!@#$%^&*()-_]{6,}$", password))

# 🔹 Register User
def register_user(unique_id, name, password):
    """Check if the unique_id already exists before inserting and validate password."""
    
    # ❌ Check if password follows the required pattern
    if not is_valid_password(password):
        return "❌ Password must have at least 6 characters, including a letter, a number, and a special character!"
    
    # ✅ Check if the unique_id already exists
    check_query = "SELECT unique_id FROM users WHERE unique_id = %s"
    result = db.fetch_data(check_query, (unique_id,))

    if result:  # If result is not empty, the ID is taken
        return "❌ This ID is already taken!"

    # ✅ Hash password and store in database
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  
    query = "INSERT INTO users (unique_id, name, password) VALUES (%s, %s, %s)"
    db.execute_query(query, (unique_id, name, hashed_password))
    
    return "✅ User Registered Successfully!"

# 🔹 Login User (Now returns user details instead of just True/False)
def login_user(unique_id, password):
    """Hashes input password and compares it with the hashed password stored in DB."""
    hashed_password = hashlib.sha256(password.encode()).hexdigest()  # ✅ Hash input password

    query = "SELECT unique_id, name FROM users WHERE unique_id = %s AND password = %s"
    result = db.fetch_data(query, (unique_id, hashed_password))  # ✅ Fetch user details

    return result[0] if result else None  # ✅ Return user data instead of just True/False

# 🔹 Get All Users (For Admin Panel)
def get_all_users():
    query = "SELECT unique_id, name FROM users ORDER BY unique_id ASC"
    return db.fetch_data(query)

# 🔹 Delete User by Unique ID (Admin Function)
def delete_user(unique_id):
    query = "DELETE FROM users WHERE unique_id = %s"
    db.execute_query(query, (unique_id,))



""" from notice_manager.py """

# 🔹 Add Notice
def add_notice(title, content, summary, file_path):
    query = "INSERT INTO notices (title, content, summary, file_path) VALUES (%s, %s, %s, %s)"
    db.execute_query(query, (title, content, summary, file_path))

# 🔹 Get Latest Notices (for Notice Board)
def get_latest_notices(limit=4):
    print("🔍 Fetching notices from database...")
    query = "SELECT title, content, file_path, summary, created_at FROM notices ORDER BY created_at DESC LIMIT %s"
    notices = db.fetch_data(query, (limit,))

    
    # print(f"✅ Notices Fetched: {notices}")  # <-- Debugging
    processed_notices = []

    for title, content, file_path, summary, notice_time in notices:
        print(f"📜 Processing: {title}, {file_path}")  # <-- Debugging

        if content == "Content extracted from file" and file_path:
            if os.path.exists(file_path):
                file_type, _ = mimetypes.guess_type(file_path)

                if file_type and file_type.startswith("text"):  # Read only text files
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            content = file.read()
                    except UnicodeDecodeError:
                        content = "❌ Error: File encoding not supported (Not UTF-8)."
                    except Exception as e:
                        content = f"❌ Error reading file: {e}"
                else:
                    content = " ".join(summary.split()[:35]) + "..."  # ✅ Show first 35 words of summary
            else:
                content = "❌ File not found"

        processed_notices.append((title, content, file_path, notice_time))

    print(f"✅ Processed Notices: {processed_notices}")  # <-- Debugging
    return processed_notices

# 🔹 Get Summarized Notices (for Rotating Summaries)
def get_summarized_notices(limit=5):
    query = "SELECT COALESCE(summary, 'No summary available') FROM notices ORDER BY created_at DESC LIMIT %s"
    results = db.fetch_data(query, (limit,))
    return [row[0] for row in results]  # Extract summaries from results

# 🔹 Get All Notices (for Admin Panel)
def get_all_notices():
    query = "SELECT id, title, summary, created_at, file_path FROM notices ORDER BY created_at DESC"
    return db.fetch_data(query)

# 🔹 Delete Notice by ID
def delete_notice(notice_id):
    """Deletes a notice and resets IDs properly."""
    try:
        delete_query = "DELETE FROM notices WHERE id = %s;"
        db.execute_query(delete_query, (notice_id,))  # ✅ No need for multi=True

        print(f"✅ Notice with ID {notice_id} deleted successfully!")
        refreshid()  # ✅ Reset ID after deletion

    except Exception as err:
        print(f"❌ Error deleting notice: {err}")

# 🔹 Reset Notice IDs After Deletion
def refreshid():
    """Resets the notice IDs properly after deletion."""
    reset_queries = [
        "CREATE TABLE temp_notices AS SELECT title, content, summary, file_path, created_at FROM notices ORDER BY id;",
        "DROP TABLE notices;",
        """CREATE TABLE notices (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            content TEXT,
            summary TEXT,
            file_path VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );""",
        "INSERT INTO notices (title, content, summary, file_path, created_at) SELECT title, content, summary, file_path, created_at FROM temp_notices;",
        "DROP TABLE temp_notices;"
    ]

    for query in reset_queries:
        try:
            db.execute_query(query)
        except Exception as e:
            print(f"❌ Error in ID Reset: {e}")



""" from summarization.py """

# ✅ Download necessary NLTK data (once per setup)
nltk.download('punkt')
nltk.download('stopwords')

# ✅ Initialize the Punkt tokenizer globally
punkt_tokenizer = PunktSentenceTokenizer()

# ✅ Ensure Tesseract OCR is set up properly
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

# 🔹 Extract Text from PDF
def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        doc = fitz.open(pdf_path)
        text = " ".join(page.get_text() for page in doc)
        return text.strip() if text.strip() else "No text found in PDF."
    except Exception as e:
        return f"❌ Error extracting text from PDF: {e}"

# 🔹 Extract Text from Image using OCR
def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR."""
    try:
        image = cv2.imread(image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
        text = pytesseract.image_to_string(gray)
        return text.strip() if text.strip() else "No text found in image."
    except Exception as e:
        return f"❌ Error extracting text from image: {e}"

# 🔹 Clean Extracted Text
def clean_text(text):
    """Cleans and preprocesses extracted text."""
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'[^a-zA-Z0-9.,!? ]', '', text)  # Remove unwanted special characters
    return text.strip()

# 🔹 Summarize Extracted Text
def summarize_text(text, max_sentences=3):
    """Summarizes the extracted text by selecting key sentences."""
    if not text.strip():
        return "No text extracted for summarization."

    sentences = punkt_tokenizer.tokenize(text)  # Use Punkt tokenizer
    return ' '.join(sentences[:max_sentences]) if sentences else "No sentences found."

# 🔹 Summarize Notices (PDF or Image)
def summarize_file(file_path):
    """Summarizes a notice file whether it is a PDF or an Image."""
    if file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        text = extract_text_from_image(file_path)
    else:
        return "Unsupported file format"

    cleaned_text = clean_text(text)
    return summarize_text(cleaned_text)


#clearing notice 
def clear_layout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
        elif child.layout():
            clear_layout(child.layout())
