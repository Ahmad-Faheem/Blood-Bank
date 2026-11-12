from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout

def is_user(user):
    return user.is_authenticated and not(user.is_staff or user.is_superuser)

@user_passes_test(is_user, login_url='User:login')
def register_donor(request):
    return render(request, 'register-donor.html' , {
        'page_title' : 'User | Register Donor',
        'user_email' : request.user.email
    })

@user_passes_test(is_user, login_url='User:login')
def request_blood(request):
    return render(request, 'request-blood.html' , {
        'page_title' : 'User | Request Blood',
        'user_email' : request.user.email
    })

def register(request):
    return render(request, 'register.html' , {
        'page_title' : 'User | Register',
    })

def login(request):
    return render(request, 'login.html' , {
        'page_title' : 'User | Login',
    })

def forget_password(request):
    return render(request, 'forget-password.html' , {
        'page_title' : 'User | forget-password',
    })

def verify_otp(request):
    return render(request, 'verify-otp.html' , {
        'page_title' : 'User | verify-otp',
    })

def change_password(request):
    return render(request, 'change-password.html' , {
        'page_title' : 'User | change-password',
    })

def user_logout(request):
    logout(request)
    return redirect('home')