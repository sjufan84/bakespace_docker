'''from fastapi import APIRouter, UploadFile, Form, File
from ..services.extraction_service import ExtractionService  

router = APIRouter()

@router.post("/extract-pdf")
async def extract_pdf_endpoint(pdf_file: UploadFile = File(...)):
    content = await pdf_file.read()
    recipe = ExtractionService.extract_pdf(content)
    return {"recipe": recipe}

@router.post("/detect-document")
async def detect_document_endpoint(uploaded_image: UploadFile = File(...)):
    content = await uploaded_image.read()
    detected_text = ExtractionService.detect_document(content)
    return {"detected_text": detected_text}

@router.post("/spellcheck-text")
async def spellcheck_text_endpoint(text: str = Form(...)):
    corrected_text = ExtractionService.spellcheck_text(text)
    return {"corrected_text": corrected_text}

@router.post("/extract-text-from-txt")
async def extract_text_from_txt_endpoint(file: UploadFile = File(...)):
    content = await file.read()
    text = ExtractionService.extract_text_from_txt(content)
    return {"text": text}

@router.post("/text-recipe-edit")
async def text_recipe_edit_endpoint(recipe: str = Form(...)):
    edited_recipe = ExtractionService.text_recipe_edit(recipe)
    return {"edited_recipe": edited_recipe}

@router.post("/photo-recipe-edit")
async def photo_recipe_edit_endpoint(recipe: str = Form(...)):
    edited_recipe = ExtractionService.photo_recipe_edit(recipe)
    return {"edited_recipe": edited_recipe}'''
