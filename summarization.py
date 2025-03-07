import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for Images
from PIL import Image  # Image Processing
import cv2  # OpenCV for image handling
import re
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
nltk.data.find('tokenizers/punkt/english.pickle')
print("✅ NLTK 'punkt' is installed correctly!")

nltk.download('punkt')       # ✅ Sentence tokenizer (Required)
nltk.download('stopwords')   # ✅ Stopwords (Required)

# 🔹 Extract Text from PDF
def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

# 🔹 Extract Text from Image using OCR
def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    text = pytesseract.image_to_string(gray)
    return text.strip()

# 🔹 Clean Extracted Text
def clean_text(text):
    """Cleans and preprocesses extracted text."""
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    text = re.sub(r'[^a-zA-Z0-9.,!? ]', '', text)  # Remove special characters
    return text

# 🔹 Summarize Extracted Text
from nltk.tokenize import sent_tokenize
import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer
from nltk.tokenize import sent_tokenize

# Ensure required data is downloaded
nltk.download('punkt')
nltk.download('stopwords')




# Initialize the Punkt tokenizer
punkt_tokenizer = PunktSentenceTokenizer()

def summarize_text(text, max_sentences=3):
    """Summarizes the extracted text by selecting key sentences."""
    if not text.strip():  # ✅ Handle empty text
        return "No text extracted for summarization."

    sentences = punkt_tokenizer.tokenize(text)  # ✅ Use PunktTokenizer instead of sent_tokenize()

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
    summary = summarize_text(cleaned_text)
    return summary


import pytesseract
import cv2

# ✅ Set the Tesseract path manually (if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    text = pytesseract.image_to_string(gray)
    return text.strip()
