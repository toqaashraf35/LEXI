import uuid
import tempfile
from django.conf import settings
from .supabase_client import supabase

def upload_pdf(pdf_file):
    pdf_file.seek(0)

    result = supabase.storage.from_("contracts").upload(
        file=pdf_file.read(),   
        path=f"{uuid.uuid4()}.pdf",
        file_options={"content-type": "application/pdf"}
    )

    return supabase.storage.from_("contracts").get_public_url(result.path)

