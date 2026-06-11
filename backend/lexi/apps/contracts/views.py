from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .services.pdf_service import (
    create_contract_pdf
)

from .services.storage_service import (
    upload_pdf
)

from .serializers import (
    ContractFieldSerializer,
    GenerateContractSerializer
)

from .services.contract_service import (
    get_contract_with_fields,
    get_contract_by_id
)

from .services.generation_service import (
    fill_contract_template
)
from lexi.common.responses import (
    success_response,
    error_response,
)

class ContractDetailsView(APIView):
    def get(self, request, contract_id):

        try:
            contract = get_contract_with_fields(
                contract_id
            )

        except ValueError as e:
            return error_response(str(e))

        serializer = ContractFieldSerializer(
            contract.contract_fields.all(),
            many=True
        )

        data = {
            "id": contract.id,
            "name": contract.name,
            "fields": serializer.data
        }

        return success_response(
            "تم جلب العقد بنجاح",
            data
        )
    
class GenerateContractView(APIView):
    def post(self, request):

        serializer = GenerateContractSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return error_response(
                "بيانات غير صحيحة",
                serializer.errors
            )

        contract = serializer.validated_data["contract"]
        fields_data = serializer.validated_data["fields"]

        mapped_fields = {}

        for cf in contract.contract_fields.select_related("field"):
            label = cf.field.label
            key = cf.field.key

            value = fields_data.get(key)

            if value is not None:
                mapped_fields[label] = value

        final_contract = fill_contract_template(
        contract.content,
        mapped_fields
    )

        pdf_file = create_contract_pdf(
            contract.name,
            final_contract
        )

        pdf_url = upload_pdf(pdf_file)

        return success_response(
            "تم إنشاء العقد بنجاح",
            {
                "contract_name": contract.name,
                "pdf_url": pdf_url
            }
        )