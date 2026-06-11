from ..models import Contract

def get_contract_with_fields(contract_id):
    contract = Contract.objects.filter(id=contract_id).prefetch_related(
        "contract_fields__field").first()

    if not contract:
        raise ValueError(
            "لم يتم العثور على العقد"
        )

    return contract

def get_contract_by_id(contract_id):
    contract = Contract.objects.filter(
        id=contract_id
    ).first()

    if not contract:
        raise ValueError(
            "لم يتم العثور على العقد"
        )

    return contract