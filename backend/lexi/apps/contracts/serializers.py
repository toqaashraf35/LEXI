from rest_framework import serializers
from .models import Contract, ContractField
class ContractFieldSerializer(serializers.ModelSerializer):

    key = serializers.CharField(source="field.key")
    label = serializers.CharField(source="field.label")
    field_type = serializers.CharField(source="field.field_type")

    class Meta:

        model = ContractField

        fields = [
            "key",
            "label",
            "field_type",
            "required"
        ]

class GenerateContractSerializer(serializers.Serializer):

    contract_id = serializers.IntegerField()
    fields = serializers.DictField()

    def validate(self, data):

        contract_id = data.get("contract_id")
        fields = data.get("fields")

        try:
            contract = Contract.objects.get(id=contract_id)

        except Contract.DoesNotExist:
            raise serializers.ValidationError({
                "contract_id": "العقد غير موجود"
            })

        required_fields = contract.contract_fields.filter(
            required=True
        )

        errors = {}

        for contract_field in required_fields:

            key = contract_field.field.key

            if key not in fields or not str(fields[key]).strip():
                errors[key] = f"{contract_field.field.label} مطلوب"

        if errors:
            raise serializers.ValidationError(errors)

        data["contract"] = contract

        return data