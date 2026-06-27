# lexi/apps/contract_analysis/services/cloudinary_service.py
import cloudinary
import cloudinary.uploader
from django.conf import settings


def upload_contract(file_path: str, file_name: str) -> str:
    """
    Upload a contract file (PDF or image) to Cloudinary.
    Returns the secure URL.
    """
    # PDFs and images use resource_type="auto"
    result = cloudinary.uploader.upload(
        file_path,
        resource_type="auto",
        folder="lexi/contracts",
        public_id=file_name.rsplit('.', 1)[0],  # filename without extension
        overwrite=False,
    )

    secure_url = result.get("secure_url")
    if not secure_url:
        raise ValueError("Cloudinary upload succeeded but returned no URL")

    return secure_url