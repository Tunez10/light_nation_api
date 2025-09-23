from rest_framework import serializers
from .models import Product
from User.serializer import UserSerializer

class ProductSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # ⬅️ include user details in response

    class Meta:
        model = Product
        fields = '__all__'
