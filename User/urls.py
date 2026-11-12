
from django.urls import path
from . import views

app_name = 'User'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('forget-password/', views.forget_password, name='forget_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('change-password/', views.change_password, name='change_password'),
    path('logout/', views.user_logout, name='user_logout'),
    path('register-donor/', views.register_donor, name='register_donor'),
    path('request-blood/', views.request_blood, name='request_blood'),
]

