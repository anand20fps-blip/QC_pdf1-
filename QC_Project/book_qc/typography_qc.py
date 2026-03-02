import statistics

def tag_issue(message, severity):
    return {
        "severity": severity,
        "message": message
    }


def run_typography_qc(doc):
    issues = []
    font_sizes = []
    margins = []
    image_dpi_threshold = 150  # Minimum acceptable DPI

    for page_num, page in enumerate(doc):

        rect = page.rect
        margins.append((rect.x0, rect.y0, rect.x1, rect.y1))

        blocks = page.get_text("dict")["blocks"]

        # ----------------------
        # FONT + WIDOW DETECTION
        # ----------------------
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    spans = line.get("spans", [])

                    # Widow detection (single short word line)
                    if len(spans) == 1:
                        text = spans[0]["text"].strip()
                        if len(text.split()) == 1:
                            issues.append(
                                tag_issue(
                                    f"Page {page_num+1}: Widow line detected ('{text}')",
                                    "Minor"
                                )
                            )

                    for span in spans:
                        font_sizes.append(span["size"])

                        # Font embedding check
                        if not span.get("font", ""):
                            issues.append(
                                tag_issue(
                                    f"Page {page_num+1}: Possible unembedded font detected",
                                    "Major"
                                )
                            )

        # ----------------------
        # FOOTER PAGE NUMBER CHECK
        # ----------------------
        footer_text = page.get_text(
            "text",
            clip=(0, rect.height - 40, rect.width, rect.height)
        )

        if str(page_num + 1) not in footer_text:
            issues.append(
                tag_issue(
                    f"Page {page_num+1}: Missing page number footer",
                    "Major"
                )
            )

        # ----------------------
        # IMAGE DPI CHECK
        # ----------------------
        for img in page.get_images(full=True):
            xref = img[0]
            pix = doc.extract_image(xref)

            width = pix["width"]
            height = pix["height"]

            # Approximate DPI calculation
            page_width_inches = rect.width / 72
            dpi = width / page_width_inches if page_width_inches else 0

            if dpi < image_dpi_threshold:
                issues.append(
                    tag_issue(
                        f"Page {page_num+1}: Low DPI image detected ({int(dpi)} DPI)",
                        "Critical"
                    )
                )

    # ----------------------
    # FONT SIZE VARIATION CHECK
    # ----------------------
    if len(set(font_sizes)) > 12:
        issues.append(
            tag_issue(
                "High font size variation detected (typography inconsistency)",
                "Minor"
            )
        )

    # ----------------------
    # MARGIN VARIANCE CHECK
    # ----------------------
    if len(set(margins)) > 1:
        issues.append(
            tag_issue(
                "Margin inconsistency detected across pages",
                "Major"
            )
        )

    return issues