from rest_framework.response import Response

def error_response(message, errors=None, status_code=400):
    return Response({
        "status": "error",
        "message": message,
        "errors": errors
    }, status=status_code)

def success_response(message, data=None, status_code=200):
    return Response({
        "status": "success",
        "message": message,
        "data": data
    }, status=status_code)

def get_first_error(errors):
    return list(errors.values())[0][0]
