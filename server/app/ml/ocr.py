"""
OCR module for extracting text from PDF and image files.
Uses pdfplumber for text-based PDFs and pytesseract for scanned documents.
"""

import os
from typing import Optional

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from PIL import Image
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from a PDF file.
    Tries pdfplumber first (text-based PDFs), falls back to pytesseract (scanned PDFs).

    Args:
        file_path: Path to the PDF file.

    Returns:
        Extracted text content.

    Raises:
        ValueError: If no text extraction library is available.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    text = ""

    # Try pdfplumber first (works best for text-based PDFs)
    if HAS_PDFPLUMBER:
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            text = ""

    # If pdfplumber yielded no text, try OCR
    if not text.strip() and HAS_TESSERACT:
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(file_path)
            for image in images:
                page_text = pytesseract.image_to_string(image)
                if page_text:
                    text += page_text + "\n"
        except Exception:
            pass

    if not text.strip():
        raise ValueError(
            "Could not extract text from PDF. "
            "Ensure the file is a valid PDF with text content or install pytesseract for OCR."
        )

    return text.strip()


def extract_text_from_image(file_path: str) -> str:
    """
    Extract text from an image file using OCR (pytesseract).

    Args:
        file_path: Path to the image file (PNG, JPEG, etc.).

    Returns:
        Extracted text content.

    Raises:
        ValueError: If pytesseract is not available.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if not HAS_TESSERACT:
        raise ValueError("pytesseract is required for image OCR but is not installed.")

    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
    except Exception as e:
        raise ValueError(f"OCR failed on image: {str(e)}")

    if not text.strip():
        raise ValueError("No text could be extracted from the image.")

    return text.strip()


def extract_text(file_path: str) -> str:
    """
    Extract text from either a PDF or image file based on the file extension.

    Args:
        file_path: Path to the file.

    Returns:
        Extracted text content.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".bmp"):
        return extract_text_from_image(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
