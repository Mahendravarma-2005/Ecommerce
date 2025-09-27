from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from website.models import Product
from website.serializers import ProductSerializer, UserRegistrationSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated]) # CORRECTED: Using the proper class name
def get_products(request):
    """
    Return all products as JSON.
    """
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticatedOrReadOnly]) # This is correct
def add_product(request):
    """
    Add a new product via API.
    """
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticatedOrReadOnly]) # This is correct
def update_product(request, pk):
    """
    Update an existing product via API.
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticatedOrReadOnly]) # This is correct
def delete_product(request, pk):
    """
    Delete a product via API.
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)