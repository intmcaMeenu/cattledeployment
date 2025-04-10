from io import BytesIO
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from cattle_app.models import User, PasswordResetToken, Category, Wishlist
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
from .models import Cart, CartItem, Category, VaccinationCenter, Vaccine
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.db import IntegrityError
from .models import Category, Subcategory,Cattle
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from .models import Subcategory
from django.http import JsonResponse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.decorators.cache import never_cache

from django.http import HttpResponse
from django.template import loader
from django.core.paginator import Paginator
from django.conf import settings


import traceback


User = get_user_model()

def index(request):
    categories = Category.objects.all()
    return render(request, 'user/index.html', {'categories': categories})

import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def login_page(request):
    user=request.user
    if user.is_authenticated and user.role==1:
        if user.contact==None and user.city==None and user.house_name==None and user.postal_code==None:
            return redirect('profile_completion')
        else:
            return redirect('indexcattle')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        # Check for vaccination center login
        if not user:
            try:
                vaccination_center = VaccinationCenter.objects.get(center_email=email, password=password)
                # Handle successful login for vaccination center
                return render(request, 'vaccine_center/vaccination_center_dashboard.html', {'user': vaccination_center})  # Render the vaccination center dashboard
            except VaccinationCenter.DoesNotExist:
                messages.error(request, 'Invalid Credentials! Try Again')
                return redirect('login_page')

        if user is not None:
            login(request, user)
            if user.is_superuser and user.is_staff:
                return redirect('admin_index')
            elif user.role==1:
                if user.contact==None and user.city==None and user.house_name==None and user.postal_code==None:
                        return redirect('profile_completion')
                else:
                    return redirect('indexcattle')
        else:
            messages.error(request, 'Invalid Credentials!Try Again')
            return redirect('login_page')
    return render(request, 'user/login_page.html')

@login_required
@never_cache
def userlogout(request):
    logout(request)
    return redirect('login_page')

@login_required
@never_cache
def admin_index(request):
    User = get_user_model()
    
    visitor_count = User.objects.filter(role=1).count()
    print(f"Debug: Visitor count is {visitor_count}")  # Add this line for debugging
    
    context = {
        'visitor_count': visitor_count,
        'category_count': Category.objects.count(),
        'subcategory_count': Subcategory.objects.count(),
        'cattle_count': Cattle.objects.count(),
    }
    
    return render(request, 'admin2/index.html', context)

@login_required
@never_cache
def indexcattle(request):
    categories = Category.objects.all()
    return render(request, 'user/indexcattle.html',  {'categories': categories})



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

@login_required
@never_cache
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

        return redirect('indexcattle')  # Redirect to indexcattle view

    return render(request, 'user/profile_completion.html')

@login_required
@never_cache
def profile_view(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'user/profile_view.html', context)

User = get_user_model()

@login_required
@never_cache
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
        return redirect('user_dashboard')
    
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'user/profile_update.html', context)



    return render(request, 'dashboard.html', context)

@login_required
@never_cache
def active_users(request):
    profiles = User.objects.filter(role=1)
    return render(request, 'admin2/admin_userview.html', {'profiles': profiles})

@login_required
@never_cache
def toggleusers(request,uid):
    user=User.objects.get(id=uid)
    if user.is_active==True:
        user.is_active=False
    else:
        user.is_active=True
    user.save()
    return redirect('admin_userview')

@login_required
@never_cache
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

@login_required
@never_cache    
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

@login_required
@never_cache
def category_delete(request):
    category_id = request.GET.get('id')
    category = get_object_or_404(Category, pk=category_id)
    if category.category_image:
        default_storage.delete(category.category_image.name)
    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('admin_category')

@login_required
@never_cache
def admin_subcategory(request):
    if request.method == 'POST':
        category_id = request.POST['category']
        subcategory_name = request.POST['subcategory_name']
        
        
        category = get_object_or_404(Category, pk=category_id)
        
        if Subcategory.objects.filter(subcategory_name__iexact=subcategory_name, category=category).exists():
            messages.error(request, 'This subcategory already exists for the selected category.')
        else:
            try:
                subcategory = Subcategory(
                    category=category,
                    subcategory_name=subcategory_name,
                    
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


@login_required
@never_cache

def subcategory_edit(request):
    if request.method == 'POST':
        subcategory_id = request.POST['subcategory_id']
        category_id = request.POST['category']
        subcategory_name = request.POST['subcategory_name']
              
        subcategory = get_object_or_404(Subcategory, pk=subcategory_id)
        category = get_object_or_404(Category, pk=category_id)
        
        if Subcategory.objects.filter(subcategory_name__iexact=subcategory_name, category=category).exclude(pk=subcategory_id).exists():
            messages.error(request, 'This subcategory already exists for the selected category.')
        else:
            try:
                subcategory.category = category
                subcategory.subcategory_name = subcategory_name
                
                subcategory.save()
                messages.success(request, 'Subcategory updated successfully.')
            except IntegrityError:
                messages.error(request, 'An error occurred while updating the subcategory.')
        
        return redirect('admin_subcategory')


@login_required
@never_cache
def subcategory_delete(request):
    subcategory_id = request.GET.get('id')
    if subcategory_id:
        subcategory = get_object_or_404(Subcategory, pk=subcategory_id)
        subcategory.delete()
        messages.success(request, 'Subcategory deleted successfully.')
    else:
        messages.error(request, 'Invalid subcategory ID.')
    return redirect('admin_subcategory')


from django.shortcuts import render
from .models import Cart, Wishlist, Payment

@login_required
@never_cache
def user_dashboard(request):
    user = request.user

    # Calculate the total number of cattle in the cart
    cart_items = CartItem.objects.filter(cart__user=user)
    cart_count = sum(item.quantity for item in cart_items)  # Sum the quantities of all items
    wishlist_count = Wishlist.objects.filter(user=user).count()
    cattle_bought_count = Payment.objects.filter(user=user).count()

    context = {
        'cart_count': cart_count,
        'wishlist_count': wishlist_count,
        'cattle_bought_count': cattle_bought_count,
    }

    return render(request, 'user/user_dashboard.html', context)

from django.http import JsonResponse

@login_required
def get_cart_wishlist_counts(request):
    if request.user.is_authenticated:
        cart_count = request.user.cart.items.count()  # Adjust this based on your cart model
        wishlist_count = request.user.wishlist.items.count()  # Adjust this based on your wishlist model
        return JsonResponse({
            'cart_count': cart_count,
            'wishlist_count': wishlist_count
        })
    return JsonResponse({'cart_count': 0, 'wishlist_count': 0})

import logging

logger = logging.getLogger(__name__)

from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .models import Category, Subcategory, Cattle

@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def user_cattle(request):
    if request.method == 'POST':
        try:
            # Extract form data
            category_id = request.POST.get('category')
            subcategory_id = request.POST.get('subcategory')
            new_subcategory = request.POST.get('new_subcategory')
            dob = request.POST.get('dob')
            weight = request.POST.get('weight')
            color = request.POST.get('color')
            image = request.FILES.get('image')
            milk_production = request.POST.get('milk_production')
            price = request.POST.get('price')
            description = request.POST.get('description')

            # Perform validations
            if not all([category_id, dob, weight, color, image, price, description]):
                return JsonResponse({'success': False, 'error': 'All fields except milk production are required.'})

            if not (subcategory_id or new_subcategory):
                return JsonResponse({'success': False, 'error': 'Please select a breed or enter a new one.'})

            # Validate price
            try:
                price_float = float(price)
                if price_float < 1000 or price_float > 100000:
                    return JsonResponse({'success': False, 'error': 'Price must be between 1,000 and 100,000.'})
            except ValueError:
                return JsonResponse({'success': False, 'error': 'Invalid price value.'})

            # Process the data
            category = Category.objects.get(id=category_id)
            
            if subcategory_id:
                subcategory = Subcategory.objects.get(subcategory_id=subcategory_id)
            elif new_subcategory:
                subcategory, created = Subcategory.objects.get_or_create(
                    category=category,
                    subcategory_name=new_subcategory
                )

            cattle = Cattle.objects.create(
                user=request.user,
                category=category,
                subcategory=subcategory,
                dob=dob,
                weight=float(weight),
                color=color,
                image=image,
                milk_production=float(milk_production) if milk_production else None,
                price=price_float,
                description=description
            )

            return JsonResponse({'success': True, 'message': 'Cattle added successfully.'})

        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e)})
        except Exception as e:
            print(f"Error in user_cattle view: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})

    # GET request
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    context = {
        'categories': categories,
        'subcategories': subcategories,
    }
    return render(request, 'user/user_cattle.html', context)

@login_required
@never_cache
def get_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category_id=category_id, status=1).values('subcategory_id', 'subcategory_name')
    return JsonResponse({'subcategories': list(subcategories)})


def user_productview(request, product_id):
    cattle = get_object_or_404(Cattle, id=product_id)
    is_sold_out = cattle.status == 3  # Check if cattle status is 3 (sold)

    context = {
        'cattle': cattle,
        'user': cattle.user,  # Add the owner user details to the context
        'is_sold_out': is_sold_out  # Add this flag to the context
    }
    return render(request, 'user/user_productview.html', context)
@login_required
@never_cache
def user_productlogview(request, product_id):
    cattle = get_object_or_404(Cattle, id=product_id)
    user_wishlist = Wishlist.objects.filter(user=request.user).values_list('cattle_id', flat=True)
    is_out_of_stock = cattle.status == 3  # Check if cattle status is 3 (sold)
    selected_count = request.GET.get('count', 1)  # Defaults to 1

    # Check if the current user is the owner of the cattle
    is_owner = cattle.user == request.user

    # Store cattle price in session as a float
    request.session['cattle_price'] = float(cattle.price)  
    request.session['cattle_id'] = cattle.id

    # Fetch payment details if the cattle is sold
    payment_details = None
    if is_out_of_stock:
        payment_details = Payment.objects.filter(cattle=cattle).first()

    context = {
        'cattle': cattle,
        'is_out_of_stock': is_out_of_stock,
        'selected_count': int(selected_count),  # Ensure it's an integer
        'user_wishlist': list(user_wishlist), 
        'owner': cattle.user,  # Add the cattle owner to the context
        'payment_details': payment_details,  # Add payment details to the context
        'is_owner': is_owner,  # Add this to the context
    }
    return render(request, 'user/user_productlogview.html', context)

# ... (previous imports)
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@never_cache
def adminview_cattle(request):
    cattle = Cattle.objects.all()
    context = {
        'cattle': cattle
    }
    return render(request, 'admin2/adminview_cattle.html', context)

@require_POST
@login_required
def update_cattle_status(request, cattle_id):
    cattle = get_object_or_404(Cattle, id=cattle_id)
    new_status = int(request.POST.get('status'))
    reject_message = request.POST.get('reject_message', '')

    if new_status == 2 and not reject_message:
        return JsonResponse({'status': 'error', 'message': 'Rejection reason is required.'})

    cattle.status = new_status
    if new_status == 2:
        cattle.reject_message = reject_message
    cattle.save()

    return JsonResponse({'status': 'success', 'new_status': new_status})


def category_detail(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    subcategories = Subcategory.objects.filter(category=category, status=1)
    
    # Fetch cattle details for the given category
    cattle = Cattle.objects.filter(category=category)
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'cattle': cattle,
    }
    return render(request, 'user/category_detail.html', context)

@login_required
@never_cache
def category_detaillog(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    subcategories = Subcategory.objects.filter(category=category, status=1)
    
    # Fetch cattle details for the given category with status 1 or 3
    cattle = Cattle.objects.filter(category=category, status__in=[1, 3])
    
    context = {
        'category': category,
        'subcategories': subcategories,
        'cattle': cattle,
    }
    return render(request, 'user/category_detaillog.html', context)

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Cattle

def is_admin(user):
    return user.is_superuser

@login_required
def update_cattle_status(request, cattle_id):
    if request.method == 'POST':
        cattle = get_object_or_404(Cattle, id=cattle_id)
        
        if request.user.is_superuser:  
            new_status = int(request.POST.get('status'))
            
            # Check if the cattle is already rejected
            if cattle.status == 2:
                return JsonResponse({'status': 'error', 'message': 'Cannot change status of already rejected cattle.'})
            
            cattle.status = new_status
            
            if new_status == 2:  # If rejecting
                reject_message = request.POST.get('reject_message')
                if not reject_message:
                    return JsonResponse({'status': 'error', 'message': 'Rejection reason is required.'})
                cattle.reject_message = reject_message
            
            cattle.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': "You are not allowed to update this cattle's status."})
    else:
        return JsonResponse({'status': 'error', 'message': "Invalid request method."})
    
    
from django.http import JsonResponse

def toggle_subcategory_status(request):
    if request.method == 'GET':
        subcategory_id = request.GET.get('subcategory_id')  # Changed from 'id' to 'subcategory_id'
        new_status = request.GET.get('status')
        subcategory = get_object_or_404(Subcategory, subcategory_id=subcategory_id)  # Use subcategory_id here
        
        # Ensure that only the owner or an authorized user can update the status
        if request.user.is_superuser:  # Removed the check for subcategory.user as it might not exist
            subcategory.status = new_status
            subcategory.save()
            return JsonResponse({'message': 'Status updated successfully'}, status=200)
        else:
            return JsonResponse({'error': 'You are not allowed to update this subcategory\'s status.'}, status=403)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
    
    
from django.db.models import Prefetch
from .models import Cattle, Payment

from django.db.models import Prefetch
from .models import Cattle, Payment, User

@login_required
@never_cache
def fetch_cattle_details(request):
    user = request.user
    submitted_cattle = Cattle.objects.filter(user=user).prefetch_related(
        Prefetch('payment_set', 
                 queryset=Payment.objects.select_related('user'))
    )
    categories = Category.objects.all()

    print(f"Debug: Total cattle found: {submitted_cattle.count()}")

    for cattle in submitted_cattle:
        print(f"Cattle ID: {cattle.id}")
        print(f"Category: {cattle.category.category_name}")
        print(f"Subcategory: {cattle.subcategory.subcategory_name}")
        print(f"Price: {cattle.price}")
        print(f"Status: {cattle.get_status_display()}")
        
        payments = cattle.payment_set.all()
        print(f"Debug: Payments for cattle {cattle.id}: {payments.count()}")
        
        if payments:
            for payment in payments:
                buyer = payment.user
                print(f"  Payment ID: {payment.payment_id}")
                print(f"  Cattle ID (from payment): {payment.cattle_id}")
                print(f"  Bought by: {buyer.first_name} {buyer.last_name}")
                print(f"  Buyer Email: {buyer.email}")
                print(f"  Buyer City: {buyer.city}")
                print(f"  Buyer Phone: {buyer.contact}")
                print(f"  Amount Paid: {payment.amount}")
                print(f"  Payment Date: {payment.payment_date}")
        else:
            print("  Not yet purchased")
        
        print("--------------------")

    context = {
        'user': user,
        'submitted_cattle': submitted_cattle,
        'categories': categories
    }
    return render(request, 'user/fetch_cattle_details.html', context)



    
@login_required
@never_cache
def vaccination_center(request):
    
    vaccination_centers=VaccinationCenter.objects.all()
    if request.method == 'POST':
        center_name = request.POST.get('center_name')
        center_email = request.POST.get('center_email')
        password = request.POST.get('password')

        # Validate the input data
        if not center_name or not center_email or not password:
            messages.error(request, 'All fields are required.')
            return redirect('vaccination_center')

        # Check if the center already exists
        try:
            existing_center = VaccinationCenter.objects.get(center_name=center_name)
            messages.error(request, 'A vaccination center with this name already exists.')
            return redirect('vaccination_center')
        except ObjectDoesNotExist:
            # Create a new vaccination center
            new_center = VaccinationCenter(center_name=center_name, center_email=center_email,  password=password)
            new_center.save()

            # Send a notification email to the admin
            #send_notification_email(center_name)

            messages.success(request, 'Vaccination center added successfully.')
            return redirect('vaccination_center')
    return render(request,'admin2/vaccination_center.html',{'vaccination_centers':vaccination_centers})

@login_required
@never_cache
def toggle_vaccination_center(request,center_id):
        if request.method == 'POST':
            center = get_object_or_404(VaccinationCenter, pk=center_id)
            center.status = not center.status
            center.save()
            return redirect('vaccination_center')
        
        
@login_required
@never_cache       

def edit_cattle(request, cattle_id):
    cattle = get_object_or_404(Cattle, id=cattle_id)

    # Restrict editing for accepted cattle (status 1)
    if cattle.status == 1:
        return HttpResponse("Editing not allowed for accepted cattle.", status=403)

    if request.method == 'POST':
        form = CattleForm(request.POST, instance=cattle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cattle edited successfully.')
            return redirect('some_view')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CattleForm(instance=cattle)

    return render(request, 'edit_cattle.html', {'form': form, 'cattle': cattle})

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import Cattle, Cart, CartItem
import logging

logger = logging.getLogger(__name__)

@login_required
def add_to_cart(request, cattle_id):
    logger.info(f"Attempting to add cattle ID {cattle_id} to cart for user {request.user.id}")
    try:
        cattle = get_object_or_404(Cattle, id=cattle_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if the item is already in the cart
        if CartItem.objects.filter(cart=cart, cattle=cattle).exists():
            return JsonResponse({'status': 'error', 'message': 'Item is already in your cart.'})

        # If not, add the item to the cart
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, cattle=cattle, defaults={'quantity': 1})
        if not item_created:
            cart_item.quantity += 1
            cart_item.save()

        logger.info(f"Successfully added cattle ID {cattle_id} to cart")
        return JsonResponse({'status': 'success', 'message': 'Item added to cart'})
    except Exception as e:
        logger.error(f"Error adding item to cart: {str(e)}", exc_info=True)
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@never_cache
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()  # Fetch all items in the user's cart
    total_price = sum(item.cattle.price * item.quantity for item in items)  # Calculate total price
    context = {
        'cart': cart,
        'items': items,
        'total_price': total_price  # Pass total price to the template
    }
    return render(request, 'user/addtocart.html', context)

@login_required
@never_cache
def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id)

        # Ensure the quantity does not exceed stock quantity
        if quantity > 0 and quantity <= cart_item.cattle.stock_quantity:
            cart_item.quantity = quantity
            cart_item.save()
            
            # Calculate the new total price
            total_price = sum(item.cattle.price * item.quantity for item in cart_item.cart.items.all())
            
            return JsonResponse({'total_price': total_price})
        else:
            return JsonResponse({'error': 'Invalid quantity'}, status=400)
    

@login_required
@never_cache
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    
    # Calculate the new total price
    cart = cart_item.cart
    total_price = sum(item.cattle.price * item.quantity for item in cart.items.all())

    return JsonResponse({'total_price': total_price})  # Return the updated total price


    def add_to_cart(request, cattle_id):
      if request.method == 'POST':
        cattle_count = request.POST.get('cattle_count', 1)  # Default to 1 if nothing is selected
        # Handle adding cattle to cart with the selected count

    def cattle_count(request):
        
       count = Cattle.objects.filter(user=request.user).count()  # Adjust the filter as needed
       return JsonResponse({'count': count})
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Wishlist  # Ensure this points to your Wishlist model
from django.contrib.auth.decorators import login_required

# Ensure the user is logged in
@csrf_exempt  # Use this if CSRF token is not being sent
@login_required  # Ensure the user is logged in
def toggle_wishlist(request):
    if request.method == 'POST':
        cattle_id = request.POST.get('cattle_id')
        # Add logic to add or remove from wishlist
        wishlist_item = Wishlist.objects.filter(cattle_id=cattle_id, user=request.user).first()
        
        if wishlist_item:
            wishlist_item.delete()
            status = 'removed'
        else:
            Wishlist.objects.create(cattle_id=cattle_id, user=request.user)
            status = 'added'
        
        # Return the status in the response
        return JsonResponse({'status': status})



@login_required
@never_cache
def wishlisted_item(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    context = {
        'wishlist_items': wishlist  # Make sure this matches your template
    }
    return render(request, 'user/wishlisted_item.html', context)

@login_required
@never_cache
def remove_from_wishlist(request):
    if request.method == 'POST':
        cattle_id = request.POST.get('cattle_id')
        try:
            # Ensure you are using the correct model name
            item = Wishlist.objects.get(cattle_id=cattle_id, user=request.user)
            item.delete()
            return JsonResponse({'status': 'removed'})
        except Wishlist.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found.'})
        
@login_required
@never_cache
def payment(request):
    cattle_price = request.session.get('cattle_price', None)
    amount = request.GET.get('amount')  # Get the amount from the query parameters
    if amount:
        amount = float(amount) * 100  # Convert to paise
    else:
        amount = cattle_price * 100  # Fallback to session value if not provided
    return render(request, 'user/payment.html', {'amount': amount})



from django.shortcuts import render
from django.http import JsonResponse
from .models import Payment  # Import your Payment model

@login_required
@never_cache
def save_payment(request):
    if request.method == 'POST':
        payment_id = request.POST.get('payment_id')
        amount = request.POST.get('amount')
        cattle_id = request.session.get('cattle_id', None)
        
        # Convert amount from paise to rupees
        amount_in_rupees = float(amount) / 100
        
        # Save payment details to the database
        payment = Payment(payment_id=payment_id, user=request.user, amount=amount_in_rupees, payment_status='success', cattle_id=cattle_id)
        payment.save()
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'}, status=400)

@login_required
@never_cache
def payment_details(request):
    payment_details = Payment.objects.filter(user=request.user)
    context = {
        'payment_details': payment_details
    }
    return render(request, 'user/payment_details.html', context)
    
from django.http import HttpResponseRedirect

def image_processing(request):
    if request.method == 'POST':
        # Assuming there's a form to upload an image
        image = request.FILES.get('image')
        if image:
            # Process the image here
            # For example, let's assume we have a function to process the image
            processed_image = processed_image(image)
            # Save the processed image
            processed_image.save()
            return HttpResponseRedirect('/user/image_processing_success')
        else:
            return JsonResponse({'status': 'error', 'message': 'No image uploaded.'})
    return render(request, 'user/image_processing.html')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import numpy as np
from django.core.files.uploadedfile import InMemoryUploadedFile
import os
from django.conf import settings
from django.core.files.storage import default_storage



def upload_image(request):
    if request.method == 'POST' and request.FILES['file1']:
        file = request.FILES['file1']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        return JsonResponse({'success': True, 'filename': filename})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
@never_cache
def vaccination_center_dashboard(request):
    user = request.user
    if user.is_authenticated and user.role == 1:
        return render(request, 'vaccine_center/vaccination_center_dashboard.html', {'user': user})
    else:
        return redirect('login_page')

@login_required
@never_cache
def vaccination_center_logout(request):
    logout(request)
    return redirect('login_page')

@login_required
@never_cache
def add_vaccine(request):
    if request.method == 'POST':
        vaccine_name = request.POST.get('vaccine_name')
        manufacturer = request.POST.get('manufacturer')
        batch_number = request.POST.get('batch_number')
        expiry_date = request.POST.get('expiry_date')

        # Create a new Vaccine instance and save it to the database
        try:
            vaccine = Vaccine(
                vaccine_name=vaccine_name,
                manufacturer=manufacturer,
                batch_number=batch_number,
                expiry_date=expiry_date
            )
            vaccine.save()  # Save the vaccine details to the database
            messages.success(request, 'Vaccine added successfully.')
            return redirect('success_url')  # Redirect to a success page
        except Exception as e:
            messages.error(request, f'Error adding vaccine: {str(e)}')

    return render(request, 'vaccine_center/add_vaccine.html')

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib import styles

from .models import Payment  # Import your Payment model

def download_invoice(request, payment_id):
    # Fetch the payment details from the database
    payment = Payment.objects.get(payment_id=payment_id)

    # Create a buffer to store the PDF data
    buffer = io.BytesIO()

    # Create the PDF object using reportlab's canvas
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Define some custom colors
    blue_color = colors.HexColor('#3498db')
    green_color = colors.HexColor('#28a745')

    # Title Styling
    p.setFont("Helvetica-Bold", 20)
    p.setFillColor(blue_color)
    p.drawString(200, height - 100, "Payment Details")

    # Add some margin space and line styling
    p.setLineWidth(1)
    p.setStrokeColor(blue_color)
    p.line(50, height - 110, width - 50, height - 110)

    # Payment details title
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.black)
    

    # Payment details styling
    p.setFont("Helvetica", 12)
    y_position = height - 180  # Start position for text

    p.drawString(50, y_position, f"Cattle Owner: {payment.cattle.user.first_name} {payment.cattle.user.last_name}")
    y_position -= 20  # Move to the next line

    p.drawString(50, y_position, f"Contact: {payment.cattle.user.contact}")
    y_position -= 20

    p.drawString(50, y_position, f"Email: {payment.cattle.user.email}")
    y_position -= 20

    p.drawString(50, y_position, f"City: {payment.cattle.user.city}")
    y_position -= 40  # Additional space before the next section

    p.drawString(50, y_position, f"Cattle: {payment.cattle.subcategory.subcategory_name}")
    y_position -= 20

    p.drawString(50, y_position, f"Amount: {payment.amount}")
    y_position -= 20

    p.drawString(50, y_position, f"Date: {payment.payment_date.strftime('%B %d, %Y')}")
    y_position -= 40  # Additional space before footer

    # Footer
    p.setFont("Helvetica", 10)
    p.setFillColor(green_color)
    p.setFont("Helvetica-Bold", 10)
    p.drawCentredString(width / 2, y_position, "Thank you for your purchase!")
    p.setStrokeColor(green_color)
    p.line(50, y_position - 10, width - 50, y_position - 10)

    # Save the PDF and close the canvas
    p.showPage()
    p.save()

    # Set the buffer to the beginning
    buffer.seek(0)

    # Create a response with the PDF file
    return FileResponse(buffer, as_attachment=True, filename=f"invoice_{payment.payment_id}.pdf")


from django.db.models import Sum

from django.db.models import Sum

def number_to_words(number):
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def convert_below_thousand(n):
        if n < 10:
            return units[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        else:
            return units[n // 100] + " Hundred" + (" and " + convert_below_thousand(n % 100) if n % 100 != 0 else "")
    
    if number == 0:
        return "Zero"
    
    result = ""
    if number >= 10000000:
        result += convert_below_thousand(number // 10000000) + " Crore "
        number %= 10000000
    if number >= 100000:
        result += convert_below_thousand(number // 100000) + " Lakh "
        number %= 100000
    if number >= 1000:
        result += convert_below_thousand(number // 1000) + " Thousand "
        number %= 1000
    if number > 0:
        result += convert_below_thousand(number)
    
    return result.strip()

@login_required
@never_cache
def invoice(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    
    # Convert the amount to words
    amount_in_words = number_to_words(int(payment.amount))
    
    context = {
        'payment': payment,
        'user': request.user,
        'amount_in_words': amount_in_words
    }
    return render(request, 'user/invoice.html', context)

@login_required
@never_cache
def sales_details_list(request):
    payments = Payment.objects.select_related('cattle__user', 'user').all()
    total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    total_in_words = number_to_words(int(total_amount))  # Convert to words
    context = {
        'payments': payments,
        'total_amount': total_amount,
        'total_in_words': total_in_words  # Add this to the context
    }
    return render(request, 'admin2/salesdetails.html', context)



def number_to_words(number):
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
    teens = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
    
    def convert_below_thousand(n):
        if n < 10:
            return units[n]
        elif n < 20:
            return teens[n - 10]
        elif n < 100:
            return tens[n // 10] + (" " + units[n % 10] if n % 10 != 0 else "")
        else:
            return units[n // 100] + " Hundred" + (" and " + convert_below_thousand(n % 100) if n % 100 != 0 else "")
    
    if number == 0:
        return "Zero"
    
    result = ""
    if number >= 10000000:
        result += convert_below_thousand(number // 10000000) + " Crore "
        number %= 10000000
    if number >= 100000:
        result += convert_below_thousand(number // 100000) + " Lakh "
        number %= 100000
    if number >= 1000:
        result += convert_below_thousand(number // 1000) + " Thousand "
        number %= 1000
    if number > 0:
        result += convert_below_thousand(number)
    
    return result.strip()

@login_required
@never_cache
def invoice(request, payment_id):
    payment = get_object_or_404(Payment, payment_id=payment_id, user=request.user)
    
    # Convert the amount to an integer (assuming it's stored as a decimal)
    amount_in_rupees = int(payment.amount)
    
    # Convert the amount to words
    amount_in_words = number_to_words(amount_in_rupees)
    
    context = {
        'payment': payment,
        'user': request.user,
        'amount_in_words': amount_in_words,
        'amount_in_rupees': amount_in_rupees  # Add this for debugging
    }
    return render(request, 'user/invoice.html', context)


