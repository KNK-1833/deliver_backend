from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class DeliveryRequest(models.Model):
    """配送依頼"""
    STATUS_CHOICES = [
        ('pending', '受付中'),
        ('assigned', 'アサイン済み'),
        ('in_progress', '配送中'),
        ('completed', '配送完了'),
        ('cancelled', 'キャンセル'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_deliveries', verbose_name='依頼者')
    title = models.CharField('案件名', max_length=200)
    description = models.TextField('詳細説明', blank=True)
    
    # 差出人情報
    sender_name = models.CharField('差出人名', max_length=100)
    sender_phone = models.CharField('差出人電話番号', max_length=20)
    sender_address = models.TextField('差出人住所')
    sender_lat = models.DecimalField('差出人緯度', max_digits=9, decimal_places=6, null=True, blank=True)
    sender_lng = models.DecimalField('差出人経度', max_digits=9, decimal_places=6, null=True, blank=True)
    
    # 配送先情報
    recipient_name = models.CharField('受取人名', max_length=100)
    recipient_phone = models.CharField('受取人電話番号', max_length=20)
    recipient_address = models.TextField('配送先住所')
    recipient_lat = models.DecimalField('配送先緯度', max_digits=9, decimal_places=6, null=True, blank=True)
    recipient_lng = models.DecimalField('配送先経度', max_digits=9, decimal_places=6, null=True, blank=True)
    
    # 荷物情報
    item_name = models.CharField('荷物名', max_length=200)
    item_quantity = models.PositiveIntegerField('数量', default=1)
    item_weight = models.DecimalField('重量（kg）', max_digits=5, decimal_places=2, null=True, blank=True)
    item_size = models.CharField('サイズ', max_length=100, blank=True)
    
    # 配送条件
    delivery_date = models.DateField('配送希望日')
    delivery_time = models.CharField('配送希望時間', max_length=50, blank=True)
    special_instructions = models.TextField('特別な指示', blank=True)
    
    # 料金
    request_amount = models.DecimalField('依頼金額', max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_fee = models.DecimalField('見積料金', max_digits=10, decimal_places=2, null=True, blank=True)
    final_fee = models.DecimalField('確定料金', max_digits=10, decimal_places=2, null=True, blank=True)
    
    # シードユーザー向け報酬設定
    driver_reward = models.DecimalField('ドライバー報酬', max_digits=10, decimal_places=2, null=True, blank=True)
    seed_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='managed_deliveries', 
                                 limit_choices_to={'user_type': 'seed'},
                                 verbose_name='管理シードユーザー')
    
    # ステータス
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = '配送依頼'
        verbose_name_plural = '配送依頼'
        ordering = ['-created_at']


class Assignment(models.Model):
    """配送アサイン"""
    STATUS_CHOICES = [
        ('accepted', '受諾'),
        ('in_progress', '配送中'),
        ('completed', '完了'),
        ('rejected', '拒否'),
    ]

    delivery_request = models.ForeignKey(DeliveryRequest, on_delete=models.CASCADE, related_name='assignments')
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments', limit_choices_to={'user_type': 'driver'})
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='assigned_requests',
                                   verbose_name='割り当て者')
    status = models.CharField('ステータス', max_length=20, choices=STATUS_CHOICES, default='accepted')
    
    # 配送時間記録
    pickup_time = models.DateTimeField('集荷時刻', null=True, blank=True)
    delivery_time = models.DateTimeField('配送時刻', null=True, blank=True)
    
    # 評価
    driver_rating = models.PositiveIntegerField('ドライバー評価', choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    requester_rating = models.PositiveIntegerField('依頼者評価', choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    
    notes = models.TextField('メモ', blank=True)
    
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'アサイン'
        verbose_name_plural = 'アサイン'
        ordering = ['-created_at']
