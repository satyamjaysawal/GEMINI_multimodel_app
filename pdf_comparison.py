import os
import streamlit as st
from PyPDF2 import PdfReader
from google.generativeai import configure, embed_content, GenerativeModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
configure(api_key=GOOGLE_API_KEY)

# Streamlit app setup
st.set_page_config(page_title="PDF Comparison using Google Generative AI", layout="centered")

# Function to extract text from a PDF file
def extract_pdf_text(pdf_file):
    text = ""
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to compare two texts and get AI-based insights
def compare_texts(text1, text2):
    model = GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    Compare the following two documents for similarities and differences:

    Document 1:
    {text1}

    Document 2:
    {text2}

    Describe key similarities, differences, and potential conclusions.
    """
    response = model.generate_content(prompt)
    return response.text if response else "Comparison not available."

# Streamlit App UI
st.title("PDF Document Comparison with Google Generative AI")
st.write("Upload two PDF files to compare.")

# File uploader
pdf_file1 = st.file_uploader("Choose the first PDF file", type="pdf")
pdf_file2 = st.file_uploader("Choose the second PDF file", type="pdf")

# Process and compare PDFs
if pdf_file1 and pdf_file2:
    with st.spinner("Extracting text from PDFs..."):
        text1 = extract_pdf_text(pdf_file1)
        text2 = extract_pdf_text(pdf_file2)

    # Compare the extracted text
    with st.spinner("Comparing documents..."):
        comparison_result = compare_texts(text1, text2)
    
    # Display the result
    st.subheader("Comparison Results")
    st.write(comparison_result)
else:
    st.info("Please upload two PDF files for comparison.")
