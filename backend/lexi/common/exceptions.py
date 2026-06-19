from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import traceback
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    print("🔥 ERROR OCCURRED:")
    print(str(exc))
    traceback.print_exc()

    response = exception_handler(exc, context)

    if response is None:
        return Response(
            {
                "status": "error",
                "message": "حدث خطأ غير متوقع"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if response.status_code == 401:
        return Response(
            {
                "status": "error",
                "message": "يجب تسجيل الدخول أولاً"
            },
            status=status.HTTP_401_UNAUTHORIZED
        )

    if response.status_code == 403:
        return Response(
            {
                "status": "error",
                "message": "ليس لديك صلاحية للوصول"
            },
            status=status.HTTP_403_FORBIDDEN
        )

    if response.status_code == 404:
        return Response(
            {
                "status": "error",
                "message": "المورد غير موجود"
            },
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(
        {
            "status": "error",
            "message": response.data
        },
        status=response.status_code
    )