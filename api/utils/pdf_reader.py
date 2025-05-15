import re
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
import pytesseract

# Load Tesseract languages (eng = English, fra = French, ara = Arabic)
TESS_LANGS = "eng+fra+ara"

# Match time ranges (e.g., 08:00-10:00) and fix invalid ones
TIME_PATTERN = re.compile(r"(\d{1,2}):(\d{2})\s*[-–]\s*(\d{1,2}):(\d{2})")

# Arabic and French day mappings
DAY_TRANSLATIONS = {
    "lundi": "Monday", "mardi": "Tuesday", "mercredi": "Wednesday", "jeudi": "Thursday", "vendredi": "Friday", "samedi": "Saturday", "dimanche": "Sunday",
    "الاثنين": "Monday", "الثلاثاء": "Tuesday", "الأربعاء": "Wednesday", "الخميس": "Thursday", "الجمعة": "Friday", "السبت": "Saturday", "الأحد": "Sunday"
}

def fix_time(h, m):
    h = int(h)
    m = int(m)
    if m >= 60:
        h += m // 60
        m = m % 60
    return f"{h:02}:{m:02}"

def extract_text_from_pdf(pdf_file):
    pdf_file.seek(0)  # rewind file to the beginning
    pdf_bytes = pdf_file.read()

    if not pdf_bytes:
        raise ValueError("Uploaded PDF file is empty.")

    pdf_file_obj = BytesIO(pdf_bytes)
    reader = PdfReader(pdf_file_obj)

    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    
    return text

def process_schedule_text(text):
    # Sample Arabic/English regex for days and times
    days_of_week = ["الأحد", "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
    
    schedule = {}
    
    # Regex to extract the days and times
    day_pattern = re.compile(r"([أ-ي]+)\s*(\d{2}:\d{2}-\d{2}:\d{2})\s*([\w\s,]+)")  # Arabic day, time, and class details
    
    # Iterate over each match and build the dictionary
    for match in re.finditer(day_pattern, text):
        day = match.group(1)
        time = match.group(2)
        class_details = match.group(3).strip()

        # Map Arabic days to English (if needed)
        if day not in schedule:
            schedule[day] = {}

        schedule[day][time] = class_details

    return schedule

def parse_schedule(pdf_file):
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_file)
    
    # Process the extracted text to build a schedule
    schedule = process_schedule_text(text)
    
    return schedule
