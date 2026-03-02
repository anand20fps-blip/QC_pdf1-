import re

def tag_issue(message, severity):
    return {
        "severity": severity,
        "message": message
    }

def run_publishing_qc(doc, pages):
    issues = []

    headers = []
    footers = []
    detected_page_numbers = []

    # Extract TOC once
    try:
        toc = doc.get_toc()
    except Exception:
        toc = []

    for page in pages:
        text = page["text"]
        page_number = page["page_number"]

        lines = [l.strip() for l in text.split("\n") if l.strip()]

        if not lines:
            continue

        # ----------------------------
        # 1️⃣ Widow / Orphan Detection
        # ----------------------------
        for i in range(len(lines) - 1):
            # Widow = single short word line
            if len(lines[i].split()) == 1:
                issues.append(tag_issue(
                    f"Widow line detected on page {page_number}",
                    "Minor"
                ))

        # Orphan = very short first paragraph line
        if len(lines[0].split()) <= 2:
            issues.append(tag_issue(
                f"Orphan line detected at top of page {page_number}",
                "Minor"
            ))

        # ----------------------------
        # 2️⃣ Header / Footer Consistency
        # ----------------------------
        header = lines[0]
        footer = lines[-1]

        headers.append(header)
        footers.append(footer)

        # Detect printed page number
        page_num_match = re.search(r'\b\d+\b', footer)
        if page_num_match:
            detected_page_numbers.append(int(page_num_match.group()))

        # ----------------------------
        # 3️⃣ Chapter Start Formatting
        # ----------------------------
        if "chapter" in header.lower():
            if not header.isupper():
                issues.append(tag_issue(
                    f"Chapter title formatting inconsistent on page {page_number}",
                    "Minor"
                ))

    # ----------------------------
    # 4️⃣ Header Consistency Across Pages
    # ----------------------------
    if len(set(headers)) > len(headers) * 0.5:
        issues.append(tag_issue(
            "Header inconsistency detected across pages.",
            "Major"
        ))

    # ----------------------------
    # 5️⃣ Footer Consistency Across Pages
    # ----------------------------
    if len(set(footers)) > len(footers) * 0.5:
        issues.append(tag_issue(
            "Footer inconsistency detected across pages.",
            "Major"
        ))

    # ----------------------------
    # 6️⃣ Incorrect Page Numbering
    # ----------------------------
    if detected_page_numbers:
        expected = list(range(min(detected_page_numbers),
                              min(detected_page_numbers) + len(detected_page_numbers)))
        if detected_page_numbers != expected:
            issues.append(tag_issue(
                "Incorrect page numbering sequence detected.",
                "Critical"
            ))

    # ----------------------------
    # 7️⃣ TOC Mismatch Detection
    # ----------------------------
    for level, title, page_num in toc:
        if page_num > len(pages):
            issues.append(tag_issue(
                f"TOC entry '{title}' points to non-existent page {page_num}.",
                "Major"
            ))

    # ----------------------------
    # 8️⃣ Inconsistent Font Sizes (Document Level)
    # ----------------------------
    font_sizes = []

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_sizes.append(span["size"])

    if len(set(font_sizes)) > 15:
        issues.append(tag_issue(
            "High font size variation detected across document.",
            "Major"
        ))

    return issues