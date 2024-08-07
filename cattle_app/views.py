from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from cattle_app.models import User, PasswordResetToken
from datetime import datetime, timedelta
from django.utils import timezone
from django.http import HttpResponse
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

def index(request):
    return render(request, 'user/index.html')

def login_page(request):
    user = request.user
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        
        if user is not None:
            login(request, user)
            if not user.profile_completed and user.role==1:
                return redirect('profile_completion')
            if user.is_superuser:
                return redirect('admin_index')
            else:
                return redirect('indexcattle')
        else:
            return render(request, 'user/login_page.html', {'error': 'Invalid login credentials'})
    elif user.is_authenticated:
        if not user.profile_completed and user.role==1:
                return redirect('profile_completion')
        if user.is_superuser:
            return redirect('admin_index')
        else:
            return redirect('indexcattle')
    
    
    return render(request, 'user/login_page.html')



def userlogout(request):
    logout(request)
    return redirect('index')

@login_required
def admin_index(request):
    return render(request, 'admin2/admin_index.html')

@login_required
def indexcattle(request):
    if not request.user.profile_completed:
        return redirect('profile_completion')
    return render(request, 'user/indexcattle.html')



def register_page(request):
    if request.method == 'POST':
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            return render(request, 'user/register_page.html', {'error': 'Passwords do not match'})
        
        try:
            user = User.objects.create_user(
                first_name=fname,
                last_name=lname,
                email=email,
                password=password1,
                username=fname
            )
            user.save()
            return redirect('login_page')
        except Exception as e:
            return render(request, 'user/register_page.html', {'error': str(e)})
    else:
        return render(request, 'user/register_page.html')



def send_password_reset_email(request, user, token):
    reset_url = f'http://127.0.0.1:8000/user/reset_password/{token}'
    subject = 'Password Reset Request'
    context = {
        'user': user,
        'reset_url': reset_url,
    }
    html_content = render_to_string('user/mail_read.html', context)
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [user.email])
    email.attach_alternative(html_content, 'text/html')
    email.send()

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        associated_users = User.objects.filter(email=email)
        if associated_users.exists():
            for user in associated_users:
                token = PasswordResetToken.objects.create(user=user)
                send_password_reset_email(request, user, token.token)
            return render(request, 'user/password_reset.html',{'message':'A password reset link has been sent to your email.'})
        else:
            return  render(request, 'user/password_reset.html',{'error':'No user is associated with this email address.'})
    return render(request, 'user/password_reset.html')

def reset_password(request, token):
    reset_token = PasswordResetToken.objects.filter(token=token, expiry__gt=timezone.now()).first()
    if not reset_token:
        return HttpResponse("Invalid or expired token.")
    
    if request.method == "POST":
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 == password2:
            reset_token.user.set_password(password1)
            reset_token.user.save()
            reset_token.delete()
            return redirect('login_page')
        else:
            return HttpResponse("Passwords do not match.")
    
    return render(request, 'user/new_password.html', {'token': token})

def profile_completion(request):
    if request.method == 'POST':
        house_name = request.POST.get('house_name')
        city = request.POST.get('city')
        phone_number = request.POST.get('phone_number')
        postal_code = request.POST.get('postal_code')

        user = request.user
        user.house_name = house_name
        user.city = city
        user.contact = phone_number
        user.postal_code = postal_code
        user.save()

        return redirect('indexcattle')

    return render(request, 'user/profile_completion.html')

@login_required
def profile_view(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'user/profile_view.html', context)

User = get_user_model()

@login_required
def profile_update(request):
    if request.method == 'POST':
        contact = request.POST.get('contact')
        house_name = request.POST.get('house_name')
        city = request.POST.get('city')
        postal_code = request.POST.get('postal_code')

        user = request.user
        user.contact = contact
        user.house_name = house_name
        user.city = city
        user.postal_code = postal_code
        user.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile_view')
    
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'user/profile_update.html', context)
