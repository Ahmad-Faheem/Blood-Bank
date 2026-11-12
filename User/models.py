
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.conf import settings

def rename_profile_image(instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        unique_id = uuid.uuid4().hex[:10]
        safe_name = "".join(c for c in instance.full_name if c.isalnum()).strip()
        return os.path.join('profile-pics/', f"{safe_name}_{unique_id}{ext}")

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not(extra_fields.get('is_staff')) or not(extra_fields.get('is_superuser')):
            raise ValueError("SuperUser must have admin permissions")
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    STATUS_CHOICES = [
        ('ACTIVATE', 'ACTIVATE'),
        ('DEACTIVATE', 'DEACTIVATE')
    ]
    username = None
    email = models.EmailField(unique=True)
    profile_image = models.ImageField(upload_to=rename_profile_image, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country_code = models.CharField(max_length=10, default='+92', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='ACTIVATE')
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 
    objects = CustomUserManager()
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.email
    
    
class PublicReview(models.Model):
    ROLE_CHOICES = [
        ('Blood Donor', 'Blood Donor'),
        ('Patient / Recipient', 'Patient / Recipient'),
        ('Hospital Representative', 'Hospital Representative'),
    ]

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]

    reviewer_name = models.CharField(max_length=255)
    reviewer_role = models.CharField(max_length=50, choices=ROLE_CHOICES)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    reviewer_email = models.EmailField(max_length=254, blank=True, null=True, default="anonymous@email.com")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer_name} ({self.reviewer_role}) - {self.rating} Stars"

import os
import uuid

def rename_donor_report(instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        unique_id = uuid.uuid4().hex[:10]
        safe_name = "".join(c for c in instance.donor_name if c.isalnum()).strip()
        return os.path.join('donor-reports/', f"{safe_name}_{unique_id}{ext}")

class Donor(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'), 
    ]
    
    DONATION_TYPE_CHOICES = [
        ('whole', 'Whole Blood'),
        ('Platelets', 'Platelets'),
        ('Plasma', 'Plasma'),
        ('red cells', 'Red Blood Cells'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A Positive'), ('A-', 'A Negative'),
        ('B+', 'B Positive'), ('B-', 'B Negative'),
        ('AB+', 'AB Positive'), ('AB-', 'AB Negative'),
        ('O+', 'O Positive'), ('O-', 'O Negative'),
    ]

    DONOR_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('DISPATCHED', 'Dispatched')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='donor_history')
    donor_name = models.CharField(max_length=80)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    medical_notes = models.TextField(blank=True, null=True)

    email = models.EmailField(unique=False)
    country_code = models.CharField(max_length=5)
    phone = models.CharField(max_length=15)
    address = models.TextField()
        
    donor_report = models.FileField(upload_to=rename_donor_report)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    weight = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(50.0), MaxValueValidator(200.0)])
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPE_CHOICES, default='whole')
    status = models.CharField(max_length=20, choices=DONOR_STATUS_CHOICES, default='PENDING' )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor_name} ({self.blood_group})"


def rename_prescription_doc(instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        unique_id = uuid.uuid4().hex[:10]
        safe_name = "".join(c for c in instance.patient_name if c.isalnum()).strip()
        return os.path.join('requester-prescriptions/', f"{safe_name}_{unique_id}{ext}")

class BloodRequest(models.Model):
    URGENCY_CHOICES = [
        ('plan', 'Routine (planned)'),
        ('urgent', 'Urgent (4-6 Hours)'),
        ('emergency', 'Emergency (Immediate)'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]

    BLOOD_TYPE_CHOICES = [
        ('whole', 'Whole Blood'),
        ('prbc', 'Red Cells (PRBC)'),
        ('platelets', 'Platelets'),
        ('plasma', 'Plasma'),
    ]

    RELATION_CHOICES = [
        ('self', 'Self'),
        ('relative', 'Family/Relative'),
        ('staff', 'Hospital Staff'),
    ]
    
    REQUEST_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='blood_requests')
    patient_name = models.CharField(max_length=150)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES)
    blood_type = models.CharField(max_length=15, choices=BLOOD_TYPE_CHOICES)
    units_required = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    urgency_level = models.CharField(max_length=15, choices=URGENCY_CHOICES)
    urgency_time = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], blank=True, null=True)
    email = models.EmailField(unique=False)

    hospital_name = models.CharField(max_length=200)
    hospital_address = models.TextField()
    doctor_name = models.CharField(max_length=150)
    doctor_phone = models.CharField(max_length=15)

    requester_name = models.CharField(max_length=150)
    requester_phone = models.CharField(max_length=15)
    relationship = models.CharField(max_length=15, choices=RELATION_CHOICES)

    prescription_doc = models.FileField(upload_to=rename_prescription_doc)
    additional_notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='PENDING' )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request for {self.patient_name} - {self.blood_group} ({self.units_required} Units)"

