import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for Images
from PIL import Image  # Image Processing
import cv2  # OpenCV for image handling
import re
import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer

# ✅ Download necessary NLTK data (once per setup)
nltk.download('punkt')
nltk.download('stopwords')

# ✅ Initialize the Punkt tokenizer globally
punkt_tokenizer = PunktSentenceTokenizer()

# ✅ Ensure Tesseract OCR is set up properly
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
