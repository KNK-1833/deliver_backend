from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import DeliveryRequest, Assignment
from .serializers import DeliveryRequestSerializer, AssignmentSerializer, DeliveryRequestCreateSerializer

User = get_user_model()


class DeliveryRequestListCreateView(generics.ListCreateAPIView):
    """配送依頼一覧・作成API"""
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DeliveryRequestCreateSerializer
        return DeliveryRequestSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'driver':
            # ドライバーは受付中の案件のみ表示
            return DeliveryRequest.objects.filter(status='pending')
        elif user.user_type == 'seed':
            # シードユーザーは全案件表示
            return DeliveryRequest.objects.all()
        else:
            # 事業者は自分の案件のみ表示
            return DeliveryRequest.objects.filter(requester=user)


class DeliveryRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """配送依頼詳細API"""
    serializer_class = DeliveryRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'driver':
            return DeliveryRequest.objects.all()
        elif user.user_type == 'seed':
            # シードユーザーは全案件編集可能
            return DeliveryRequest.objects.all()
        else:
            return DeliveryRequest.objects.filter(requester=user)


class AssignmentListView(generics.ListAPIView):
    """アサイン一覧API"""
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'driver':
            return Assignment.objects.filter(driver=user)
        elif user.user_type == 'seed':
            # シードユーザーは全アサイン表示
            return Assignment.objects.all()
        else:
            return Assignment.objects.filter(delivery_request__requester=user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_delivery(request, pk):
    """配送案件受諾API"""
    if request.user.user_type != 'driver':
        return Response({'error': 'ドライバーのみ受諾可能です。'}, status=status.HTTP_403_FORBIDDEN)

    try:
        delivery_request = DeliveryRequest.objects.get(pk=pk, status='pending')
    except DeliveryRequest.DoesNotExist:
        return Response({'error': '案件が見つからないか、既に受諾済みです。'}, status=status.HTTP_404_NOT_FOUND)

    # 既にアサインされているかチェック
    if Assignment.objects.filter(delivery_request=delivery_request, driver=request.user).exists():
        return Response({'error': '既に受諾済みです。'}, status=status.HTTP_400_BAD_REQUEST)

    # アサイン作成
    assignment = Assignment.objects.create(
        delivery_request=delivery_request,
        driver=request.user,
        status='accepted'
    )

    # 配送依頼のステータス更新
    delivery_request.status = 'assigned'
    delivery_request.save()

    serializer = AssignmentSerializer(assignment)
    return Response({
        'assignment': serializer.data,
        'message': '案件を受諾しました。'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_assignment_status(request, pk):
    """アサインステータス更新API"""
    if request.user.user_type != 'driver':
        return Response({'error': 'ドライバーのみ更新可能です。'}, status=status.HTTP_403_FORBIDDEN)

    try:
        assignment = Assignment.objects.get(pk=pk, driver=request.user)
    except Assignment.DoesNotExist:
        return Response({'error': 'アサインが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if new_status not in ['in_progress', 'completed']:
        return Response({'error': '無効なステータスです。'}, status=status.HTTP_400_BAD_REQUEST)

    assignment.status = new_status
    assignment.save()

    # 配送依頼のステータスも更新
    if new_status == 'in_progress':
        assignment.delivery_request.status = 'in_progress'
    elif new_status == 'completed':
        assignment.delivery_request.status = 'completed'
    
    assignment.delivery_request.save()

    serializer = AssignmentSerializer(assignment)
    return Response({
        'assignment': serializer.data,
        'message': 'ステータスを更新しました。'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_driver_reward(request, pk):
    """ドライバー報酬設定API（シードユーザー用）"""
    if request.user.user_type != 'seed':
        return Response({'error': 'シードユーザーのみ設定可能です。'}, status=status.HTTP_403_FORBIDDEN)

    try:
        delivery_request = DeliveryRequest.objects.get(pk=pk)
    except DeliveryRequest.DoesNotExist:
        return Response({'error': '案件が見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

    driver_reward = request.data.get('driver_reward')
    if not driver_reward:
        return Response({'error': '報酬額が必要です。'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        driver_reward = float(driver_reward)
        if driver_reward <= 0:
            return Response({'error': '報酬額は正の数である必要があります。'}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({'error': '無効な報酬額です。'}, status=status.HTTP_400_BAD_REQUEST)

    # 報酬額設定
    delivery_request.driver_reward = driver_reward
    delivery_request.seed_user = request.user
    delivery_request.save()

    serializer = DeliveryRequestSerializer(delivery_request)
    return Response({
        'delivery_request': serializer.data,
        'message': 'ドライバー報酬を設定しました。'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_driver_to_request(request, pk):
    """ドライバーを案件に直接割り当てるAPI（シードユーザー・事業者用）"""
    # シードユーザーまたは自分の案件の事業者のみ実行可能
    if request.user.user_type not in ['seed', 'company']:
        return Response({'error': '権限がありません。'}, status=status.HTTP_403_FORBIDDEN)

    try:
        delivery_request = DeliveryRequest.objects.get(pk=pk)
        
        # 事業者の場合は自分の案件のみ
        if request.user.user_type == 'company' and delivery_request.requester != request.user:
            return Response({'error': '自分の案件のみ割り当て可能です。'}, status=status.HTTP_403_FORBIDDEN)
            
    except DeliveryRequest.DoesNotExist:
        return Response({'error': '案件が見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

    # pendingまたはassigned状態のみ対応
    if delivery_request.status not in ['pending', 'assigned']:
        return Response({'error': '処理済みまたはキャンセル済みの案件は変更できません。'}, status=status.HTTP_400_BAD_REQUEST)

    driver_id = request.data.get('driver_id')
    if not driver_id:
        return Response({'error': 'ドライバーIDが必要です。'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        driver = User.objects.get(id=driver_id, user_type='driver')
    except User.DoesNotExist:
        return Response({'error': '指定されたドライバーが見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

    # 既にアサインされている場合の処理
    existing_assignment = Assignment.objects.filter(
        delivery_request=delivery_request, 
        status__in=['accepted', 'in_progress']
    ).first()
    
    if existing_assignment:
        # 同じドライバーが既にアサインされている場合
        if existing_assignment.driver.id == driver.id:
            return Response({'error': 'このドライバーは既にアサイン済みです。'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 別のドライバーがアサインされている場合は既存のアサインメントを無効化
        existing_assignment.status = 'cancelled'
        existing_assignment.save()

    # 新しいアサイン作成
    assignment = Assignment.objects.create(
        delivery_request=delivery_request,
        driver=driver,
        assigned_by=request.user,
        status='accepted'
    )

    # 配送依頼のステータス更新
    delivery_request.status = 'assigned'
    delivery_request.save()

    serializer = AssignmentSerializer(assignment)
    return Response({
        'assignment': serializer.data,
        'message': f'ドライバー {driver.get_full_name() or driver.username} を案件に割り当てました。'
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def available_drivers(request):
    """利用可能なドライバー一覧API"""
    if request.user.user_type not in ['seed', 'company']:
        return Response({'error': '権限がありません。'}, status=status.HTTP_403_FORBIDDEN)

    # 利用可能なドライバーを取得（DriverProfile の is_available が True のもの）
    from apps.users.models import DriverProfile
    from apps.users.serializers import DriverProfileMiniSerializer
    
    available_driver_profiles = DriverProfile.objects.filter(
        is_available=True
    ).select_related('user')
    
    drivers_data = []
    for profile in available_driver_profiles:
        drivers_data.append({
            'id': profile.user.id,
            'username': profile.user.username,
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'email': profile.user.email,
            'phone_number': profile.user.phone_number,
            'license_number': profile.license_number,
            'vehicle_type': profile.vehicle_type,
            'vehicle_number': profile.vehicle_number,
            'is_available': profile.is_available
        })

    return Response(drivers_data)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_request_status(request, pk):
    """配送依頼ステータス更新API（シードユーザー・事業者用）"""
    # シードユーザーまたは自分の案件の事業者のみ実行可能
    if request.user.user_type not in ['seed', 'company']:
        return Response({'error': '権限がありません。'}, status=status.HTTP_403_FORBIDDEN)

    try:
        delivery_request = DeliveryRequest.objects.get(pk=pk)
        
        # 事業者の場合は自分の案件のみ
        if request.user.user_type == 'company' and delivery_request.requester != request.user:
            return Response({'error': '自分の案件のみ更新可能です。'}, status=status.HTTP_403_FORBIDDEN)
            
    except DeliveryRequest.DoesNotExist:
        return Response({'error': '案件が見つかりません。'}, status=status.HTTP_404_NOT_FOUND)

    new_status = request.data.get('status')
    if not new_status:
        return Response({'error': 'ステータスが必要です。'}, status=status.HTTP_400_BAD_REQUEST)

    # ステータスの妥当性チェック
    valid_statuses = ['pending', 'assigned', 'in_progress', 'completed', 'cancelled']
    if new_status not in valid_statuses:
        return Response({'error': '無効なステータスです。'}, status=status.HTTP_400_BAD_REQUEST)

    # ステータス更新
    delivery_request.status = new_status
    delivery_request.save()

    serializer = DeliveryRequestSerializer(delivery_request)
    return Response({
        'delivery_request': serializer.data,
        'message': 'ステータスを更新しました。'
    })
