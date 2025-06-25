from dotenv import load_dotenv
import base64
import streamlit as st
import os
import io
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Use st.secrets if deploying on Streamlit Cloud (uncomment below if needed)
# genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Local run:
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# === Helper Functions ===

def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        pdf_data = uploaded_file.read()
        doc = fitz.open(stream=pdf_data, filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap()

        img_byte_arr = io.BytesIO()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.save(img_byte_arr, format='JPEG')

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr.getvalue()).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# === Streamlit App ===

st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

input_text = st.text_area("Job Description:", key="input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file:
    st.success("✅ PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume")
submit3 = st.button("Percentage match")

input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. 
Give me the percentage of match if the resume matches the job description. 
First, the output should come as percentage, then keywords missing, and finally final thoughts.
"""

if submit1 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)
    response = get_gemini_response(input_text, pdf_content, input_prompt1)
    st.subheader("The Response is")
    st.write(response)
elif submit3 and uploaded_file:
    pdf_content = input_pdf_setup(uploaded_file)
    response = get_gemini_response(input_text, pdf_content, input_prompt3)
    st.subheader("The Response is")
    st.write(response)
elif (submit1 or submit3) and not uploaded_file:
    st.warning("⚠️ Please upload a PDF resume first.")
