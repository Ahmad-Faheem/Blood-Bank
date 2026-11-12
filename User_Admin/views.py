from django.shortcuts import render, redirect
from User.models import Donor, BloodRequest, PublicReview
from User_Admin.models import SystemSetting, Notification
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Sum
from itertools import groupby

User = get_user_model()

def is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def admin_login(request):
    if is_admin_user(request.user):
        return redirect('User_Admin:dashboard')
    return render(request, 'admin-login.html', {
        "page_title" : "Administrator | Login",
    })

@user_passes_test(is_admin_user, login_url='User_Admin:admin_login')
def dashboard(request):
    availlable_donors = Donor.objects.filter(status='APPROVED').count()
    pending_screenings = Donor.objects.filter(status='PENDING').count() 
    active_requests = BloodRequest.objects.filter(status='PENDING').count()

    blood_groups = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
    inventory_data = []

    for bg in blood_groups:
        available_units = Donor.objects.filter(blood_group=bg, status='APPROVED').count()
        
        if 0 <= available_units <= 10:
            stock_label = "LOW STOCK"
            status_class = "low"
            graph_img = "images/blood-icon.png"
        elif 11 <= available_units <= 30:
            stock_label = "MEDIUM STOCK"
            status_class = "med"
            graph_img = "images/graph-2.png"
        else: 
            stock_label = "GOOD STOCK"
            status_class = "high"
            graph_img = "images/graph-1.png"

        inventory_data.append({
            'type': bg,
            'units': available_units,
            'label': stock_label,
            'status_class': status_class,
            'graph_img': graph_img
        })
    
    context = {
        'availlable_donors': availlable_donors,
        'pending_screenings': pending_screenings,
        'active_requests': active_requests,
        'inventory_data': inventory_data,
        'page_title' : "Admin | Dashboard",
    }
    return render(request, 'dashboard.html', context)


class NotificationsView(UserPassesTestMixin, TemplateView):
    template_name = "notifications.html"
    login_url = 'User_Admin:admin_login' 
    raise_exception = False 

    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        all_notifications = Notification.objects.all().order_by('-created_at')
        grouped_notifications = []
        for date, group in groupby(all_notifications, lambda x: x.created_at.date()):
            grouped_notifications.append({
                'date': date,
                'items': list(group)
            })

        context['grouped_notifications'] = grouped_notifications
        context['page_title'] = "Admin | Notifications"
        return context


@user_passes_test(is_admin_user, login_url='User_Admin:admin_login')
def donors(request):
    pending_donors = Donor.objects.filter(status='PENDING')
    approved_count = Donor.objects.filter(status='APPROVED').count()
    pending_count = pending_donors.count()
    context = {
        'page_title' : "Admin | Donors",
        'pending_donors': pending_donors,
        'approved_count': approved_count,
        'pending_count': pending_count
    }
    return render(request, 'donors.html' , context)

@user_passes_test(is_admin_user, login_url='User_Admin:admin_login')
def requests(request):
    pending_requests = BloodRequest.objects.filter(status='PENDING')
    approved_count = BloodRequest.objects.filter(status='APPROVED').count()
    pending_count = pending_requests.count()
    context = {
        'page_title' : "Admin | Blood Requests",
        'pending_requests': pending_requests,
        'approved_count': approved_count,
        'pending_count': pending_count
    }
    return render(request, 'requests.html' , context)

@user_passes_test(is_admin_user, login_url='User_Admin:admin_login')
def reports(request):
    return render(request, 'reports.html' , {
        'page_title' : "Admin | Reports",
    })

@user_passes_test(is_admin_user, login_url='User_Admin:admin_login')
def reviews(request):
    pending_reviews = PublicReview.objects.filter(status='PENDING')
    approved_count = PublicReview.objects.filter(status='APPROVED').count()
    pending_count = pending_reviews.count()
    context = {
        'page_title' : "Admin | Reviews",
        'pending_reviews': pending_reviews,
        'approved_count': approved_count,
        'pending_count': pending_count
    }
    return render(request, 'reviews.html', context)

class SettingsTemplateView(UserPassesTestMixin, TemplateView):
    template_name = "settings.html" 
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.is_superuser)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['settings'] = SystemSetting.load()
        context['page_title'] = " Admin | Global Settings ",
        return context
    
def admin_logout(request):
    logout(request)
    return redirect('User_Admin:admin_login')