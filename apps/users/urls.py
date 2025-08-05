from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('driver-profile/', views.DriverProfileView.as_view(), name='driver-profile'),
    path('available-drivers/', views.available_drivers, name='available-drivers'),
    path('drivers/', views.all_drivers, name='all-drivers'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]