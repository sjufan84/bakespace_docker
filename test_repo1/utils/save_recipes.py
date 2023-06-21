import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64
import tempfile

def save_recipe_as_pdf(text, title="recipe"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as fp:
        c = canvas.Canvas(fp.name, pagesize=letter)
        c.drawString(20, 750, title)  # Add title to the PDF
        for i, line in enumerate(text.split('\n')):
            c.drawString(20, 750 - (i+1) * 20, line)  # Adjusted the starting point to accommodate the title
        c.save()
        return fp.name


def get_recipe_pdf_download_link(pdf_path, download_name):
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    b64_pdf = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:file/pdf;base64,{b64_pdf}" download="{download_name}">Download Recipe as PDF</a>'
    return href

def save_pairing_as_pdf(text, title=f"Wine Pairing Suggestions for {st.session_state.recipe_name}"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as fp:
        c = canvas.Canvas(fp.name, pagesize=letter)
        c.drawString(20, 750, title)  # Add title to the PDF
        for i, line in enumerate(text.split('\n')):
            c.drawString(20, 750 - (i+1) * 20, line)  # Adjusted the starting point to accommodate the title
        c.save()
        return fp.name


def get_pairing_pdf_download_link(pdf_path, download_name):
    with open(pdf_path, "rb") as f:
        pdf_data = f.read()
    b64_pdf = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:file/pdf;base64,{b64_pdf}" download="{download_name}">Download Recipe as PDF</a>'
    return href

