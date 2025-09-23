from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet

from django.urls import path
from .views import RequestPasswordResetEmail, PasswordResetConfirm

router = DefaultRouter()
router.register(r'', UserViewSet)

urlpatterns = [
    path('userApi/', include(router.urls)),                     # Login/Register via ViewSet
    path('userApi/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 👈 New: Token refresh

    path('request-reset-password/', RequestPasswordResetEmail.as_view(), name='request-reset-password'),
    path('reset-password/', PasswordResetConfirm.as_view(), name='reset-password'),
]
