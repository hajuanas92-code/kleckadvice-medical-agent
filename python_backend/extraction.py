
from __future__ import annotations

import io
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
import pytesseract
from PIL import Image


# ---------------------------------------------------------------------------
# STEP 1: PDF -> list of page images
# ---------------------------------------------------------------------------
def pdf_to_images(
    pdf_path: str, dpi: int = 300, page_numbers: List[int] = None
) -> List[Image.Image]:
    """
    Convert selected pages of a PDF into PIL Images.
    Higher dpi = better OCR accuracy but slower processing.
    300 is a good balance for lab report scans.

    page_numbers: 0-indexed list of pages to render, e.g. [0, 1] for the
                  first two pages. None (default) = render every page.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    zoom = dpi / 72  # PyMuPDF renders at 72 dpi by default; scale up via matrix
    matrix = fitz.Matrix(zoom, zoom)

    doc = fitz.open(str(pdf_path))
    indices = page_numbers if page_numbers is not None else range(len(doc))

    images = []
    for i in indices:
        pix = doc[i].get_pixmap(matrix=matrix)
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        images.append(img)
    doc.close()

    return images


# ---------------------------------------------------------------------------
# STEP 2a: OCR via Tesseract (DEFAULT - use this first)
# ---------------------------------------------------------------------------
def ocr_with_tesseract(images: List[Image.Image]) -> str:
    """
    Run Tesseract OCR on a list of page images and join the text.
    Free, local, no API key, no rate limits. Good default for prototyping.
    """
    full_text = []
    for i, img in enumerate(images):
        # psm 6 = "assume a uniform block of text" - works well for reports
        text = pytesseract.image_to_string(img, config="--psm 6")
        full_text.append(f"--- Page {i + 1} ---\n{text.strip()}")

    return "\n\n".join(full_text)


# ---------------------------------------------------------------------------
# STEP 2b: OCR via Google Cloud Vision API (LATER - swap in if Tesseract
# accuracy is not good enough on messy/handwritten/rotated scans)
# ---------------------------------------------------------------------------
# from google.cloud import vision
#
# def ocr_with_cloud_vision(images: List[Image.Image]) -> str:
#     """
#     Run OCR using Google Cloud Vision's DOCUMENT_TEXT_DETECTION.
#     Free for the first 1,000 pages/month, then ~$1.50 per 1,000 pages.
#     Requires GOOGLE_APPLICATION_CREDENTIALS env var pointing to a
#     service account key with Vision API access enabled.
#     """
#     client = vision.ImageAnnotatorClient()
#     full_text = []
#
#     for i, img in enumerate(images):
#         # Convert PIL Image -> bytes, since the API expects raw image content
#         buf = io.BytesIO()
#         img.save(buf, format="PNG")
#         content = buf.getvalue()
#
#         vision_image = vision.Image(content=content)
#         response = client.document_text_detection(image=vision_image)
#
#         if response.error.message:
#             raise RuntimeError(
#                 f"Cloud Vision error on page {i + 1}: {response.error.message}"
#             )
#
#         page_text = response.full_text_annotation.text
#         full_text.append(f"--- Page {i + 1} ---\n{page_text.strip()}")
#
#     return "\n\n".join(full_text)


def strip_page_markers(full_text: str) -> str:
    """
    Remove the "--- Page N ---" markers that ocr_with_tesseract/
    ocr_with_cloud_vision insert for filter_relevant_pages' benefit.
    Call this right before sending text to the LLM - the model doesn't
    need that scaffolding, only the actual report content.
    """
    lines = full_text.splitlines()
    cleaned = [line for line in lines if not line.strip().startswith("--- Page")]
    return "\n".join(cleaned).strip()


# ---------------------------------------------------------------------------
# STEP 3: strip OCR page markers, then single entry point the rest of
# the pipeline (LangGraph node, Spring Boot call, etc.) will actually call.
# ---------------------------------------------------------------------------
def extract_text_from_pdf(
    pdf_path: str,
    engine: str = "tesseract",
    page_numbers: List[int] = None,
) -> str:
    """
    Main entry point: takes a path to a PDF report and returns raw
    extracted text, ready to be handed to the LLM extraction step.

    engine: "tesseract" (default, free/local) or "cloud_vision" (later).
    page_numbers: 0-indexed list of pages to OCR, e.g. [0, 1] for the
                  first two pages. None (default) = process every page.
    """
    images = pdf_to_images(pdf_path, page_numbers=page_numbers)

    if engine == "tesseract":
        text = ocr_with_tesseract(images)

    elif engine == "cloud_vision":
        raise NotImplementedError(
            "Cloud Vision path is stubbed out (commented) above - "
            "uncomment ocr_with_cloud_vision and its import to enable it."
        )
        # text = ocr_with_cloud_vision(images)

    else:
        raise ValueError(f"Unknown OCR engine: {engine}")

    return strip_page_markers(text)


# ---------------------------------------------------------------------------
# Quick manual test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python extraction.py <path_to_report.pdf>")
        sys.exit(1)

    text = extract_text_from_pdf(r"C:\Users\anas\Downloads\report2.pdf", engine="tesseract", page_numbers=[0,1])
    print(text)