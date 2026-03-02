import fitz

def extract_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page in doc:
        text = page.get_text()
        bbox = page.rect
        pages.append({
            "page_number": page.number + 1,
            "text": text,
            "word_count": len(text.split()),
            "bbox": (bbox.x0, bbox.y0, bbox.x1, bbox.y1)
        })

    return doc, pages