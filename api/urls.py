
from django.urls import path
from .views import CustomUserRegisterView, LoginView, ChangePasswordView, ForgetPasswordView, VerifyOTPView
from .views import DonorRegistrationView, BloodRequestView, AdminApiLoginView, UserProfileUpdateView
from .views import submit_public_review, moderate_review_action 
from .views import moderate_donor_action, moderate_request_action 
from .views import SystemSettingsUpdateAPI, MarkNotification, MarkAllNotifications
from django.urls import path

urlpatterns = [
    path('admin-login/', AdminApiLoginView.as_view(), name='admin_api_login'),
    path('register/', CustomUserRegisterView.as_view(), name='api_register'),
    path('login/', LoginView.as_view(), name='api_login'),
    path('forget-password/', ForgetPasswordView.as_view(), name='api_forget_password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='api_verify_otp'),
    path('change-password/', ChangePasswordView.as_view(), name='api_change_password'),
    path('reviews/submit/', submit_public_review, name='api_submit_review'),
    path('reviews/<int:review_id>/moderate/', moderate_review_action, name='api_moderate_review'),
    path('register-donor/', DonorRegistrationView.as_view(), name='api_donor_registration'),
    path('donors/<int:donor_id>/moderate/', moderate_donor_action, name='api_moderate_donor'),
    path('blood-request/', BloodRequestView.as_view(), name='api_blood_request'),
    path('requests/<int:request_id>/moderate/', moderate_request_action, name='api_moderate_request'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile_update'),
    path('settings/save/', SystemSettingsUpdateAPI.as_view(), name='system_save_settings'),
    path('notifications/<int:pk>/read/', MarkNotification.as_view(), name='mark-read'),
    path('notifications/mark-all-read/', MarkAllNotifications.as_view(), name='mark-all-read'),
]
