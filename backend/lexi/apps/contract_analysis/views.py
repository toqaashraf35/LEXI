# lexi/apps/contract_analysis/views.py
import os
import tempfile
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status

from .services.cloudinary_service import upload_contract
from .services.extraction_service import extract_text
from .services.clause_service import extract_clauses_with_llm, chunk_text
from .services.analysis_service import predict_clause
from .services.explanation_service import explain_clause_risk
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
            # Step 1: Upload to Cloudinary first
            file_url = upload_contract(tmp_path, file.name)

            # Step 2: Extract text from temp file
            raw_text = extract_text(tmp_path)

            # Step 3: Extract clauses via LLM
            chunks = chunk_text(raw_text)
            all_clauses = []
            clause_counter = 1
            for chunk in chunks:
                extracted = extract_clauses_with_llm(chunk)
                for c in extracted:
                    all_clauses.append({
                        'clause_id': clause_counter,
                        'text': c.get('text', '').strip()
                    })
                    clause_counter += 1

            # Step 4: Predict + explain each clause
            analyzed = []
            for c in all_clauses:
                prediction = predict_clause(
                    c['text'], contract_type, contract_subtype
                )
                explanation = risk_level = recommendation = None
                is_risky = prediction['risk'] == 1

                if is_risky:
                    parties = prediction['risk_parties'] if prediction['risk_parties'] else ['جميع الأطراف']
                    llm_result     = explain_clause_risk(
                        clause       = c['text'],
                        parties      = parties,
                        risk_type_ar = prediction['risk_type'],
                        )
                    explanation    = llm_result['explanation']
                    risk_level     = llm_result['risk_level']
                    recommendation = llm_result['recommendation']
                else:
                    parties = []

                analyzed.append({
                    'clause_id':      c['clause_id'],
                    'clause_text':    c['text'],
                    'risk':           'نعم' if prediction['risk'] == 1 else 'لا',
                    'risk_type':      prediction['risk_type'] if is_risky else None,
                    'risk_parties':   parties,
                    'explanation':    explanation,
                    'risk_level':     risk_level,
                    'recommendation': recommendation,
                })

            total = len(analyzed)
            risky = sum(1 for c in analyzed if c['risk'] == 'نعم')

            # Step 5: Save to DB
            contract_analysis = ContractAnalysis.objects.create(
                user             = request.user,
                file_url         = file_url,
                file_name        = file.name,
                contract_type    = contract_type,
                contract_subtype = contract_subtype,
                total_clauses    = total,
                risky_clauses    = risky,
                safe_clauses     = total - risky,
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
                    'summary': {
                        'total_clauses': total,
                        'risky_clauses': risky,
                        'safe_clauses':  total - risky,
                    },
                    'created_at': contract_analysis.created_at,
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