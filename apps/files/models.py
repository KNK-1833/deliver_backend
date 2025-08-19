from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class FileUpload(models.Model):
    """ファイルアップロード"""
    FILE_TYPE_CHOICES = [
        ('delivery_document', '配送帳票'),
        ('receipt', '受領書'),
        ('other', 'その他'),
    ]

    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files', verbose_name='アップロード者')
    # ファイルデータをBase64でテキストフィールドに保存（最大10MB想定）
    file_data = models.TextField('ファイルデータ（Base64）', blank=True, null=True)
    # 既存のfileフィールドは互換性のため残す（後で削除）
    file = models.FileField('ファイル（旧）', upload_to='uploads/%Y/%m/%d/', blank=True, null=True)
    original_name = models.CharField('元のファイル名', max_length=255)
    file_type = models.CharField('ファイルタイプ', max_length=20, choices=FILE_TYPE_CHOICES, default='delivery_document')
    file_size = models.PositiveIntegerField('ファイルサイズ（バイト）')
    mime_type = models.CharField('MIMEタイプ', max_length=100)
    
    # Claude API関連
    is_processed = models.BooleanField('Claude処理済み', default=False)
    claude_response = models.JSONField('Claude API レスポンス', null=True, blank=True)
    extracted_data = models.JSONField('抽出データ', null=True, blank=True)
    
    # 配送案件との関連（オプション）
    delivery_request = models.ForeignKey(
        'delivery.DeliveryRequest', 
        on_delete=models.CASCADE, 
        related_name='uploaded_files',
        null=True, 
        blank=True,
        verbose_name='関連配送案件'
    )
    
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    class Meta:
        verbose_name = 'ファイルアップロード'
        verbose_name_plural = 'ファイルアップロード'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_name} - {self.uploader.username}"
