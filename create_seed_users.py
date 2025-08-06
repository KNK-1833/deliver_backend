#!/usr/bin/env python
"""
本番環境用シードユーザー作成スクリプト
"""
import os
import sys
import django

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.users.models import DriverProfile

User = get_user_model()

def create_seed_users():
    """シードユーザーを作成"""
    
    # 管理者アカウント作成
    admin_email = 'admin@example.com'
    if not User.objects.filter(email=admin_email).exists():
        admin = User.objects.create_superuser(
            username='admin',
            email=admin_email,
            password='AdminTest123!',
            phone_number='090-0000-0000'
        )
        print(f'✅ 管理者アカウントを作成しました: {admin.email}')
    else:
        admin = User.objects.get(email=admin_email)
        admin.set_password('AdminTest123!')
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()
        print(f'🔄 管理者アカウントを更新しました: {admin.email}')

    # 事業者アカウント作成
    company_email = 'company@example.com'
    if not User.objects.filter(email=company_email).exists():
        company = User.objects.create_user(
            username='company_user',
            email=company_email,
            password='CompanyTest123!',
            phone_number='090-1111-1111',
            user_type='company'
        )
        print(f'✅ 事業者アカウントを作成しました: {company.email}')
    else:
        company = User.objects.get(email=company_email)
        company.set_password('CompanyTest123!')
        company.save()
        print(f'🔄 事業者アカウントを更新しました: {company.email}')

    # ドライバーアカウント作成
    driver_email = 'driver@example.com'
    if not User.objects.filter(email=driver_email).exists():
        driver = User.objects.create_user(
            username='driver_user',
            email=driver_email,
            password='DriverTest123!',
            phone_number='090-2222-2222',
            user_type='driver'
        )
        # ドライバープロフィール作成
        DriverProfile.objects.create(
            user=driver,
            vehicle_type='motorcycle',
            is_available=True
        )
        print(f'✅ ドライバーアカウントを作成しました: {driver.email}')
    else:
        driver = User.objects.get(email=driver_email)
        driver.set_password('DriverTest123!')
        driver.save()
        if not hasattr(driver, 'driver_profile'):
            DriverProfile.objects.create(
                user=driver,
                vehicle_type='motorcycle',
                is_available=True
            )
        print(f'🔄 ドライバーアカウントを更新しました: {driver.email}')

    print('\n' + '='*50)
    print('シードユーザー作成完了！')
    print('='*50)

if __name__ == '__main__':
    create_seed_users()