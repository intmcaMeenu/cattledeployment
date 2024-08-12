from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from cattle_app.models import User, PasswordResetToken, Category
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
from django.contrib.auth import logout as auth_logout
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from .models import Category
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.db import IntegrityError
from .models import Category, Subcategory,Cattle
import traceback


User = get_user_model()

def index(request):
    categories = Category.objects.all()
    return render(request, 'user/index.html',{'categories': categories})

import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def login_page(request):
    user=request.user
    if user.is_authenticated:
            return render(request,'user/indexcattle.html')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            if user.is_superuser and user.is_staff:
                return redirect('admin_index')
            elif user.role==1:
                if user.contact==None and user.city==None and user.house_name==None and user.postal_code==None:
                        return redirect('profile_completion')
                else:
                    return render(request, 'user/indexcattle.html')
        else:
            messages.error(request, 'Invalid Credentials!Try Again')
            return redirect('login_page')
    return render(request, 'user/login_page.html')


def userlogout(request):
    logout(request)
    return redirect('login_page')

@login_required
def admin_index(request):
    return render(request, 'admin2/index.html')

@login_required
def indexcattle(request):
    return render(request,'user/indexcattle.html')



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

@login_required
def active_users(request):
    profiles = User.objects.filter(role=1)
    return render(request, 'admin2/admin_userview.html', {'profiles': profiles})

def toggleusers(request,uid):
    user=User.objects.get(id=uid)
    if user.is_active==True:
        user.is_active=False
    else:
        user.is_active=True
    user.save()
    return redirect('admin_userview')

@login_required
def admin_category(request):
    if request.method == 'POST':
        category_name = request.POST['category_name']
        if Category.objects.filter(category_name__iexact=category_name).exists():
            return render(request, 'admin2/admin_category.html', {
                'error': 'This category already exists.',
                'categories': Category.objects.all()
            })
        try:
            if 'category_image' in request.FILES:
                image = request.FILES['category_image']
                file_name = default_storage.save(f'category_images/{image.name}', image)
                category = Category(category_name=category_name, category_image=file_name)
            else:
                category = Category(category_name=category_name)
            category.save()
            messages.success(request, 'Category added successfully.')
        except IntegrityError:
            messages.error(request, 'This category already exists.')
        return redirect('admin_category')
    categories = Category.objects.all()
    return render(request, 'admin2/admin_category.html', {'categories': categories})

def category_edit(request):
    if request.method == 'POST':
        category_id = request.POST['category_id']
        category_name = request.POST['category_name']
        category = get_object_or_404(Category, pk=category_id)
        if Category.objects.filter(category_name__iexact=category_name).exclude(pk=category_id).exists():
            return render(request, 'admin2/admin_category.html', {
                'error': 'This category already exists.',
                'categories': Category.objects.all()
            })
        try:
            category.category_name = category_name
            if 'category_image' in request.FILES:
                image = request.FILES['category_image']
                file_name = default_storage.save(f'category_images/{image.name}', image)
                category.category_image = file_name
            category.save()
            messages.success(request, 'Category updated successfully.')
        except IntegrityError:
            messages.error(request, 'This category already exists.')
        return redirect('admin_category')

def category_delete(request):
    category_id = request.GET.get('id')
    category = get_object_or_404(Category, pk=category_id)
    if category.category_image:
        default_storage.delete(category.category_image.name)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('admin_category')

@login_required
def admin_subcategory(request):
    if request.method == 'POST':
        category_id = request.POST['category']
        subcategory_name = request.POST['subcategory_name']
        subcategory_description = request.POST['subcategory_description']
        
        category = get_object_or_404(Category, pk=category_id)
        
        if Subcategory.objects.filter(subcategory_name__iexact=subcategory_name, category=category).exists():
            messages.error(request, 'This subcategory already exists for the selected category.')
        else:
            try:
                subcategory = Subcategory(
                    category=category,
                    subcategory_name=subcategory_name,
                    subcategory_description=subcategory_description
                )
                subcategory.save()
                messages.success(request, 'Subcategory added successfully.')
            except IntegrityError:
                messages.error(request, 'An error occurred while adding the subcategory.')
        
        return redirect('admin_subcategory')
    
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    context = {
        'categories': categories,
        'subcategories': subcategories
    }
    return render(request, 'admin2/admin_subcategory.html', context)

def subcategory_edit(request):
    if request.method == 'POST':
        subcategory_id = request.POST['subcategory_id']
        category_id = request.POST['category']
        subcategory_name = request.POST['subcategory_name']
        subcategory_description = request.POST['subcategory_description']
        
        subcategory = get_object_or_404(Subcategory, pk=subcategory_id)
        category = get_object_or_404(Category, pk=category_id)
        
        if Subcategory.objects.filter(subcategory_name__iexact=subcategory_name, category=category).exclude(pk=subcategory_id).exists():
            messages.error(request, 'This subcategory already exists for the selected category.')
        else:
            try:
                subcategory.category = category
                subcategory.subcategory_name = subcategory_name
                subcategory.subcategory_description = subcategory_description
                subcategory.save()
                messages.success(request, 'Subcategory updated successfully.')
            except IntegrityError:
                messages.error(request, 'An error occurred while updating the subcategory.')
        
        return redirect('admin_subcategory')

def subcategory_delete(request):
    subcategory_id = request.GET.get('id')
    if subcategory_id:
        subcategory = get_object_or_404(Subcategory, pk=subcategory_id)
        subcategory.delete()
        messages.success(request, 'Subcategory deleted successfully.')
    else:
        messages.error(request, 'Invalid subcategory ID.')
    return redirect('admin_subcategory')


@login_required
def user_dashboard(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'user/user_dashboard.html', context)



@login_required
def user_cattle(request):
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()

    if request.method == 'POST':
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        new_subcategory = request.POST.get('new_subcategory')
        dob = request.POST.get('dob')
        weight = request.POST.get('weight')
        color = request.POST.get('color')
        image = request.FILES.get('image')
        number_of_cattle = request.POST.get('number_of_cattle')
        milk_production = request.POST.get('milk_production')

        try:
            category = Category.objects.get(id=category_id)
            
            if subcategory_id:
                subcategory = Subcategory.objects.get(id=subcategory_id)
                cattle = Cattle(
                user=request.user,
                category=category,
                subcategory=subcategory,
                dob=dob,
                weight=weight,
                color=color,
                image=image,
                number_of_cattle=number_of_cattle,
                milk_production=milk_production
            )
                cattle.save()
                messages.success(request, 'Cattle added successfully.')
                return redirect('user_dashboard')
            elif new_subcategory:
                subcategory, created = Subcategory.objects.get_or_create(
                    category=category,
                    subcategory_name=new_subcategory
                )
            else:
                messages.error(request, 'Please select a breed or enter a new one.')
                return redirect('user_cattle')

           
        except Category.DoesNotExist:
            messages.error(request, 'Selected category does not exist.')
        except Subcategory.DoesNotExist:
            messages.error(request, 'Selected subcategory does not exist.')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    context = {
        'categories': categories,
        'subcategories': subcategories,
    }
    return render(request, 'user/user_cattle.html', context)


def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category_id=category_id)
    return render(request, 'user/subcategory_options.html', {'subcategories': subcategories})







