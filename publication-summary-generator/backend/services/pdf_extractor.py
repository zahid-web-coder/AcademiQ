import fitz  # PyMuPDF

def extract_text_from_pdf(file_path: str) -> str:
    try:
        text = ""
        with fitz.open(file_path) as pdf:
            for page in pdf:
                text += page.get_text()
        return text.strip() if text else "Error: No extractable text found in PDF."
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"
