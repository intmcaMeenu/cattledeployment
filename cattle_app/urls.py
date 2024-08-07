from django.urls import path
from . import views

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
]
