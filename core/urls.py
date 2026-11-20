from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'core'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='core:admin_login', permanent=False), name='home'),
    path('login/', views.admin_login, name='admin_login'),
    path('register/', views.admin_register, name='admin_register'),
    path('forgot-password/', views.admin_forgot_password, name='admin_forgot_password'),
    path('verify-otp/', views.admin_verify_otp, name='admin_verify_otp'),
    path('reset-password/', views.admin_reset_password, name='admin_reset_password'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('drivers/', views.drivers_placeholder, name='drivers_placeholder'),
    path('bookings/', views.bookings_placeholder, name='bookings_placeholder'),
    path('users-placeholder/', views.users_placeholder, name='users_placeholder'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('logout/', views.admin_logout, name='admin_logout'),
]
