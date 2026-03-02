import re
from spellchecker import SpellChecker

spell = SpellChecker()

def tag_issue(message, severity):
    return {
        "severity": severity,
        "message": message
    }

def run_content_qc(pages):
    issues = []
    full_text = "\n".join(p["text"] for p in pages)

    words = re.findall(r"\b[a-zA-Z]+\b", full_text)

    # ----------------------
    # 1️⃣ Spelling Check (Pure Python)
    # ----------------------
    misspelled = spell.unknown(words)

    if misspelled:
        issues.append(tag_issue(
            f"{len(misspelled)} possible spelling errors detected.",
            "Major"
        ))

    # ----------------------
    # 2️⃣ Repeated Paragraphs
    # ----------------------
    paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
    duplicates = set([p for p in paragraphs if paragraphs.count(p) > 1])

    if duplicates:
        issues.append(tag_issue(
            "Repeated paragraph detected.",
            "Major"
        ))

    # ----------------------
    # 3️⃣ Missing Headings
    # ----------------------
    headings = re.findall(r'Chapter\s+\d+', full_text)
    if not headings:
        issues.append(tag_issue(
            "No chapter headings detected.",
            "Minor"
        ))

    # ----------------------
    # 4️⃣ Inconsistent Numbering
    # ----------------------
    numbers = re.findall(r'\d+\.', full_text)
    if len(numbers) != len(set(numbers)):
        issues.append(tag_issue(
            "Possible inconsistent numbering detected.",
            "Major"
        ))

    return issues