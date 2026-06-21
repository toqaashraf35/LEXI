from ..models import Contract, ContractHistory
from .mapping_service import build_key_to_label_map
from .template_service import fill_contract_template
from .pdf_service import generate_pdf_bytes
from .storage_service import upload_pdf
import io


def generate_contract_pdf(user, contract_id: int, fields_data: dict) -> str:

    contract = (
        Contract.objects
        .prefetch_related('contract_fields__field')
        .get(id=contract_id)
    )

    key_label_map = build_key_to_label_map(contract)

    converted_data = {
        key_label_map.get(k, k): v
        for k, v in fields_data.items()
    }

    filled_content = fill_contract_template(
        template=contract.contract_content,
        data=converted_data,
    )

    pdf_bytes = generate_pdf_bytes(
        contract_name=contract.contract_name,
        filled_content=filled_content,
    )

    pdf_file = io.BytesIO(pdf_bytes)
    pdf_url = upload_pdf(pdf_file)

    ContractHistory.objects.create(
        user=user,
        contract=contract,
        contract_name=contract.contract_name,
        pdf_url=pdf_url
    )

    return pdf_url