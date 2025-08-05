from rest_framework import serializers
from .models import FileUpload


class UploaderSerializer(serializers.Serializer):
    """アップローダー情報シリアライザー"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    user_type = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class FileUploadSerializer(serializers.ModelSerializer):
    """ファイルアップロードシリアライザー"""
    uploader = UploaderSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = FileUpload
        fields = '__all__'
        read_only_fields = ['uploader', 'original_name', 'file_size', 'mime_type', 'is_processed', 'claude_response', 'extracted_data']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    def create(self, validated_data):
        validated_data['uploader'] = self.context['request'].user
        
        # ファイル情報を自動設定
        file_obj = validated_data['file']
        validated_data['original_name'] = file_obj.name
        validated_data['file_size'] = file_obj.size
        validated_data['mime_type'] = getattr(file_obj, 'content_type', 'application/octet-stream')
        
        return super().create(validated_data)