from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect

from .services.contract_service import (
    get_contract_with_fields,
    get_all_contracts,
    get_user_contract_history,
    get_user_contract_history_by_id,
    delete_user_contract_history,
    get_contract_categories,
    get_contracts_by_category
)
from .services.generation_service import generate_contract_pdf 

from .serializers import (
    ContractFieldSerializer,
    GenerateContractSerializer,
    ContractListSerializer,
    ContractHistorySerializer,
    ContractCategorySerializer
)
from lexi.common.responses import success_response, error_response


class ContractListView(APIView):

    def get(self, request):
        contracts  = get_all_contracts()
        serializer = ContractListSerializer(contracts, many=True)
        return success_response("تم جلب العقود بنجاح", serializer.data)

class ContractDetailsView(APIView):

    def get(self, request, contract_id):
        try:
            contract = get_contract_with_fields(contract_id)
        except ValueError as e:
            return error_response(str(e))

        serializer = ContractFieldSerializer(
            contract.contract_fields.all(), many=True
        )
        return success_response(
            "تم جلب العقد بنجاح",
            {
                "id":     contract.id,
                "name":   contract.contract_name,
                "fields": serializer.data,
            },
        )

class GenerateContractView(APIView):

    def post(self, request):
        serializer = GenerateContractSerializer(data=request.data)

        if not serializer.is_valid():
            return error_response("بيانات غير صحيحة", serializer.errors)

        contract    = serializer.validated_data["contract"]
        fields_data = serializer.validated_data["fields"]

        try:
            pdf_url = generate_contract_pdf(request.user, contract.id, fields_data)
        except Exception as e:
            return error_response(f"فشل توليد العقد: {str(e)}")

        return success_response(
            "تم إنشاء العقد بنجاح",
            {
                "contract_name": contract.contract_name,
                "pdf_url":       pdf_url,
            },
        )

class ServeContractPDFView(APIView):

    def get(self, request):
        url = request.query_params.get("url")
        if not url:
            return error_response("لم يتم تمرير رابط الملف", status_code=400)
        return redirect(url)
    
class ContractHistoryListView(APIView):

    def get(self, request):

        history = get_user_contract_history(request.user)
        serializer = ContractHistorySerializer(history, many=True)

        return success_response(
            message="تم جلب سجل العقود بنجاح",
            data=serializer.data
        )
    
class ContractHistoryDetailView(APIView):

    def get(self, request, pk):

        history = get_user_contract_history_by_id(request.user, pk)

        if not history:
            return error_response(
                message="العقد غير موجود",
                status_code=404
            )

        serializer = ContractHistorySerializer(history)

        return success_response(
            message="تم جلب العقد بنجاح",
            data=serializer.data
        )
    
class ContractHistoryDeleteView(APIView):

    def delete(self, request, pk):

        deleted = delete_user_contract_history(request.user, pk)

        if not deleted:
            return error_response(
                message="العقد غير موجود",
                status_code=404
            )

        return success_response(
            message="تم حذف العقد بنجاح",
            data=None
        )
    
class ContractCategoriesView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):

        categories = get_contract_categories()

        serializer = ContractCategorySerializer(
            categories,
            many=True
        )

        return success_response(
            message="تم جلب التصنيفات بنجاح",
            data=serializer.data
        )
    
class ContractsByCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, category):

        contracts = get_contracts_by_category(category)

        serializer = ContractListSerializer(
            contracts,
            many=True
        )

        return success_response(
            message="تم جلب العقود بنجاح",
            data=serializer.data
        )