from django.contrib import admin
from .models import DeliveryRequest, Assignment


@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'requester', 'status', 'delivery_date', 'created_at']
    list_filter = ['status', 'delivery_date', 'created_at']
    search_fields = ['title', 'sender_name', 'recipient_name', 'item_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['delivery_request', 'driver', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['delivery_request__title', 'driver__username']
    readonly_fields = ['created_at', 'updated_at']
