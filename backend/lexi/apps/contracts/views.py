from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import (
    ContractFieldSerializer,
    GenerateContractSerializer
)

from .services.contract_service import (
    get_contract_with_fields,
    get_contract_by_id
)
from .services.pdf_service import (
    generate_contract_pdf
)
from .services.generation_service import (
    fill_contract_template
)
from lexi.common.responses import (
    success_response,
    error_response,
    get_first_error
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
            "Contract fetched successfully",
            data
        )
    
class GenerateContractView(APIView):

    permission_classes = [IsAuthenticated]
    def post(self, request):

        serializer = GenerateContractSerializer(
            data=request.data
        )

        if not serializer.is_valid():

            return error_response(
                get_first_error(
                    serializer.errors
                ),
                serializer.errors
            )

        contract_id = serializer.validated_data[
            "contract_id"
        ]

        inputs = serializer.validated_data[
            "inputs"
        ]

        try:

            contract = get_contract_by_id(
                contract_id
            )

        except ValueError as e:

            return error_response(str(e))

        final_content = fill_contract_template(
            contract.content,
            inputs
        )

        pdf_path = generate_contract_pdf(
            final_content
        )

        return success_response(
            "Contract generated successfully",
            {
                "pdf": pdf_path
            }
        )