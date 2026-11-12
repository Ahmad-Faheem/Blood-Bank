
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'Blood_Bank'

urlpatterns = [
    path('',views.home, name="home"),
    path('all-reviews/',views.All_Reviews, name="All_Reviews"),
    path('profile/',views.user_profile, name="user_profile"),
    path('User/', include('User.urls')),
    path('User-Admin/', include('User_Admin.urls')),
    path('api/v1/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

