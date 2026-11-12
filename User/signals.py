import os
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(pre_save, sender=CustomUser)
def delete_old_profile_pic(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_profile = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return False

    old_file = old_profile.profile_image
    new_file = instance.profile_image
    
    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


