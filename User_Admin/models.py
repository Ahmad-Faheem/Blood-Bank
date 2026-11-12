
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class SystemSetting(models.Model):
    low_threshold = models.IntegerField(default=5, validators=[MinValueValidator(1)])
    optimal_cap = models.IntegerField(default=50, validators=[MinValueValidator(10)])
    expiration_alert_days = models.IntegerField(default=7, validators=[MinValueValidator(2)])

    auto_broadcast = models.BooleanField(default=True)
    broadcast_template = models.TextField(
        default="URGENT: The Regional Blood Bank has a critical shortage of blood type {BLOOD_GROUP}. "
                "If you are eligible to donate, please visit our clinic immediately or reply to reserve a slot."
    )

    min_age = models.IntegerField(default=18, validators=[MinValueValidator(16), MaxValueValidator(100)])
    max_age = models.IntegerField(default=65, validators=[MinValueValidator(50), MaxValueValidator(100)])
    min_weight = models.DecimalField(max_digits=5, decimal_places=2, default=50.0, validators=[MinValueValidator(45.0)])
    surgery_deferral = models.IntegerField(default=6, validators=[MinValueValidator(0)])
    deferral_period = models.IntegerField(default=4, validators=[MinValueValidator(0)])
    hemoglobin_min = models.DecimalField(max_digits=3, decimal_places=1, default=12.5, validators=[MinValueValidator(0.0)])

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "System Setting"
        verbose_name_plural = "System Settings"

    def save(self, *args, **kwargs):
        """Enforce the singleton pattern: always keep id=1."""
        self.pk = 1
        super(SystemSetting, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        """Safely fetch settings instance or generate defaults if missing."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"System Configurations (Last Updated: {self.updated_at.strftime('%Y-%m-%d %H:%M')})"


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('DONOR', 'New Donor Registered'),
        ('REQUEST', 'Blood Donor Request'),
        ('INVENTORY', 'Low Stock Alert'),
    ]

    notification_type = models.CharField(max_length=15, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} - Read: {self.is_read}"
