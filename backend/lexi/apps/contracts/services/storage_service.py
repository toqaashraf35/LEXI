import cloudinary.uploader
import uuid

def upload_pdf(pdf_file):
    pdf_file.seek(0)
    result = cloudinary.uploader.upload(
        pdf_file,
        resource_type="raw",
        format="pdf",
        type="upload",
        folder="contracts",
        public_id=str(uuid.uuid4())
    )

    return result["secure_url"]