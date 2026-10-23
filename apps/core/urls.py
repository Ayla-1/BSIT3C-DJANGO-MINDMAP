from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('home/', views.home, name='dashboard'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('test-login/', views.test_login_page, name='test_login'),
    path('test-dropdown/', views.test_dropdown, name='test_dropdown'),
    path('profile/', views.user_profile, name='user_profile'),
]