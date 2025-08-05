from django.urls import path
from . import views

urlpatterns = [
    path('uploads/', views.FileUploadListCreateView.as_view(), name='file-upload-list'),
    path('uploads/<int:pk>/', views.FileUploadDetailView.as_view(), name='file-upload-detail'),
    path('uploads/<int:pk>/process/', views.process_with_claude, name='process-with-claude'),
    path('uploads/<int:pk>/create-delivery/', views.create_delivery_from_file, name='create-delivery-from-file'),
]