from datetime import date, timedelta
from django.db.models import Count
from django.apps import apps

COMPATIBLE_DONORS = {
    'O-': ['O-'], 
    'O+': ['O-', 'O+'], 
    'A-': ['O-', 'A-'],
    'A+': ['O-', 'O+', 'A-', 'A+'], 
    'B-': ['O-', 'B-'],
    'B+': ['O-', 'O+', 'B-', 'B+'], 
    'AB-': ['O-', 'A-', 'B-', 'AB-'],
    'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
}

def get_available_donor_pool(blood_group):
    Donor = apps.get_model('User', 'Donor')
    allowed_groups = COMPATIBLE_DONORS.get(blood_group, [])
    
    approved_pool = Donor.objects.filter(
        status='APPROVED',
        blood_group__in=allowed_groups
    )
    
    return approved_pool.distinct().order_by('created_at')


def check_global_inventory_thresholds():
    Donor = apps.get_model('User', 'Donor')
    Notification = apps.get_model('User_Admin', 'Notification') 
    hundred_days_ago = date.today() - timedelta(days=100)
    
    inventory_counts = Donor.objects.filter(
        status='APPROVED',
        created_at__date__lte=hundred_days_ago
    ).values('blood_group').annotate(total_units=Count('id'))

    current_stock = {bg[0]: 0 for bg in Donor.BLOOD_GROUP_CHOICES}
    for item in inventory_counts:
        current_stock[item['blood_group']] = item['total_units']

    low_stock_groups = [bg for bg, count in current_stock.items() if count < 10]

    if low_stock_groups:
        groups_str = ", ".join(low_stock_groups)
        Notification.objects.create(
            notification_type='INVENTORY',
            title="Low Inventory Warning Alert",
            message=f"CRITICAL DEFICIT: The following blood groups have fallen below the 10-unit safety threshold: [{groups_str}]. Please prepare donors for them."
        )

        