from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
import os

from services.training_service import run_full_analysis

router = APIRouter(prefix="/training", tags=["Training"])


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = run_full_analysis(tmp_path)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)