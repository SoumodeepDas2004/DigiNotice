import fitz  # PyMuPDF for PDFs
import pytesseract  # OCR for Images
from PIL import Image  # Image Processing
import cv2  # OpenCV for image handling
import re
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

nltk.download('punkt')
nltk.download('stopwords')

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
def summarize_text(text, max_sentences=3):
    """Summarizes the extracted text by selecting key sentences."""
    sentences = sent_tokenize(text)
    if len(sentences) <= max_sentences:
        return text  # If text is already short, return as is

    stop_words = set(stopwords.words("english"))
    important_sentences = [sent for sent in sentences if len(set(sent.split()) - stop_words) > 3]

    return ' '.join(important_sentences[:max_sentences])

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