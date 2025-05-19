import io
import re
import os
import json
import datetime
import tempfile
import streamlit as st
import PyPDF2
from streamlit_pdf_viewer import pdf_viewer
from openai import OpenAI
from dotenv import load_dotenv
from pdf_util import generate_cv, cv_data

load_dotenv()

st.set_page_config(
    page_title="AI CV Analyst",
    page_icon="📃",
    layout="centered",
)

st.title("📄 AI CV Analyst")
# delay the toast for 2 seconds
st.toast("Welcome to the AI CV Analyst!", icon="📄")
st.markdown(
    "Upload your resume and get AI-powered feedback tailored to your needs!",
)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return "\n".join(
        [page.extract_text() for page in reader.pages if page.extract_text()]
    )


def extract_text_from_file(file):
    if file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(file.read()))
    return file.read().decode("utf-8")


def analyze_resume(content: str, role: str, client: OpenAI):
    prompt = f"""Please analyze this resume and provide constructive feedback. 
    Focus on the following aspects:
    1. Content clarity and impact
    2. Skills presentation
    3. Experience descriptions
    4. Specific improvements for {role if role else 'general job applications'}

    Resume content:
    {content}

    Please provide your analysis in a clear, structured format with specific recommendations.
    And finally, please provide a score out of 10 for the resume."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert resume reviewer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1000,
    )
    return response.choices[0].message.content


def rewrite_resume(content: str, analysis: str, role: str, client: OpenAI):
    prompt = f"""Rewrite the resume to make it more impactful and tailored to {role if role else 'general'} job roles.
    Use the following analysis as a guide for your rewrite:
    {analysis}

    Resume content:
    {content}

    Return the updated CV in this raw JSON format {cv_data} using the same structure as the original.
    Do NOT include any markdown formatting, explanation, or code fences like ```json.
    Only return the raw JSON.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert resume writer."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1500,
    )
    return response.choices[0].message.content


uploaded_file = st.file_uploader("Upload your resume (PDF or TXT)", type=["pdf", "txt"])
job_role = st.text_input("Enter the job role you're targeting (optional)")
analyze = st.button("Analyze Resume")

if analyze or uploaded_file:
    try:
        text = extract_text_from_file(uploaded_file)
        if not text.strip():
            st.error("Your uploaded file is empty.")
            st.stop()

        client = OpenAI(api_key=OPENAI_API_KEY)

        with st.spinner("Analyzing your resume..."):
            analysis = analyze_resume(text, job_role, client)

        st.markdown("Resume Analysis")
        st.markdown(analysis)

        with st.spinner("Rewriting your resume..."):
            rewritten_json_str = rewrite_resume(
                text,
                analysis,
                job_role,
                client,
            )

        try:
            json_data = json.loads(rewritten_json_str)
        except json.JSONDecodeError:
            # Attempt to fix malformed JSON
            # replace single quotes with double
            fixed_json_str = re.sub(r"'", '"', rewritten_json_str)
            # remove newline escapes if necessary
            fixed_json_str = re.sub(r"\\n", "", fixed_json_str)
            print("Rewritten JSON: ", fixed_json_str)
            try:
                json_data = json.loads(fixed_json_str)
            except Exception as inner_e:
                print(f"JSON formatting error: {inner_e}")
                st.markdown("Rewritten Resume (Raw JSON)")
                st.text_area("Raw Response", rewritten_json_str, height=300)
                st.stop()

        pdf_buffer = generate_cv(json_data)

        # Save the PDF to a temporary file
        # This is a workaround to allow the PDF to be downloaded
        # without needing to save it to disk
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_buffer.getvalue())
            tmp_path = tmp.name

        st.session_state["rewritten_cv_pdf"] = pdf_buffer  # store in session
        pdf_viewer(input=tmp_path, width=700)

        # Download button
        st.download_button(
            label="📥 Download Rewritten Resume as PDF",
            data=pdf_buffer,
            file_name="rewritten_resume.pdf",
            mime="application/pdf",
        )
        st.stop()

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

current_year = datetime.datetime.now().year
st.markdown("AI-powered feedback tailored to your needs!")
st.markdown(
    f"""<center>© {current_year}  AI CV Analyst by Lorenzo</center>""",
    unsafe_allow_html=True,
)
