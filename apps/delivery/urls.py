from django.urls import path
from . import views

urlpatterns = [
    path('requests/', views.DeliveryRequestListCreateView.as_view(), name='delivery-request-list'),
    path('requests/<int:pk>/', views.DeliveryRequestDetailView.as_view(), name='delivery-request-detail'),
    path('assignments/', views.AssignmentListView.as_view(), name='assignment-list'),
    path('requests/<int:pk>/accept/', views.accept_delivery, name='accept-delivery'),
    path('requests/<int:pk>/assign/', views.assign_driver_reward, name='assign-driver-reward'),
    path('requests/<int:pk>/assign-driver/', views.assign_driver_to_request, name='assign-driver-to-request'),
    path('assignments/<int:pk>/status/', views.update_assignment_status, name='update-assignment-status'),
    path('requests/<int:pk>/status/', views.update_request_status, name='update-request-status'),
    path('available-drivers/', views.available_drivers, name='available-drivers'),
]