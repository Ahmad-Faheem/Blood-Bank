from django.shortcuts import render
from User.models import PublicReview, Donor, BloodRequest
from User_Admin.models import SystemSetting
from django.db.models import Sum
from django.contrib.auth.decorators import user_passes_test

def home(request):
    featured_reviews = PublicReview.objects.filter(status='APPROVED').order_by('-created_at')[:2]
    
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

    return render(request, 'home.html' , {
        'page_title' : 'Regional Blood Bank',
        'inventory_data': inventory_data,
        'reviews' : featured_reviews,
    })

def All_Reviews(request):
    featured_reviews = PublicReview.objects.filter(status='APPROVED').order_by('-created_at')
    return render(request, 'all-reviews.html' , {
        'page_title' : 'Blood Bank | Reviews',
        'reviews' : featured_reviews,
    })

def is_user(user):
    return user.is_authenticated 

@user_passes_test(is_user, login_url='User:login')
def user_profile(request):
    context = {
        'page_title' : f"{request.user.full_name.upper() or request.user.email} | Profile",
        'countries' : {
            "+1" : "+1 (US)",
            "+44" : "+44 (UK)",
            "+92" : "+92 (PK)",
            "+91":"+91 (IN)"
        },
        'profile_status' : {
            'ACTIVATE' : "Activate",
            'DEACTIVATE' : "Deactivate"
        }
    }
    if request.user.is_authenticated:
        context['donor_history'] = Donor.objects.filter(user=request.user).order_by('-created_at')
        context['request_history'] = BloodRequest.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'profile.html' , context)
