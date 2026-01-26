from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, RegisterSerializer

class LoginView(APIView):
    """
    POST /api/auth/login/ — вход в систему
    """
    def post(self, request):
        print(f"DEBUG-login: Received data: {request.data}")
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            print(f"DEBUG: Serializer valid, user: {serializer.validated_data}")
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        print(f"DEBUG: Serializer errors: {serializer.errors}")
        return Response(
            {'error': 'Неверные учётные данные'},
            status=status.HTTP_400_BAD_REQUEST
        )


class RegisterView(APIView):
    """
    POST /api/auth/register/ — регистрация
    """
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            print("Данные валидны")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)  # покажет ошибки валидации
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """
    POST /api/auth/logout/ — выход из системы
    Аннулирует токен JWT пользователя.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            else:
                # Если refresh_token не передан, возвращаем 400
                return Response(
                    {'error': 'refresh_token обязателен'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'error': 'Ошибка при выходе'},
                status=status.HTTP_400_BAD_REQUEST
            )

