from ..models import Contract

def get_contract_with_fields(contract_id):

    contract = Contract.objects.filter(id=contract_id).prefetch_related(
        "contract_fields__field").first()

    if not contract:
        raise ValueError(
            "Contract not found"
        )

    return contract

from ..models import Contract


def get_contract_by_id(contract_id):

    contract = Contract.objects.filter(
        id=contract_id
    ).first()

    if not contract:
        raise ValueError(
            "Contract not found"
        )

    return contract