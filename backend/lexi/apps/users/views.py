from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import SignupSerializer
from .services.auth_service import create_user

class SignupView(APIView):

    def post(self, request):
        serializer = SignupSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "Validation failed",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        user = create_user(serializer.validated_data)

        return Response({
            "status": "success",
            "message": "User created successfully. Please verify your email.",
            "data": {
                "email": user.email,
                "full_name": user.full_name
            }
        }, status=status.HTTP_201_CREATED)