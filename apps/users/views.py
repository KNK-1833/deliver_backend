from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import get_user_model
from .models import DriverProfile
from .serializers import UserSerializer, DriverProfileSerializer, UserRegistrationSerializer, CustomTokenObtainPairSerializer

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """ユーザー登録API"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        user_serializer = UserSerializer(user)
        return Response({
            'user': user_serializer.data,
            'message': 'ユーザー登録が完了しました。'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """ユーザープロフィール取得・更新API"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class DriverProfileView(generics.RetrieveUpdateAPIView):
    """ドライバープロフィール取得・更新API"""
    serializer_class = DriverProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        driver_profile, created = DriverProfile.objects.get_or_create(user=self.request.user)
        return driver_profile

    def get(self, request, *args, **kwargs):
        if request.user.user_type != 'driver':
            return Response({'error': 'ドライバーではありません。'}, status=status.HTTP_403_FORBIDDEN)
        return super().get(request, *args, **kwargs)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_drivers(request):
    """稼働可能なドライバー一覧API"""
    drivers = DriverProfile.objects.filter(is_available=True).select_related('user')
    serializer = DriverProfileSerializer(drivers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def all_drivers(request):
    """全ドライバー一覧API（シードユーザー用）"""
    if request.user.user_type != 'seed':
        return Response({'error': 'シードユーザーではありません。'}, status=status.HTTP_403_FORBIDDEN)
    
    drivers = User.objects.filter(user_type='driver').select_related('driver_profile')
    serializer = UserSerializer(drivers, many=True)
    return Response(serializer.data)


class CustomTokenObtainPairView(TokenObtainPairView):
    """カスタムJWTトークン取得ビュー（emailログイン対応）"""
    
    def post(self, request, *args, **kwargs):
        # emailが送信された場合、usernameに変換
        if 'email' in request.data and 'username' not in request.data:
            try:
                user = User.objects.get(email=request.data['email'])
                # リクエストデータを変更
                mutable_data = request.data.copy()
                mutable_data['username'] = user.username
                request._full_data = mutable_data
            except User.DoesNotExist:
                return Response(
                    {'detail': '認証情報が正しくありません。'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        # 元のpost処理を実行
        response = super().post(request, *args, **kwargs)
        
        # 成功時にユーザー情報を追加
        if response.status_code == 200:
            try:
                email = request.data.get('email') or request.data.get('username')
                if '@' in email:  # emailの場合
                    user = User.objects.get(email=email)
                else:  # usernameの場合
                    user = User.objects.get(username=email)
                
                user_data = UserSerializer(user).data
                response.data['user'] = user_data
            except User.DoesNotExist:
                pass
        
        return response
