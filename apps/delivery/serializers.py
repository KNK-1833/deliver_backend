from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DeliveryRequest, Assignment

User = get_user_model()


class DeliveryRequestSerializer(serializers.ModelSerializer):
    """配送依頼シリアライザー"""
    requester = serializers.StringRelatedField(read_only=True)
    assigned_driver = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryRequest
        fields = '__all__'
        read_only_fields = ['requester']

    def get_assigned_driver(self, obj):
        """割り当てられたドライバー情報を取得"""
        assignment = obj.assignments.filter(status__in=['accepted', 'in_progress', 'completed']).first()
        if assignment:
            driver = assignment.driver
            return {
                'id': driver.id,
                'username': driver.username,
                'first_name': driver.first_name,
                'last_name': driver.last_name,
                'full_name': driver.get_full_name() or driver.username
            }
        return None

    def create(self, validated_data):
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)


class DriverMiniSerializer(serializers.ModelSerializer):
    """ドライバー簡易シリアライザー"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class DeliveryRequestMiniSerializer(serializers.ModelSerializer):
    """配送依頼簡易シリアライザー（Assignment用）"""
    class Meta:
        model = DeliveryRequest
        fields = ['id', 'title', 'request_amount', 'driver_reward', 'delivery_date']


class AssignmentSerializer(serializers.ModelSerializer):
    """アサインシリアライザー"""
    delivery_request = DeliveryRequestMiniSerializer(read_only=True)
    driver = DriverMiniSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['driver']


class AssignmentDetailSerializer(serializers.ModelSerializer):
    """アサイン詳細シリアライザー（フル情報）"""
    delivery_request = DeliveryRequestSerializer(read_only=True)
    driver = DriverMiniSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'
        read_only_fields = ['driver']


class DeliveryRequestCreateSerializer(serializers.ModelSerializer):
    """配送依頼作成用シリアライザー"""
    
    class Meta:
        model = DeliveryRequest
        exclude = ['requester', 'status']

    def create(self, validated_data):
        validated_data['requester'] = self.context['request'].user
        return super().create(validated_data)