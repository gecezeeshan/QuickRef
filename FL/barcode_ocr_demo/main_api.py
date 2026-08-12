# API placeholder
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import shutil, tempfile, os
from app.pipeline import process_image

app = FastAPI(title="Barcode + OCR API")

@app.post("/process")
async def process(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    try:
        res = process_image(tmp_path, out_dir="output")
        return JSONResponse(res)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
