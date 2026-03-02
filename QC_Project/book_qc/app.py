import streamlit as st
from pdf_extractor import extract_pdf
from structural_qc import run_structural_qc
from typography_qc import run_typography_qc
from publishing_qc import run_publishing_qc
from content_qc import run_content_qc
from semantic_qc import run_semantic_qc
from report_generator import generate_report

st.set_page_config(layout="wide")
st.title("📘 AI Book Publishing QC System (Local LLM)")

uploaded_file = st.file_uploader("Upload Book PDF", type=["pdf"])

if uploaded_file:
    with open("temp_book.pdf", "wb") as f:
        f.write(uploaded_file.read())

    doc, pages = extract_pdf("temp_book.pdf")

    with st.spinner("Running Structural QC..."):
        structural_issues = run_structural_qc(doc, pages)

    with st.spinner("Running Typography QC..."):
        typography_issues = run_typography_qc(doc)

    with st.spinner("Running Publishing QC..."):
        publishing_issues = run_publishing_qc(doc, pages)

    with st.spinner("Running Content QC..."):
        content_issues = run_content_qc(pages)

    with st.spinner("Running Semantic QC (LLaMA3)..."):
        semantic_issues = run_semantic_qc(pages)

    # Combine non-structural issues
    combined_typography = typography_issues + publishing_issues + content_issues

    report_text, score, status = generate_report(
        structural_issues,
        combined_typography,
        semantic_issues
    )

    st.success(f"QC Completed — Score: {score}/100")
    st.write(f"### Status: {status}")
    st.text_area("QC Report", report_text, height=500)

    st.download_button("Download Report", report_text, "QC_Report.txt")