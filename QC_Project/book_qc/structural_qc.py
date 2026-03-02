import re

def tag_issue(message, severity):
    return {
        "severity": severity,
        "message": message
    }

def run_structural_qc(doc, pages):
    issues = []

    total_pages = len(doc)

    # ------------------------
    # 1️⃣ Blank Pages
    # ------------------------
    for page in pages:
        if page["word_count"] < 15:
            issues.append(tag_issue(
                f"Page {page['page_number']} appears blank.",
                "Major"
            ))

    # ------------------------
    # 2️⃣ Page Order Issues
    # ------------------------
    page_numbers = [p["page_number"] for p in pages]
    if page_numbers != sorted(page_numbers):
        issues.append(tag_issue(
            "Page order appears incorrect.",
            "Critical"
        ))

    # ------------------------
    # 3️⃣ Missing Pages (Logical Detection)
    # ------------------------
    expected = list(range(1, total_pages + 1))
    if page_numbers != expected:
        issues.append(tag_issue(
            "Possible missing pages detected.",
            "Critical"
        ))

    # ------------------------
    # 4️⃣ Margin Consistency
    # ------------------------
    margins = []
    for page in doc:
        rect = page.rect
        margins.append((rect.x0, rect.y0, rect.x1, rect.y1))

    if len(set(margins)) > 1:
        issues.append(tag_issue(
            "Margin inconsistency detected across pages.",
            "Major"
        ))

    # ------------------------
    # 5️⃣ Page Dimension Consistency
    # ------------------------
    page_sizes = [(page.rect.width, page.rect.height) for page in doc]
    if len(set(page_sizes)) > 1:
        issues.append(tag_issue(
            "Inconsistent page dimensions detected.",
            "Critical"
        ))

    # ------------------------
    # 6️⃣ Broken Bookmarks
    # ------------------------
    try:
        toc = doc.get_toc()
        for level, title, page_num in toc:
            if page_num > total_pages:
                issues.append(tag_issue(
                    f"Broken bookmark detected: '{title}' points to non-existent page {page_num}.",
                    "Major"
                ))
    except Exception:
        pass

    # ------------------------
    # 7️⃣ Image Resolution Check (DPI-Based)
    # ------------------------
    min_dpi = 150

    for page in doc:
        rect = page.rect
        page_width_inches = rect.width / 72

        for img in page.get_images(full=True):
            xref = img[0]
            pix = doc.extract_image(xref)

            width = pix["width"]
            dpi = width / page_width_inches if page_width_inches else 0

            if dpi < min_dpi:
                issues.append(tag_issue(
                    f"Low DPI image detected on page {page.number+1} ({int(dpi)} DPI).",
                    "Critical"
                ))

    # ------------------------
    # 8️⃣ Font Embedding Check
    # ------------------------
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if not span.get("font", ""):
                            issues.append(tag_issue(
                                f"Possible unembedded font on page {page_num+1}.",
                                "Major"
                            ))

    # ------------------------
    # 9️⃣ Excessive Image Count (Layout Risk)
    # ------------------------
    for page in doc:
        if len(page.get_images(full=True)) > 15:
            issues.append(tag_issue(
                f"Page {page.number+1} contains excessive number of images.",
                "Minor"
            ))

    return issues