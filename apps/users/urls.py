from django.urls import path
from apps.users import views


app_name = 'users'

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('change-password/', views.change_password, name='change_password'),
    path('change-mode/', views.change_mode, name='change_mode'),
    path('api-token/', views.api_token, name='api_token'),
    path('regenerate-token/', views.regenerate_token, name='regenerate_token'),
]
