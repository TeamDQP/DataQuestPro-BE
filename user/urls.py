from . import views
from django.urls import path, include

app_name = 'user'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('login/refresh/', views.CustomTokenRefreshView.as_view(),
         name='token_refresh'),
    path('validate-jwt/', views.JWTValidationView.as_view(), name='validate-jwt'),
    path('verify/<int:pk>', views.EmailVerification.as_view(), name='verify'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('update/', views.UserUpdate.as_view(), name='update'),
    path('delete/', views.UserDelete.as_view(), name='delete'),
    path('profile/write/', views.ProfileWrite.as_view(), name='profile-write'),
    path('profile/read/', views.ProfileRead.as_view(), name='profile-read'),
    path('profile/update/', views.ProfileUpdate.as_view(), name='profile-update'),
    path('profile/delete/', views.ProfileDelete.as_view(), name='profile-delete'),
]
