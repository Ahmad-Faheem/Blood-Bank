
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import CustomUserRegisterSerializer, LoginSerializer, ChangePasswordSerializer, ForgetPasswordSerializer, VerifyOTPSerializer, UserProfileUpdateSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.utils.decorators import method_decorator
from rest_framework import status
from django.core.cache import cache
from User_Admin.models import Notification, SystemSetting
from User.models import BloodRequest
import random
import secrets
import json

class CustomUserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CustomUserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully!"}, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            redirect_to = request.query_params.get('next') or '/'
            return Response({
                "message": "Successfully Logged In !",
                "redirect_url": redirect_to,
                "user": {
                    "email": user.email,
                    "full_name": user.full_name
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ForgetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = str(random.randint(100000, 999999))
            
            cache_key = f"otp_reset_{email}"
            cache.set(cache_key, otp_code, timeout=300)  
            
            # 3. Handle sending the OTP email ( now show in terminal )
            print(f"------------ OTP for {email} is: {otp_code} ------------")
            
            # Optional: integration template for real deployment:
            # from django.core.mail import send_mail
            # send_mail(
            #     'Password Reset OTP',
            #     f'Your verification code is {otp_code}. It expires in 5 minutes.',
            #     'noreply@yoursite.com',
            #     [email],
            #     fail_silently=False,
            # )

            return Response("Verification OTP sent to your email", status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            cache.delete(f"otp_reset_{email}")
            reset_token = secrets.token_urlsafe(32)
            cache.set(f"verified_reset_token_{email}", reset_token, timeout=600)

            return Response({
                "message": "Identity verified successfully.",
                "email": email,
                "reset_token": reset_token  
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()
class ChangePasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email').lower()
        submitted_token = request.data.get('reset_token')

        if not email or not submitted_token:
            return Response({"confirm_password": "Missing validation requirements."}, status=status.HTTP_400_BAD_REQUEST)

        saved_token = cache.get(f"verified_reset_token_{email}")
        if not saved_token or saved_token != submitted_token:
            return Response({"confirm_password": "Unauthorized action or session expired."}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, email=email)
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save_password(user)
            cache.delete(f"verified_reset_token_{email}")
            return Response({"message": "Password Upadated successfully!"}, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, *args, **kwargs):
        serializer = UserProfileUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully!"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from .serializers import PublicReviewSerializer
@api_view(['POST'])
def submit_public_review(request):
    serializer = PublicReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()  
        return Response({"message": "Review submitted for moderation."}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from User.models import PublicReview
@csrf_exempt
def moderate_review_action(request, review_id):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        action = data.get('action')
        review_id = data.get('review_id')
        review = get_object_or_404(PublicReview, id=review_id)

        if action == 'approve':
            review.status = 'APPROVED'
        elif action == 'reject':
            review.status = 'REJECTED'
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        review.save()
        return JsonResponse({'success': True, 'message': f'Review {action}d successfully.'})
    return JsonResponse({'error': 'Method not allowed'}, status=405)

    
from .serializers import DonorRegistrationSerializer

class DonorRegistrationView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request, *args, **kwargs):
        serializer = DonorRegistrationSerializer(data=request.data, context={'request' : request})
        if serializer.is_valid():
            donor_instance = serializer.save(user=request.user)
            
            user_full_name = request.user.full_name.title()  
            blood_group_val = donor_instance.blood_group
            Notification.objects.create(
                notification_type='DONOR',
                title="New Donor Registered",
                message=f"placed by {user_full_name} [ {blood_group_val} Blood Group ]",
            )
            return Response({
                    "message": "Donor registered successfully!",
                    "donor_name": serializer.validated_data.get('donor_name')
                }, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from User.models import Donor
@csrf_exempt
def moderate_donor_action(request, donor_id):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        action = data.get('action')
        donor_id = data.get('donor_id')
        donor = get_object_or_404(Donor, id=donor_id)

        if action == 'approve':
            donor.status = 'APPROVED'
        elif action == 'reject':
            donor.status = 'REJECTED'
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
            
        donor.save()
        return JsonResponse({'success': True, 'message': f'Donor {action}d successfully.'})   
    return JsonResponse({'error': 'Method not allowed'}, status=405)


from .serializers import BloodRequestSerializer
from .blood_logic import get_available_donor_pool

class BloodRequestView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        serializer = BloodRequestSerializer(data=request.data, context={'request' : request})
        if serializer.is_valid():
            request_instance = serializer.save(user=request.user)

            blood_group_val = request_instance.blood_group
            units_required_val = request_instance.units_required
            urgency_time_val = request_instance.urgency_time
            Notification.objects.create(
                notification_type='REQUEST',
                title="Blood Donor Request",
                message=f"{blood_group_val} Blood Group {units_required_val} items needed in {urgency_time_val or 1} days",
            )

            available_donors = get_available_donor_pool(blood_group_val)
            available_units_count = available_donors.count()
            config = SystemSetting.load()
            shortage_detected = available_units_count < units_required_val
            if available_units_count <= config.low_threshold or shortage_detected:
                Notification.objects.create(
                    notification_type='INVENTORY',
                    title="Donor Shortage Alert!",
                    message=f"CRITICAL POOL: Type {blood_group_val} has only {available_units_count} available units left. System safety threshold is {config.low_threshold} units."
                )

            if config.auto_broadcast:
                units_needed = max(0, units_required_val - available_units_count)
                formatted_msg = config.broadcast_template.format(
                    BLOOD_GROUP=blood_group_val,
                    UNITS_REQUESTED=units_needed if units_needed > 0 else config.low_threshold
                )
                
                Notification.objects.create(
                    notification_type='REQUEST',
                    title=f"EMERGENCY BROADCAST Sent [{blood_group_val}]",
                    message=formatted_msg
                )
                
            return Response(
                {
                    "message": "Blood request submitted successfully!",
                    "request_id": serializer.data.get('id'),
                    "shortage_detected": shortage_detected
                }, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
from .blood_logic import check_global_inventory_thresholds

@csrf_exempt
def moderate_request_action(request, request_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        action = data.get('action')
        req_id = request_id or data.get('request_id')
        blood_req = get_object_or_404(BloodRequest, id=req_id)

        if action == 'approve':
            units_needed = blood_req.units_required
            available_pool = get_available_donor_pool(blood_req.blood_group)
            
            if available_pool.count() < units_needed:
                return JsonResponse({
                    'success': False,
                    'error': 'INSUFFICIENT_DONORS',
                    'message': f"Cannot dispatch blood. Request asks for {units_needed} units, but only {available_pool.count()} donors are currently available."
                }, status=422)

            assigned_donors_ids = list(available_pool.values_list('id', flat=True)[:units_needed])
            donors_to_dispatch = Donor.objects.filter(id__in=assigned_donors_ids)
            dispatched_names_log = []
            for donor in donors_to_dispatch:
                donor.status = 'DISPATCHED' 
                donor.save()
                dispatched_names_log.append(donor.donor_name.title())
                
            blood_req.status = 'APPROVED'
            blood_req.save()
            check_global_inventory_thresholds()

            return JsonResponse({
                'success': True,
                'message': f"Blood request approved successfully. Dispatched {len(donors_to_dispatch)} donor units.",
                'dispatched_donors': [d.donor_name.title() for d in donors_to_dispatch]
            }, status=200)

        elif action == 'reject':
            blood_req.status = 'REJECTED'
            blood_req.save()
            return JsonResponse({'success': True, 'message': 'Blood Request rejected successfully.'})

    except Exception as e:
        return JsonResponse({'error': f"System Execution Failure: {str(e)}"}, status=500)
    

from django.contrib.auth import login
from .serializers import AdminLoginSerializer 

@method_decorator(csrf_exempt, name='dispatch')
class AdminApiLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = AdminLoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user) 
            return Response({
                "status": "Success",
                "message": "Admin successfully logged In!",
                "redirect_url": '/User-Admin/dashboard/'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class SystemSettingsUpdateAPI(APIView):
    permission_classes = [IsAuthenticated]

    def check_permissions(self, request):
        super().check_permissions(request)
        if not (request.user.is_staff or request.user.is_superuser):
            self.permission_denied(request, message="Access Denied: Administrative privileges required.")

    def post(self, request, *args, **kwargs):
        try:
            settings_obj = SystemSetting.load()
            settings_obj.low_threshold = int(request.data.get('low_threshold', settings_obj.low_threshold))
            settings_obj.optimal_cap = int(request.data.get('optimal_cap', settings_obj.optimal_cap))
            settings_obj.expiration_alert_days = int(request.data.get('expiration_alert', settings_obj.expiration_alert_days))
            
            auto_broadcast_val = request.data.get('auto_broadcast')
            settings_obj.auto_broadcast = str(auto_broadcast_val).lower() in ['true', 'on', '1']
            settings_obj.broadcast_template = str(request.data.get('broadcast_template', settings_obj.broadcast_template)).strip()
            
            settings_obj.min_age = int(request.data.get('min_age', settings_obj.min_age))
            settings_obj.max_age = int(request.data.get('max_age', settings_obj.max_age))
            settings_obj.min_weight = float(request.data.get('min_weight', settings_obj.min_weight))
            settings_obj.surgery_deferral = int(request.data.get('surgery_deferral', settings_obj.surgery_deferral))
            settings_obj.deferral_period = int(request.data.get('deferral_period', settings_obj.deferral_period))
            settings_obj.hemoglobin_min = float(request.data.get('hemoglobin_min', settings_obj.hemoglobin_min))

            settings_obj.full_clean()
            settings_obj.save()

            return Response({
                "status": "Success",
                "message": "Global configurations saved and updated successfully!"
            }, status=status.HTTP_200_OK)

        except ValueError as val_err:
            return Response({"error": f"Invalid format processing data: {str(val_err)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

class MarkNotification(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        notification = get_object_or_404(Notification, pk=pk)
        notification.is_read = True
        notification.save()
        return Response({"status": "updated", "message": "Notification status checked read."}, status=200)

class MarkAllNotifications(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        Notification.objects.filter(is_read=False).update(is_read=True)
        return Response({"status": "updated", "message": "All items cleared successfully."}, status=200)
