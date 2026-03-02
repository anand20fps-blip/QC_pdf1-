import ollama

def chunk_text(text, size=1200):
    return [text[i:i+size] for i in range(0, len(text), size)]

def classify_severity(text):
    text = text.lower()
    if "contradiction" in text or "fact error" in text:
        return "Critical"
    elif "inconsistency" in text or "missing explanation" in text:
        return "Major"
    else:
        return "Minor"

def run_semantic_qc(pages):
    full_text = "\n".join(p["text"] for p in pages)
    chunks = chunk_text(full_text)

    issues = []

    for chunk in chunks[:5]:  # limit for performance
        prompt = f"""
You are a professional publishing QC expert.

Identify:
- Logical inconsistencies
- Fact contradictions
- Tone inconsistency
- Missing explanations
- Poor flow

Respond in concise bullet points only.
Do not explain — just list issues.
        
Text:
{chunk}
"""

        response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}]
        )

        result_text = response["message"]["content"]

        severity = classify_severity(result_text)

        issues.append({
            "severity": severity,
            "message": result_text.strip()
        })

    return issues