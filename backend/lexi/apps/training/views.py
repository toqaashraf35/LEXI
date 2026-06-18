import os
import tempfile
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from .services.ai_service import run_full_analysis
from .services.cloudinary_service import upload_video
from .models import TrainingAnalysis
from .serializers import TrainingAnalysisSerializer


class TrainingAnalysisView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        video_file = request.FILES.get("video")

        if not video_file:
            return Response({
                "status": "error",
                "message": "يرجى رفع ملف الفيديو"
            }, status=status.HTTP_400_BAD_REQUEST)

        allowed_types = ["video/mp4", "video/avi", "video/mov", "video/mkv"]
        if video_file.content_type not in allowed_types:
            return Response({
                "status": "error",
                "message": "نوع الملف غير صالح. يُسمح فقط بملفات الفيديو"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Save temporarily
        suffix = os.path.splitext(video_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in video_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # Step 2: Upload to Cloudinary
            video_url = upload_video(tmp_path)

            # Step 3: Run AI analysis
            results = run_full_analysis(tmp_path)

            # Step 4: Save to DB
            analysis = TrainingAnalysis.objects.create(
                user=request.user,
                video_url=video_url,
                audio_analysis=results["audio_analysis"],
                body_analysis=results["body_analysis"],
                report=results["report"]
            )

            # Step 5: Return response
            return Response({
                "status": "success",
                "message": "تم تحليل الفيديو بنجاح",
                "data": {
                    "id": analysis.id,
                    "video_url": video_url,
                    "audio_analysis": results["audio_analysis"],
                    "body_analysis": results["body_analysis"],
                    "report": results["report"],
                    "created_at": analysis.created_at
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"فشل التحليل: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TrainingHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        analyses = TrainingAnalysis.objects.filter(
            user=request.user
        ).order_by('-created_at')

        serializer = TrainingAnalysisSerializer(analyses, many=True)

        return Response({
            "status": "success",
            "message": "تم جلب السجل بنجاح",
            "count": analyses.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
class TrainingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            analysis = TrainingAnalysis.objects.get(pk=pk, user=request.user)
        except TrainingAnalysis.DoesNotExist:
            return Response({
                "status": "error",
                "message": "التحليل غير موجود"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = TrainingAnalysisSerializer(analysis)
        return Response({
            "status": "success",
            "message": "تم جلب التحليل بنجاح",
            "data": serializer.data
        }, status=status.HTTP_200_OK)