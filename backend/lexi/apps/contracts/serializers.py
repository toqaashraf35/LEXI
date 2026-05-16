from rest_framework import serializers
from .models import ContractField

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

class GenerateContractSerializer(
    serializers.Serializer
):

    contract_id = serializers.IntegerField()

    inputs = serializers.DictField()