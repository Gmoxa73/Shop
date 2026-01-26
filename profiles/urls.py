from django.urls import path
from . import views


urlpatterns = [
    path('profile/', views.user_profile, name='user_profile'),
    path('update-avatar/', views.update_avatar, name='update_avatar'),
]