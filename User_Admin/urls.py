
from django.urls import path
from . import views

app_name = 'User_Admin'

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.dashboard , name='dashboard'),
    path('notifications/', views.NotificationsView.as_view(), name='notifications'),
    path('donors/', views.donors , name='donors'),
    path('requests/', views.requests , name='requests'),
    path('reports/', views.reports , name='reports'),
    path('reviews/', views.reviews , name='reviews'),
    path('settings/', views.SettingsTemplateView.as_view(), name='settings'),
    path('logout/', views.admin_logout, name='admin_logout'),
]
