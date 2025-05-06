from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import pdfplumber
import pandas as pd
import os
from pathlib import Path
import mimetypes
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify allowed origins like ["http://localhost:4200"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def is_pdf(path: str) -> bool: #helper function to determine if file chosen is a pdf for security/data integrity purposes

    if Path(path).suffix.lower() != ".pdf":
        return False
    
    mtype, _ = mimetypes.guess_type(path)
    if mtype != "application/pdf":
        return False
    
    try:
        with open(path, "rb") as f:
            header = f.read(4)
        if header != b"%PDF":
            return False
    except (FileNotFoundError, IOError):
        return False
    # Passes all tests
    return True

        
    # except Exception as e:
    #     print(f"PDF validation error: {str(e)}")
    #     return False

@app.get("/")
def read_root():
    return {"message": "Welcome to the PDF to Excel API! Use the /convert endpoint to upload a PDF."}

@app.post("/convert")
async def convert_pdf_to_excel(file: UploadFile = File(...)):
    # Save the uploaded PDF file
    pdf_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    
    with open(pdf_path, "wb") as f:
        f.write(await file.read())

    if not is_pdf(pdf_path):
        os.remove(pdf_path)
        raise HTTPException(status_code=400, detail="Error: File Uploaded not a pdf")
    
    # Extract data from the PDF
    extracted_data = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            # Process the text to extract the data you need
            # Right now we're just appending the raw text
            extracted_data.append({"Page Text": text})

    # Convert the data to a DataFrame and save it as an Excel file
    df = pd.DataFrame(extracted_data)
    excel_path = pdf_path.replace(".pdf", ".xlsx")
    df.to_excel(excel_path, index=False)

    # Cleanup PDF file
    os.remove(pdf_path)

    # Return the Excel file to the client
    return FileResponse(excel_path, filename=f"{file.filename.replace('.pdf', '')}_data.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
