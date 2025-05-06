from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True, max_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'serviceNumber', 'email', 'phone', 'code', 'profile_image']
        extra_kwargs = {
            'username': {'read_only': True},
        }
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    code = serializers.CharField(max_length=6, write_only=True)
