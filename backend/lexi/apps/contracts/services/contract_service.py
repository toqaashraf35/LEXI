from ..models import Contract, ContractHistory


def get_contract_with_fields(contract_id):
    contract = Contract.objects.filter(
        id=contract_id
    ).prefetch_related("contract_fields__field").first()

    if not contract:
        raise ValueError("لم يتم العثور على العقد")

    return contract


def get_all_contracts():
    return Contract.objects.all()

def get_user_contract_history(user):
    return ContractHistory.objects.filter(
        user=user
    ).order_by("-created_at")

def get_user_contract_history_by_id(user, history_id: int):
    try:
        return ContractHistory.objects.get(
            id=history_id,
            user=user
        )
    except ContractHistory.DoesNotExist:
        return None

def delete_user_contract_history(user, history_id: int) -> bool:
    history = get_user_contract_history_by_id(user, history_id)

    if not history:
        return False

    history.delete()
    return True