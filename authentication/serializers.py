from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True, max_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'serviceNumber', 'email', 'phone', 'code', 'profile_image']
        
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    code = serializers.CharField(max_length=6, write_only=True)

# New serializers for two-step login
class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)

class CodeVerificationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    code = serializers.CharField(max_length=6)


from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True, max_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'serviceNumber', 'email', 'phone', 'code', 'profile_image']
        
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    code = serializers.CharField(max_length=6, write_only=True)

# New serializers for two-step login
class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)

class CodeVerificationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50)
    code = serializers.CharField(max_length=6)

# New serializer for listing users
class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'serviceNumber', 'email', 'phone', 'profile_image']
