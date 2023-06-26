from fastapi import APIRouter, Form, Request
from pydantic import BaseModel
from ..services.extraction_service import ExtractionService  

class Recipe(BaseModel):
    recipe: str

class TextData(BaseModel):
    text: str

router = APIRouter()

@router.post("/extract-pdf")
async def extract_pdf_endpoint(request: Request):
    form_data = await request.form()
    pdf_file = form_data["pdf_file"]
    content = await pdf_file.read()
    recipe = ExtractionService.extract_pdf(content)
    return {"recipe": recipe}

@router.post("/detect-document")
async def detect_document_endpoint(request: Request):
    form_data = await request.form()
    uploaded_image = form_data["uploaded_image"]
    content = await uploaded_image.read()
    detected_text = ExtractionService.detect_document(content)
    return {"detected_text": detected_text}

@router.post("/spellcheck-text")
async def spellcheck_text_endpoint(text_data: TextData):
    corrected_text = ExtractionService.spellcheck_text(text_data.text)
    return {"corrected_text": corrected_text}

@router.post("/extract-text-from-txt")
async def extract_text_from_txt_endpoint(request: Request):
    form_data = await request.form()
    file = form_data["file"]
    content = await file.read()
    text = ExtractionService.extract_text_from_txt(content)
    return {"text": text}

@router.post("/recipe-edit")
async def recipe_edit_endpoint(recipe: str):
    edited_recipe = ExtractionService.edit_recipe_text(recipe)
    return {"edited_recipe": edited_recipe}

