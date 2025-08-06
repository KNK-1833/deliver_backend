from django.contrib import admin
from .models import FileUpload


@admin.register(FileUpload)
class FileUploadAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'uploader', 'file_type', 'is_processed', 'created_at']
    list_filter = ['file_type', 'is_processed', 'created_at']
    search_fields = ['original_name', 'uploader__username']
    readonly_fields = ['created_at', 'updated_at', 'file_size', 'mime_type']
