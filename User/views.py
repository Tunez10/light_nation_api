from rest_framework import status, viewsets, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from .serializer import UserSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from django.core.mail import send_mail
from .models import EmailVerificationToken

from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import status


from rest_framework.views import APIView
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .serializer import PasswordResetRequestSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str  # or force_text if using older Django






User = get_user_model()

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.is_active = False
        user.save()

        token = EmailVerificationToken.objects.create(user=user)

        send_mail(
            subject="Verify Your Kingdomhub account",
            message=f"Your verification token is: {token.token}",
            from_email='Kingdomhub <peterekene162@gmail.com>', 
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({"detail": "User registered. Check your email for verification token."}, status=status.HTTP_201_CREATED)
    

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_email(self, request):
        token = request.data.get('token')
        try:
            token_obj = EmailVerificationToken.objects.get(token=token, is_used=False)
            token_obj.is_used = True
            token_obj.save()

            user = token_obj.user
            user.is_active = True
            user.save()

            return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)
        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

    

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        user_serializer = UserSerializer(user)

        return Response({
            'data': user_serializer.data,  # User info
            'access_token': access_token,  # JWT Access Token
            'refresh_token': refresh_token  # JWT Refresh Token
        }, status=status.HTTP_200_OK)
    


    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
            try:
                refresh_token = request.data.get("refresh_token")

                if not refresh_token:
                    return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

                token = RefreshToken(refresh_token)
                token.blacklist()  # 🚫 This marks the token as blacklisted

                return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)

            except TokenError as e:
                return Response({"detail": "Token is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)
            

    @action(detail=False, methods=['get', 'put'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user

        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        elif request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)





class RequestPasswordResetEmail(APIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]


    @swagger_auto_schema(request_body=PasswordResetRequestSerializer)
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Respond success anyway for security
                return Response({'success': 'If your email exists, a reset link has been sent.'}, status=status.HTTP_200_OK)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)

            reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"
            print(f"✅ Reset URL: {reset_url}")

            send_mail(
                subject='Reset your password',
                message=f'Click the link to reset your password: {reset_url}',
                from_email='Kingdomhub <peterekene162@gmail.com>',
                recipient_list=[user.email],
            )

            return Response({'success': 'If your email exists, a reset link has been sent.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class PasswordResetConfirm(APIView):
    permission_classes = [AllowAny]


    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['uid', 'token', 'new_password'],
            properties={
                'uid': openapi.Schema(type=openapi.TYPE_STRING, description='Base64-encoded user ID'),
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Password reset token'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password')
            }
        ),
        responses={
            200: 'Password has been reset successfully',
            400: 'Invalid input or token'
        }
    )
    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not uidb64 or not token or not new_password:
            return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))  # ✅ decode base64 to raw UID
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()

        if not token_generator.check_token(user, token):
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({'message': 'Password has been reset successfully'}, status=status.HTTP_200_OK)






