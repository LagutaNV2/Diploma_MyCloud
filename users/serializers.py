# users/serializers.py
from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_admin', 'storage_path']
        read_only_fields = ['id', 'storage_path']

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'is_admin']
        extra_kwargs = {
            'is_admin': {'default': False}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
