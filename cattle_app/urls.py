from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import download_invoice
from .views import invoice


urlpatterns = [
    # ... existing paths ...
    
    path('', views.index, name='index'),
    path('logout/', views.userlogout, name='logout'),
    path('login/', views.login_page, name='login_page'),
    path('register_page/', views.register_page, name='register_page'),
    path('admin_index/', views.admin_index, name='admin_index'),
    path('indexcattle/', views.indexcattle, name='indexcattle'),
    path('password_reset_request/', views.password_reset_request, name='password_reset_request'),
    path('reset_password/<str:token>/', views.reset_password, name='reset_password'),
    path('profile_completion/', views.profile_completion, name='profile_completion'),
    path('profile_view/', views.profile_view, name='profile_view'),
    path('profile_update/', views.profile_update, name='profile_update'), 
    path('admin_userview/', views.active_users, name='admin_userview'),
    path('toggleusers/<int:uid>/', views.toggleusers, name='toggleusers'),
    path('admin_category/', views.admin_category, name='admin_category'),
    path('category_edit/', views.category_edit, name='category_edit'),
    path('category_delete/', views.category_delete, name='category_delete'),
    path('admin_subcategory/', views.admin_subcategory, name='admin_subcategory'),
    path('subcategory_edit/', views.subcategory_edit, name='subcategory_edit'),
    path('subcategory_delete/', views.subcategory_delete, name='subcategory_delete'),
    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user_cattle/', views.user_cattle, name='user_cattle'),
    path('get-subcategories/', views.get_subcategories, name='get_subcategories'),
    path('user_productview/<int:product_id>/', views.user_productview, name='user_productview'),
    path('user_productlogview/<int:product_id>/', views.user_productlogview, name='user_productlogview'),
    path('adminview_cattle/', views.adminview_cattle, name='adminview_cattle'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('category_log/<int:category_id>/', views.category_detaillog, name='category_detaillog'), 
    path('update-cattle-status/<int:cattle_id>/', views.update_cattle_status, name='update_cattle_status'),
    path('toggle_subcategory_status/', views.toggle_subcategory_status, name='toggle_subcategory_status'),
   
    path('vaccination_center/', views.vaccination_center, name='vaccination_center'),
    path('toggle_vaccination_center/<int:center_id>/', views.toggle_vaccination_center, name='toggle_vaccination_center'),
    path('fetch_cattle_details/', views.fetch_cattle_details, name='fetch_cattle_details'),
    path('edit_cattle/<int:cattle_id>/', views.edit_cattle, name='edit_cattle'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:cattle_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('toggle_wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('wishlisted_item/', views.wishlisted_item, name='wishlisted_item'),
    path('remove_from_wishlist/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('payment/', views.payment, name='payment'),
    path('save_payment/', views.save_payment, name='save_payment'),
    path('payment_details/', views.payment_details, name='payment_details'),
    
    path('vaccination_center_dashboard/', views.vaccination_center_dashboard, name='vaccination_center_dashboard'),
    path('vaccination_center_logout/', views.vaccination_center_logout, name='vaccination_center_logout'),
    path('add_vaccine/', views.add_vaccine, name='add_vaccine'),
    path('get_cart_wishlist_counts/', views.get_cart_wishlist_counts, name='get_cart_wishlist_counts'),
    path('download_invoice/<str:payment_id>/', download_invoice, name='download_invoice'),
    path('sales_details/', views.sales_details_list, name='sales_details_list'),
    path('invoice/<str:payment_id>/', invoice, name='invoice'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
