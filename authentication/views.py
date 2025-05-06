from rest_framework import status, generics, parsers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer, UserLoginSerializer

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'name': user.name,
                'serviceNumber': user.serviceNumber,
                'username': user.username,
                'code': user.plain_code,
                'email': user.email,
                'phone': user.phone
                
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = [AllowAny]  # Allow anyone to login
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            code = serializer.validated_data['code']
            
            user = authenticate(username=username, password=code)
            
            if user:
                token, created = Token.objects.get_or_create(user=user)

                response_data = {
                    'token': token.key,
                    'id': user.pk,
                    'name': user.name,
                    'serviceNumber': user.serviceNumber,
                    'username': user.username,
                    'code': user.plain_code,
                    'email': user.email,
                    'phone': user.phone
                }
                
                # Add profile image URL if it exists
                if hasattr(user, 'profile_image') and user.profile_image:
                    response_data['profile_image'] = request.build_absolute_uri(user.profile_image.url)
                else:
                    response_data['profile_image'] = None
                    
                return Response(response_data, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # Add profile_image URL if it exists
        if instance.profile_image:
            data['profile_image'] = request.build_absolute_uri(instance.profile_image.url)
        
        # Add plain_code to the response
        data['code'] = instance.plain_code
        
        return Response(data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Get updated instance
        updated_instance = self.get_object()
        response_data = serializer.data
        
        # Add profile_image URL if it exists
        if updated_instance.profile_image:
            response_data['profile_image'] = request.build_absolute_uri(updated_instance.profile_image.url)
        
        # Add plain_code to the response
        response_data['code'] = updated_instance.plain_code
        
        return Response(response_data)