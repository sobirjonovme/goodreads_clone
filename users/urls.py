from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    LogOutView,
    ProfileView,
    ProfileUpdateView
)


app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('profile/<str:username>', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile-edit'),
]
