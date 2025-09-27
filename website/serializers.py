# website/serializers.py

from rest_framework import serializers
from .models import Product, AuthUser 
# NOTE: We removed the unused 'from django.contrib.auth.models import User'
#       and imported your custom AuthUser model.

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'productname', 'description', 'price']

class UserRegistrationSerializer(serializers.ModelSerializer):
    # These fields are used for input validation but are not saved directly to the database
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        # CRITICAL FIX: Reference the custom AuthUser model
        model = AuthUser 
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, attrs):
        # Validation for password match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        # Creating a user with the custom AuthUser model's create_user method
        # This handles hashing the password correctly and saving the instance.
        user = AuthUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'] # Pass raw password to the manager method
        )
        return user