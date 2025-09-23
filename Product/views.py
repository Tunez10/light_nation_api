from rest_framework import viewsets, permissions
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Product
from .serializer import ProductSerializer
from rest_framework.response import Response
from rest_framework.decorators import action

# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from .models import Product
# from .serializer import ProductSerializer
# from django.db.models import Q


class ProductView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]    
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_products(self, request):
        user_products = Product.objects.filter(user=request.user)
        serializer = self.get_serializer(user_products, many=True)
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated])
    def mark_as_sold(self, request, pk=None):
        product = self.get_object()

        # Only the owner can mark as sold
        if product.user != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        product.is_sold = True
        product.save()

        return Response({"status": "✅ Marked as sold"})
    

    # @api_view(['GET'])
    # def related_products(request, productname):         
    #     related = Product.objects.filter(
    #         Q(productname__icontains=productname)
    #     )[:6]  # You can adjust the number of related products returned
    #     serializer = ProductSerializer(related, many=True)
    #     return Response(serializer.data)
        



    
