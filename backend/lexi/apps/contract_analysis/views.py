# lexi/apps/contract_analysis/views.py
import os
import tempfile
import requests
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .services.cloudinary_service import upload_contract
from .models import ContractAnalysis


class ContractAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({
                'status': 'error',
                'message': 'يرجى رفع ملف العقد'
            }, status=status.HTTP_400_BAD_REQUEST)

        allowed_types = [
            'application/pdf',
            'image/png', 'image/jpeg',
            'image/tiff', 'image/bmp'
        ]
        if file.content_type not in allowed_types:
            return Response({
                'status': 'error',
                'message': 'نوع الملف غير صالح. يُسمح فقط بـ PDF أو صور'
            }, status=status.HTTP_400_BAD_REQUEST)

        contract_type    = request.data.get('contract_type', 'عام')
        contract_subtype = request.data.get('contract_subtype', 'عام')

        suffix = os.path.splitext(file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # Step 1: Upload to Cloudinary
            file_url = upload_contract(tmp_path, file.name)

            # Step 2: Call FastAPI for AI analysis
            with open(tmp_path, 'rb') as f:
                ai_response = requests.post(
                    f"{settings.AI_SERVICE_URL}/contract-analysis/analyze",
                    files={'file': (file.name, f, file.content_type)},
                    data={
                        'contract_type': contract_type,
                        'contract_subtype': contract_subtype
                    },
                    timeout=300
                )

            if ai_response.status_code != 200:
                raise Exception(f"AI service error: {ai_response.text}")

            result = ai_response.json()
            analyzed = result['contract_analysis']
            summary  = result['summary']

            # Step 3: Save to DB
            contract_analysis = ContractAnalysis.objects.create(
                user             = request.user,
                file_url         = file_url,
                file_name        = file.name,
                contract_type    = contract_type,
                contract_subtype = contract_subtype,
                total_clauses    = summary['total_clauses'],
                risky_clauses    = summary['risky_clauses'],
                safe_clauses     = summary['safe_clauses'],
                result           = analyzed,
            )

            return Response({
                'status':  'success',
                'message': 'تم تحليل العقد بنجاح',
                'data': {
                    'id':                contract_analysis.id,
                    'file_url':          file_url,
                    'file_name':         file.name,
                    'contract_type':     contract_type,
                    'contract_subtype':  contract_subtype,
                    'contract_analysis': analyzed,
                    'summary':           summary,
                    'created_at':        contract_analysis.created_at,
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status':  'error',
                'message': f'فشل التحليل: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class ContractAnalysisHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        analyses = ContractAnalysis.objects.filter(user=request.user)
        data = [
            {
                'id':               a.id,
                'file_url':         a.file_url,
                'file_name':        a.file_name,
                'contract_type':    a.contract_type,
                'contract_subtype': a.contract_subtype,
                'total_clauses':    a.total_clauses,
                'risky_clauses':    a.risky_clauses,
                'safe_clauses':     a.safe_clauses,
                'created_at':       a.created_at,
            }
            for a in analyses
        ]
        return Response({
            'status':  'success',
            'message': 'تم جلب السجل بنجاح',
            'count':   len(data),
            'data':    data,
        }, status=status.HTTP_200_OK)


class ContractAnalysisDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            analysis = ContractAnalysis.objects.get(pk=pk, user=request.user)
        except ContractAnalysis.DoesNotExist:
            return Response({
                'status':  'error',
                'message': 'التحليل غير موجود'
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'status':  'success',
            'message': 'تم جلب التحليل بنجاح',
            'data': {
                'id':                analysis.id,
                'file_url':          analysis.file_url,
                'file_name':         analysis.file_name,
                'contract_type':     analysis.contract_type,
                'contract_subtype':  analysis.contract_subtype,
                'contract_analysis': analysis.result,
                'summary': {
                    'total_clauses': analysis.total_clauses,
                    'risky_clauses': analysis.risky_clauses,
                    'safe_clauses':  analysis.safe_clauses,
                },
                'created_at': analysis.created_at,
            }
        }, status=status.HTTP_200_OK)


class ContractAnalysisDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            analysis = ContractAnalysis.objects.get(pk=pk, user=request.user)
        except ContractAnalysis.DoesNotExist:
            return Response({
                'status':  'error',
                'message': 'التحليل غير موجود'
            }, status=status.HTTP_404_NOT_FOUND)

        analysis.delete()
        return Response({
            'status':  'success',
            'message': 'تم حذف التحليل بنجاح'
        }, status=status.HTTP_200_OK)
    
class ContractAnalysisDeleteAllView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        deleted_count, _ = ContractAnalysis.objects.filter(
            user=request.user
        ).delete()

        return Response({
            'status':  'success',
            'message': 'تم حذف جميع سجلات تحليل العقود بنجاح',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)