from django.urls import path, include
from .views import ProductView
from rest_framework.routers import DefaultRouter


# from .views import  PurchasedItemViewSet


router = DefaultRouter()
router.register(r'', ProductView )



urlpatterns = [
    path('', include(router.urls)),
]