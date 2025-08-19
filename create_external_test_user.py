#!/usr/bin/env python
import os
import django

# Django設定
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_external_test_user():
    User = get_user_model()
    
    # 外部テスト用ユーザー情報
    email = 'external.test@delivery-support.com'
    username = 'external_test_user'
    password = 'Zy1GZ53J'
    
    # ユーザー作成または取得
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': username,
            'user_type': 'seed',
            'is_verified': True,
            'is_staff': True,
            'is_superuser': False
        }
    )
    
    if created:
        user.set_password(password)
        user.save()
        print('✅ 外部テスト用ユーザーを作成しました')
    else:
        print('❌ ユーザーは既に存在します')
        # パスワードを更新
        user.set_password(password)
        user.user_type = 'seed'
        user.is_verified = True
        user.is_staff = True
        user.save()
        print('🔄 既存ユーザーの権限を更新しました')
    
    print('')
    print('🎯 テストアカウント情報:')
    print('=' * 50)
    print(f'📧 Email: {email}')
    print(f'👤 Username: {username}')
    print(f'🔑 Password: {password}')
    print(f'🔐 User Type: {user.user_type}')
    print(f'⚡ 権限: seed (全機能アクセス可能)')
    print('=' * 50)
    print('')
    print('🌐 アクセス先:')
    print('   ローカル: http://localhost:3000/')
    print('   本番環境: https://deliverfrontend-production.up.railway.app/')
    print('')
    print('📱 利用可能な機能:')
    print('   ✅ 全ユーザーのファイル表示・ダウンロード')
    print('   ✅ 全配送依頼の表示・管理')
    print('   ✅ ドライバー管理機能')
    print('   ✅ データインポート機能')
    print('   ✅ システム管理機能')
    print('   ✅ Claude AI ファイル処理')

if __name__ == '__main__':
    create_external_test_user()