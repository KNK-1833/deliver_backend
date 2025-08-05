import pytest
from django.urls import reverse
from rest_framework import status
from apps.delivery.models import DeliveryRequest, Assignment
from datetime import date


@pytest.mark.django_db
class TestDeliveryRequest:
    """配送依頼のテスト"""

    def test_create_delivery_request(self, authenticated_client, delivery_request_data):
        """配送依頼作成のテスト"""
        client, user = authenticated_client
        
        url = reverse('delivery-request-list')
        response = client.post(url, delivery_request_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == delivery_request_data['title']
        
        # データベース確認
        delivery_request = DeliveryRequest.objects.get(id=response.data['id'])
        assert delivery_request.requester == user
        assert delivery_request.status == 'pending'

    def test_list_delivery_requests_company(self, authenticated_client, delivery_request_data, create_user):
        """事業者の配送依頼一覧取得テスト"""
        client, user = authenticated_client
        
        # 配送依頼を作成
        DeliveryRequest.objects.create(requester=user, **delivery_request_data)
        
        # 他のユーザーの配送依頼も作成（表示されないはず）
        other_user = create_user()
        DeliveryRequest.objects.create(requester=other_user, **delivery_request_data)
        
        url = reverse('delivery-request-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1  # 自分の依頼のみ
        assert response.data['results'][0]['requester'] == str(user)

    def test_list_delivery_requests_driver(self, authenticated_driver_client, delivery_request_data, create_user):
        """ドライバーの配送依頼一覧取得テスト（受付中のみ）"""
        client, driver = authenticated_driver_client
        
        # 受付中の配送依頼を作成
        requester = create_user(email='requester@example.com')
        pending_request = DeliveryRequest.objects.create(
            requester=requester,
            status='pending',
            **delivery_request_data
        )
        
        # アサイン済みの配送依頼を作成（表示されないはず）
        assigned_request = DeliveryRequest.objects.create(
            requester=requester,
            status='assigned',
            **delivery_request_data
        )
        
        url = reverse('delivery-request-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1  # 受付中のみ
        assert response.data['results'][0]['id'] == pending_request.id

    def test_get_delivery_request_detail(self, authenticated_client, delivery_request_data):
        """配送依頼詳細取得のテスト"""
        client, user = authenticated_client
        
        delivery_request = DeliveryRequest.objects.create(
            requester=user,
            **delivery_request_data
        )
        
        url = reverse('delivery-request-detail', kwargs={'pk': delivery_request.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == delivery_request.id

    def test_update_delivery_request(self, authenticated_client, delivery_request_data):
        """配送依頼更新のテスト"""
        client, user = authenticated_client
        
        delivery_request = DeliveryRequest.objects.create(
            requester=user,
            **delivery_request_data
        )
        
        url = reverse('delivery-request-detail', kwargs={'pk': delivery_request.id})
        update_data = {'title': '更新されたタイトル'}
        response = client.patch(url, update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == '更新されたタイトル'

    def test_delete_delivery_request(self, authenticated_client, delivery_request_data):
        """配送依頼削除のテスト"""
        client, user = authenticated_client
        
        delivery_request = DeliveryRequest.objects.create(
            requester=user,
            **delivery_request_data
        )
        
        url = reverse('delivery-request-detail', kwargs={'pk': delivery_request.id})
        response = client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not DeliveryRequest.objects.filter(id=delivery_request.id).exists()

    def test_unauthorized_access_to_others_request(self, authenticated_client, delivery_request_data, create_user):
        """他人の配送依頼への不正アクセステスト"""
        client, user = authenticated_client
        
        # 他のユーザーの配送依頼を作成
        other_user = create_user()
        delivery_request = DeliveryRequest.objects.create(
            requester=other_user,
            **delivery_request_data
        )
        
        url = reverse('delivery-request-detail', kwargs={'pk': delivery_request.id})
        response = client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeliveryAssignment:
    """配送アサインのテスト"""

    def test_accept_delivery_success(self, authenticated_driver_client, delivery_request_data, create_user):
        """配送案件受諾の成功テスト"""
        driver_client, driver = authenticated_driver_client
        
        # 配送依頼を作成
        requester = create_user(email='requester@example.com')
        delivery_request = DeliveryRequest.objects.create(
            requester=requester,
            status='pending',
            **delivery_request_data
        )
        
        url = reverse('accept-delivery', kwargs={'pk': delivery_request.id})
        response = driver_client.post(url)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert 'assignment' in response.data
        assert 'message' in response.data
        
        # データベース確認
        assignment = Assignment.objects.get(id=response.data['assignment']['id'])
        assert assignment.driver == driver
        assert assignment.delivery_request == delivery_request
        assert assignment.status == 'accepted'
        
        # 配送依頼のステータス更新確認
        delivery_request.refresh_from_db()
        assert delivery_request.status == 'assigned'

    def test_accept_delivery_already_assigned(self, authenticated_driver_client, delivery_request_data, create_user):
        """既にアサイン済みの案件受諾失敗テスト"""
        driver_client, driver = authenticated_driver_client
        
        # 配送依頼を作成
        requester = create_user(email='requester@example.com')
        delivery_request = DeliveryRequest.objects.create(
            requester=requester,
            status='assigned',  # 既にアサイン済み
            **delivery_request_data
        )
        
        url = reverse('accept-delivery', kwargs={'pk': delivery_request.id})
        response = driver_client.post(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_accept_delivery_duplicate(self, authenticated_driver_client, delivery_request_data, create_user):
        """同じドライバーによる重複受諾失敗テスト"""
        driver_client, driver = authenticated_driver_client
        
        # 配送依頼を作成
        requester = create_user(email='requester@example.com')
        delivery_request = DeliveryRequest.objects.create(
            requester=requester,
            status='pending',
            **delivery_request_data
        )
        
        # 既にアサインを作成
        Assignment.objects.create(
            delivery_request=delivery_request,
            driver=driver,
            status='accepted'
        )
        
        url = reverse('accept-delivery', kwargs={'pk': delivery_request.id})
        response = driver_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_driver_accept_delivery(self, authenticated_client, delivery_request_data):
        """非ドライバーによる受諾失敗テスト"""
        client, user = authenticated_client
        
        delivery_request = DeliveryRequest.objects.create(
            requester=user,
            status='pending',
            **delivery_request_data
        )
        
        url = reverse('accept-delivery', kwargs={'pk': delivery_request.id})
        response = client.post(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_assignments_driver(self, authenticated_driver_client, delivery_request_data, create_user):
        """ドライバーのアサイン一覧取得テスト"""
        driver_client, driver = authenticated_driver_client
        
        # 配送依頼とアサインを作成
        requester = create_user(email='requester@example.com')
        delivery_request = DeliveryRequest.objects.create(
            requester=requester,
            **delivery_request_data
        )
        assignment = Assignment.objects.create(
            delivery_request=delivery_request,
            driver=driver,
            status='accepted'
        )
        
        url = reverse('assignment-list')
        response = driver_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == assignment.id

    def test_list_assignments_requester(self, authenticated_client, delivery_request_data, create_driver):
        """依頼者のアサイン一覧取得テスト"""
        client, user = authenticated_client
        
        # 配送依頼とアサインを作成
        driver = create_driver(email='driver@example.com')
        delivery_request = DeliveryRequest.objects.create(
            requester=user,
            **delivery_request_data
        )
        assignment = Assignment.objects.create(
            delivery_request=delivery_request,
            driver=driver,
            status='accepted'
        )
        
        url = reverse('assignment-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == assignment.id

    def test_update_assignment_status(self, authenticated_driver_client, delivery_request_data, create_user):
        """アサインステータス更新のテスト"""
        driver_client, driver = authenticated_driver_client
        
        # 配送依頼とアサインを作成
        requester = create_user(email='requester@example.com')
        delivery_request = DeliveryRequest.objects.create(
            requester=requester,
            **delivery_request_data
        )
        assignment = Assignment.objects.create(
            delivery_request=delivery_request,
            driver=driver,
            status='accepted'
        )
        
        url = reverse('update-assignment-status', kwargs={'pk': assignment.id})
        data = {'status': 'in_progress'}
        response = driver_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['assignment']['status'] == 'in_progress'
        
        # データベース確認
        assignment.refresh_from_db()
        delivery_request.refresh_from_db()
        assert assignment.status == 'in_progress'
        assert delivery_request.status == 'in_progress'

    def test_complete_assignment(self, authenticated_driver_client, delivery_request_data, create_user):
        """アサイン完了のテスト"""
        driver_client, driver = authenticated_driver_client
        
        # 配送依頼とアサインを作成
        requester = create_user(email='requester@example.com')
        delivery_request = DeliveryRequest.objects.create(
            requester=requester,
            **delivery_request_data
        )
        assignment = Assignment.objects.create(
            delivery_request=delivery_request,
            driver=driver,
            status='in_progress'
        )
        
        url = reverse('update-assignment-status', kwargs={'pk': assignment.id})
        data = {'status': 'completed'}
        response = driver_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['assignment']['status'] == 'completed'
        
        # データベース確認
        assignment.refresh_from_db()
        delivery_request.refresh_from_db()
        assert assignment.status == 'completed'
        assert delivery_request.status == 'completed'

    def test_invalid_status_update(self, authenticated_driver_client, delivery_request_data, create_user):
        """無効なステータス更新のテスト"""
        driver_client, driver = authenticated_driver_client
        
        # 配送依頼とアサインを作成
        requester = create_user(email='requester@example.com')
        delivery_request = DeliveryRequest.objects.create(
            requester=requester,
            **delivery_request_data
        )
        assignment = Assignment.objects.create(
            delivery_request=delivery_request,
            driver=driver,
            status='accepted'
        )
        
        url = reverse('update-assignment-status', kwargs={'pk': assignment.id})
        data = {'status': 'invalid_status'}
        response = driver_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_driver_status_update(self, authenticated_client, delivery_request_data, create_driver):
        """非ドライバーによるステータス更新失敗テスト"""
        client, user = authenticated_client
        
        # 配送依頼とアサインを作成
        driver = create_driver(email='driver@example.com')
        delivery_request = DeliveryRequest.objects.create(
            requester=user,
            **delivery_request_data
        )
        assignment = Assignment.objects.create(
            delivery_request=delivery_request,
            driver=driver,
            status='accepted'
        )
        
        url = reverse('update-assignment-status', kwargs={'pk': assignment.id})
        data = {'status': 'in_progress'}
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN