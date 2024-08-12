from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
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
    path('get_subcategories/', views.get_subcategories, name='get_subcategories'),
    
    

    
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
