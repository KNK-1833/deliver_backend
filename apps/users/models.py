from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """カスタムユーザーモデル"""
    email = models.EmailField('メールアドレス', unique=True)
    phone_number = models.CharField('電話番号', max_length=20, blank=True)
    user_type = models.CharField(
        'ユーザータイプ',
        max_length=20,
        choices=[
            ('driver', 'ドライバー'),
            ('company', '事業者'),
            ('seed', 'シードユーザー'),
        ],
        default='driver'
    )
    is_verified = models.BooleanField('認証済み', default=False)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = 'ユーザー'


class DriverProfile(models.Model):
    """ドライバープロフィール"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField('運転免許証番号', max_length=50, blank=True)
    vehicle_type = models.CharField(
        '車両タイプ',
        max_length=20,
        choices=[
            ('motorcycle', 'バイク'),
            ('light_truck', '軽トラック'),
            ('truck', 'トラック'),
        ],
        blank=True
    )
    vehicle_number = models.CharField('車両番号', max_length=20, blank=True)
    is_available = models.BooleanField('稼働可能', default=True)
    current_location_lat = models.DecimalField('現在位置（緯度）', max_digits=9, decimal_places=6, null=True, blank=True)
    current_location_lng = models.DecimalField('現在位置（経度）', max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'ドライバープロフィール'
        verbose_name_plural = 'ドライバープロフィール'
