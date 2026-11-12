
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from User.models import CustomUser, PublicReview
from User_Admin.models import SystemSetting
from django.core.validators import validate_email
from django.core.cache import cache
from datetime import date, timedelta
import re

User = get_user_model()
class CustomUserRegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'password']

    def validate_full_name(self, value):
        value = value.strip()
        if len(value) < 3 or not re.match(r'^[a-zA-Z\s]+$', value):
            raise serializers.ValidationError("Enter a Valid Name.")
        return value

    def validate_email(self, value):
        value = value.strip().lower()
        try :
            validate_email(value)
        except:
            raise serializers.ValidationError("Enter a valid Email Address.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This Email is already registered.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$', value):
            raise serializers.ValidationError("Must contain Upper, Lower, Digits & Symbols.")
        return value

    def create(self, validated_data):
        full_name = validated_data.pop('full_name').lower()
        email = validated_data.pop('email').lower()
        password = validated_data.pop('password')

        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate_email(self, value):
        value = value.strip().lower()
        try :
            validate_email(value)
        except:
            raise serializers.ValidationError("Enter a valid Email Address.")
        return value

    def validate(self, data):
        email = data.get('email').lower()
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)

            is_user = User.objects.filter(email=email, is_superuser=False).first()
            if not is_user:
                raise serializers.ValidationError({"email": "No User Account matches this email."})

            if not is_user.is_active:
                raise serializers.ValidationError({"email": "This user account has been deactivated."})  
        else:
            raise serializers.ValidationError({"password": "Must include both email and password."})

        data['user'] = user
        return data
    

User = get_user_model()
class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)

    def validate_email(self, value):
        value = value.strip().lower()
        if not re.match(r'^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Enter a valid Email Address.")
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No User found with this email address.")    
        return value


User = get_user_model()
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, min_length=6, max_length=6)

    def validate_otp(self, value):
        if not re.match(r'^\d{6}$', value):
            raise serializers.ValidationError("OTP must be a 6-digit number.")
        return value

    def validate(self, data):
        email = data.get('email').lower()
        otp = data.get('otp')

        cache_key = f"otp_reset_{email}"
        saved_otp = cache.get(cache_key)

        if not saved_otp:
            raise serializers.ValidationError({"otp" : "The verification code is expired."})

        if saved_otp != otp:
            raise serializers.ValidationError({"otp" : "Invalid verification code."})
        return data


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError({"new_password" : "Password must be at least 8 characters."})
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$', value):
            raise serializers.ValidationError({"new_password" : "Must contain Upper, Lower, Digits & Symbols."})
        return value

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError({"confirm_password" : "Passwords do not match."})
        return data

    def save_password(self, user):
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'profile_image', 'address', 'status', 'country_code', 'phone', 'description']

    def validate_full_name(self, value):
        if value:
            value = value.strip().lower()
            if len(value) < 3 or not re.match(r'^[a-zA-Z\s]+$', value):
                raise serializers.ValidationError("Enter a Valid Name.")
        return value

    def update(self, instance, validated_data):
        full_name = validated_data.pop('full_name', None)
        status = validated_data.pop('status', None)
        if full_name:
            name_parts = full_name.split(' ', 1)
            instance.first_name = name_parts[0]
            instance.last_name = name_parts[1] if len(name_parts) > 1 else ""
        if status:
            instance.is_active = True if status == 'ACTIVATE' else False
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PublicReviewSerializer(serializers.ModelSerializer):
    reviwer_name = serializers.CharField(source='reviewer_name'.lower())
    reviwer_email = serializers.CharField(source='reviewer_email'.lower(), required=False, allow_blank=True)
    reviwer_role = serializers.CharField(source='reviewer_role')
    reviwer_comment = serializers.CharField(source='comment')
    user_rating = serializers.IntegerField(source='rating', write_only=True) 

    class Meta:
        model = PublicReview
        fields = ['id', 'reviwer_name', 'reviwer_email', 'reviwer_role', 'user_rating', 'reviwer_comment', 'rating', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at', 'rating']

    def validate_reviwer_email(self, value):
        if value == "" or value is None:
            return None
        return value
    
    def validate_user_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

import os
from datetime import date
from User.models import Donor

class DonorRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = '__all__'
        read_only_fields = ['user', 'status']

    def validate_donor_name(self, value):
        value = value.strip().lower()
        if len(value) < 3 or len(value) > 80:
            raise serializers.ValidationError("Donor Name should be 3 - 80 characters.")
        return value

    def validate_date_of_birth(self, value):
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        system_rules = SystemSetting.load()
        if age < system_rules.min_age:
            raise serializers.ValidationError("Donor must be at least 18 years old.")
        if age > system_rules.max_age:
            raise serializers.ValidationError("Donor must be 55 years or under it.")
        return value

    def validate_email(self, value):
        request = self.context.get('request')
        value = value.strip().lower()
        if not re.match(r'^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Enter a Valid Email Address.")
        if request.user.email != value :
            raise serializers.ValidationError('The Email is not matched with user.')
        return value

    def validate_phone(self, value):
        value = value.strip()
        if not re.match(r'^\d{10,15}$', value):
            raise serializers.ValidationError("Only 10 - 15 digits are Allowed.")
        return value

    def validate_address(self, value):
        value = value.strip()
        if not re.match(r'^[a-zA-Z0-9\s,.-]+$', value):
            raise serializers.ValidationError("Invalid Address: Contains Forbidden Special Characters.")
        return value

    def validate_weight(self, value):
        system_rules = SystemSetting.load()
        try:
            weight_val = float(value)
        except (ValueError, TypeError):
            raise serializers.ValidationError("Weight must be a valid number.")   
        if not (system_rules.min_weight <= weight_val <= 200.0):
            raise serializers.ValidationError("Weight must be between 50 - 200 kg.")
        return round(weight_val, 2)

    def validate_donor_report(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        if ext not in valid_extensions:
            raise serializers.ValidationError("Unsupported file format. Only ( PDF, JPG, JPEG, PNG ) allowed.")

        max_size = 2 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("The donor report file size cannot exceed 2MB.")
        return value
    
    def validate(self, attrs):
        request = self.context.get('request')
        if not request or not request.user or not request.user.is_authenticated :
            raise serializers.ValidationError('User is not Authenticated ...')
        
        user = request.user
        hundred_days_ago = date.today() - timedelta(days=100)
        recent_donation_exists = Donor.objects.filter(
            user=user,
            created_at__date__gt=hundred_days_ago
        ).exists()

        if recent_donation_exists:
            raise serializers.ValidationError(
                "Access Denied: You have already donated blood within the last 100 days. For donor safety, you must wait 100 days between donations."
            )
        return attrs

    def validate(self, data):
        config = SystemSetting.load()
        
        if 'birth_date' in data:
            today = date.today()
            born = data['birth_date']
            age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        else:
            age = data.get('age')

        if age is not None:
            if age < config.min_age or age > config.max_age:
                raise serializers.ValidationError({
                    "age": f"Donor age must be between {config.min_age} and {config.max_age} years to register."
                })

        weight = data.get('weight')
        if weight is not None and float(weight) < float(config.min_weight):
            raise serializers.ValidationError({
                "weight": f"Donor weight does not meet the safety minimum threshold of {config.min_weight} kg."
            })
        return data

from User.models import BloodRequest
class BloodRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = '__all__'
        read_only_fields = ['user', 'status']

    def validate_email(self, value):
        request = self.context.get('request')
        value = value.strip().lower()
        if not re.match(r'^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-zA-Z]{2,}$', value):
            raise serializers.ValidationError("Enter a Valid Email Address.")
        if request.user.email != value :
            raise serializers.ValidationError('The Email is not matched with user.')
        return value
    
    def validate_patient_name(self, value):
        value = value.strip().lower()
        if len(value) < 3:
            raise serializers.ValidationError("Enter a Valid Name (At least 3 characters).")
        return value

    def validate_units_required(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Enter units between 1 - 10.")
        return value

    def validate_urgency_time(self, value):
        if value == "" or value is None:
            return None
        return value

    def validate_hospital_name(self, value):
        value = value.strip().lower()
        if len(value) < 5:
            raise serializers.ValidationError("Enter a Valid Hospital Name (At least 5 characters).")
        return value

    def validate_hospital_address(self, value):
        if not re.match(r'^[a-zA-Z0-9\s,.-]+$', value):
            raise serializers.ValidationError("Invalid Address: Contains Forbidden Special Characters.")
        return value

    def validate_doctor_name(self, value):
        value = value.strip().lower()
        if len(value) < 3:
            raise serializers.ValidationError("Enter a Valid Doctor Name.")
        return value

    def validate_doctor_phone(self, value):
        if not re.match(r'^\d{10,15}$', value):
            raise serializers.ValidationError("Only 10 - 15 digits are Allowed.")
        return value

    def validate_requester_name(self, value):
        value = value.strip().lower()
        if len(value) < 3:
            raise serializers.ValidationError("Enter a Valid Requester Name.")
        return value

    def validate_requester_phone(self, value):
        if not re.match(r'^\d{10,15}$', value):
            raise serializers.ValidationError("Only 10 - 15 digits are Allowed.")
        return value

    def validate_prescription_doc(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        if ext not in valid_extensions:
            raise serializers.ValidationError("Unsupported file format. Only ( PDF, JPG, JPEG, PNG ) allowed.")
        max_size = 2 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError("The prescription file size cannot exceed 2MB.")
        return value

    def validate(self, data):
        urgency_level = data.get('urgency_level')
        urgency_time = data.get('urgency_time')
        if urgency_level == 'plan':
            if urgency_time is None:
                raise serializers.ValidationError({"urgency_time": "Urgency Time is required when urgency level is set to Routine."})
            if urgency_time < 1 or urgency_time > 10:
                raise serializers.ValidationError({"urgency_time": "Urgency Time must be 1 - 10 Days."})
        else:
            data['urgency_time'] = None

        return data

User = get_user_model()
class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email').lower()
        password = data.get('password')

        admin_user = User.objects.filter(email=email, is_superuser=True).first()
        if not admin_user:
            raise serializers.ValidationError({"email": "No Admin account matches this email."})

        request = self.context.get('request')
        user = authenticate(request, username=email, password=password)
        if not user:
            raise serializers.ValidationError({"password": "Incorrect password verification failed."})

        if not (user.is_staff or user.is_superuser):
            raise serializers.ValidationError({"non_field_errors": "Access Denied: Not Admin Account."})

        data['user'] = user
        return data
    
