import io
import pymupdf
from fastapi import FastAPI, UploadFile
import re

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Camdyn says hi! :)"}

@app.post("/read-pdf/")
async def read_pdf_file(file: UploadFile):
    try:
        course_grade_dict = dict()
        pdf_bytes = await file.read()
        pdf_file = io.BytesIO(pdf_bytes)

        pdf_document = pymupdf.open("pdf", pdf_file)

        for page in pdf_document:
            page_line = 0
            lines = page.get_text().splitlines()
            while page_line < len(lines):
                if check_if_session_text(lines[page_line]) and page_line + 3 < len(lines) and check_if_grade_exists(lines[page_line + 3]):
                    course_code = extract_course_code(lines[page_line + 1])
                    course_weight = extract_course_weight(lines[page_line + 1])
                    course_grade_dict[course_code] = [lines[page_line + 3], course_weight]
                page_line += 1

        print(course_grade_dict)

    except Exception as e:
        return {"error": f"Error processing PDF: {e}"}

def check_if_session_text(text):
    session_pattern = re.compile(r"(FW|SU)\d{2}", re.IGNORECASE)
    return session_pattern.match(text)

def check_if_grade_exists(text):
    grade_pattern = re.compile(r"[A-F]{1}[+]*", re.IGNORECASE)
    return grade_pattern.match(text)

def extract_course_code(text):
    course_code_pattern = re.compile(r"[A-Z]{2}\s[A-Z]+\s+\d{4}", re.IGNORECASE)
    return course_code_pattern.match(text).group(0)

def extract_course_weight(text):
    course_code_pattern = re.compile(r"[A-Z]{2}\s[A-Z]+\s+\d{4}", re.IGNORECASE)
    course_weight_pattern = re.compile(r"\d\.\d{2}")
    course_weight = course_code_pattern.split(text)[1].strip()
    return course_weight_pattern.match(course_weight).group(0)