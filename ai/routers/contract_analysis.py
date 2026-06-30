from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
import tempfile
import os

from services.contract_analysis_service import analyze_contract

router = APIRouter(prefix="/contract-analysis", tags=["Contract Analysis"])


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    contract_type: str = Form(default="عام"),
    contract_subtype: str = Form(default="عام"),
):
    # Save uploaded file temporarily
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = analyze_contract(tmp_path, contract_type, contract_subtype)
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)