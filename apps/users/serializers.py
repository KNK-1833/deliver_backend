from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import DriverProfile

User = get_user_model()


class DriverProfileMiniSerializer(serializers.ModelSerializer):
    """ドライバープロフィール簡易シリアライザー"""
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    
    class Meta:
        model = DriverProfile
        fields = ['id', 'license_number', 'vehicle_type', 'vehicle_number', 'phone_number', 'is_available']


class UserSerializer(serializers.ModelSerializer):
    """ユーザーシリアライザー"""
    password = serializers.CharField(write_only=True)
    driver_profile = DriverProfileMiniSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'phone_number', 'user_type', 'is_verified', 'driver_profile', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class DriverProfileSerializer(serializers.ModelSerializer):
    """ドライバープロフィールシリアライザー"""
    user = UserSerializer(read_only=True)

    class Meta:
        model = DriverProfile
        fields = '__all__'


class UserRegistrationSerializer(serializers.ModelSerializer):
    """ユーザー登録用シリアライザー"""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone_number', 'user_type']

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("パスワードが一致しません。")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # ドライバーの場合はプロフィールを作成
        if user.user_type == 'driver':
            DriverProfile.objects.create(user=user)
        
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """カスタムJWTトークン取得シリアライザー（emailログイン対応）"""
    username_field = User.USERNAME_FIELD
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # emailフィールドを追加
        self.fields[self.username_field] = serializers.EmailField()
        self.fields['email'] = serializers.EmailField()

    def validate(self, attrs):
        # emailでログインの場合
        email = attrs.get('email') or attrs.get('username')
        password = attrs.get('password')

        if email and password:
            # emailでユーザーを検索してusernameを取得
            try:
                user = User.objects.get(email=email)
                # usernameフィールドを設定
                attrs[self.username_field] = user.username
                attrs['username'] = user.username
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    'No active account found with the given credentials'
                )

        # 親クラスのvalidateを呼び出し
        result = super().validate(attrs)
        
        # ユーザー情報をレスポンスに追加
        if hasattr(self, 'user') and self.user:
            user_data = UserSerializer(self.user).data
            result['user'] = user_data
            
        return result