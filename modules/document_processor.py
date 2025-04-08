import pytesseract
from PIL import Image
import pdf2image
import os
import tempfile

def process_document(file):
    """
    Process uploaded document and extract text
    Supports PDF and image files
    """
    # Create temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        file.save(tmp.name)
        file_path = tmp.name

    try:
        # Check file type
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext in ['.jpg', '.jpeg', '.png']:
            # Process image file
            text = process_image(file_path)
        elif file_ext == '.pdf':
            # Process PDF file
            text = process_pdf(file_path)
        else:
            raise ValueError("Unsupported file format")
            
        return text
    finally:
        # Clean up temporary file
        os.unlink(file_path)

def process_image(image_path):
    """Extract text from image using OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise Exception(f"Error processing image: {str(e)}")

def process_pdf(pdf_path):
    """Convert PDF to images and extract text"""
    try:
        # Convert PDF to images
        images = pdf2image.convert_from_path(pdf_path)
        
        # Extract text from each page
        text = ""
        for image in images:
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
            
        return text
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}") 