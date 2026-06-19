from rest_framework import serializers
from .models import Contract, ContractField, ContractHistory
import re

class ContractFieldSerializer(serializers.ModelSerializer):
    key = serializers.CharField(source="field.key")
    label = serializers.CharField(source="field.label")
    type = serializers.CharField(source="field.type")

    class Meta:
        model = ContractField
        fields = [
            "key",
            "label",
            "type",
            "required",
            "order"
        ]

class ContractListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ["id", "contract_name"]

ARABIC_TEXT_REGEX = re.compile(r"^[\u0600-\u06FF\s\-،.,()]+$")


class GenerateContractSerializer(serializers.Serializer):
    contract_id = serializers.IntegerField()
    fields = serializers.DictField()

    def validate(self, data):
        contract_id = data["contract_id"]
        fields = data["fields"]

        try:
            contract = Contract.objects.prefetch_related(
                "contract_fields__field"
            ).get(id=contract_id)
        except Contract.DoesNotExist:
            raise serializers.ValidationError({
                "contract_id": "العقد غير موجود"
            })

        required_fields_map = {
            cf.field.key: {
                "label": cf.field.label,
                "field_type": getattr(cf.field, "field_type", "text")
            }
            for cf in contract.contract_fields.all()
        }

        missing = [
            info["label"]
            for key, info in required_fields_map.items()
            if key not in fields or fields[key] in [None, ""]
        ]

        if missing:
            raise serializers.ValidationError({
                "fields": f"حقول ناقصة: {', '.join(missing)}"
            })

        invalid_text_fields = []

        for key, value in fields.items():

            field_info = required_fields_map.get(key)
            if not field_info:
                continue

            field_type = field_info["field_type"]

            if field_type == "text":
                if not isinstance(value, str) or not ARABIC_TEXT_REGEX.match(value):
                    invalid_text_fields.append(field_info["label"])

        if invalid_text_fields:
            raise serializers.ValidationError({
                "fields": f"يجب أن تكون الحقول التالية باللغة العربية فقط: {', '.join(invalid_text_fields)}"
            })

        data["contract"] = contract
        data["required_fields_map"] = required_fields_map

        return data
    
class ContractHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractHistory
        fields = [
            "id",
            "user",
            "contract",
            "contract_name",
            "pdf_url",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
    
