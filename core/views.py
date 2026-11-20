import random
import time

from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST

from .forms import (
    AdminForgotPasswordForm,
    AdminLoginForm,
    AdminRegistrationForm,
    AdminResetPasswordForm,
    AdminVerifyOTPForm,
    PassengerUserForm,
)
from .models import AdminProfile
from user.models import User as PassengerUser

User = get_user_model()


def _is_admin_user(user):
    """Return True if the user is an active administrator."""
    if not (user.is_authenticated and user.is_active and (user.is_staff or user.is_superuser)):
        return False
    admin_profile = getattr(user, 'admin_profile', None)
    if admin_profile is not None and not admin_profile.is_active:
        return False
    return True


@never_cache
def admin_login(request):
    """Handle manual administrator login using Django's built-in authentication."""
    if _is_admin_user(request.user):
        return redirect('core:admin_dashboard')

    form = AdminLoginForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is None:
                form.add_error(None, 'Invalid username or password. Please try again.')
            elif not user.is_active:
                form.add_error(None, 'This account is inactive. Please contact the system administrator.')
            elif not (user.is_staff or user.is_superuser):
                form.add_error(None, 'Access denied. Administrator privileges are required to sign in.')
            elif getattr(user, 'admin_profile', None) is not None and not user.admin_profile.is_active:
                form.add_error(None, 'This administrator profile is inactive. Please contact the system administrator.')
            else:
                login(request, user)
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    return redirect(next_url)
                return redirect('core:admin_dashboard')

    context = {
        'form': form,
        'next': request.POST.get('next') or request.GET.get('next', ''),
    }
    return render(request, 'core/login.html', context)


@never_cache
def admin_register(request):
    """Handle manual administrator registration and store profile in AdminProfile."""
    form = AdminRegistrationForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Admin account registered successfully. Please sign in.')
            return redirect('core:admin_login')
        messages.error(request, 'Registration failed. Please fix the errors below.')

    return render(request, 'core/register.html', {'form': form})


def _get_admin_context(request):
    """Return common admin profile details for Bootstrap admin templates."""
    admin_profile = getattr(request.user, 'admin_profile', None)
    admin_full_name = (
        admin_profile.full_name
        if admin_profile
        else (request.user.get_full_name() or request.user.username)
    )
    admin_email = (admin_profile.email if admin_profile else request.user.email) or 'Not provided'
    admin_role = (
        admin_profile.role
        if admin_profile
        else ('Superuser' if request.user.is_superuser else 'Staff Administrator')
    )
    return {
        'admin_profile': admin_profile,
        'admin_full_name': admin_full_name,
        'admin_email': admin_email,
        'admin_role': admin_role,
    }


@never_cache
@login_required
def admin_dashboard(request):
    """Render the administrator dashboard after successful authentication."""
    if not _is_admin_user(request.user):
        logout(request)
        messages.error(request, 'Access denied. Administrator privileges are required.')
        return redirect('core:admin_login')

    context = {
        **_get_admin_context(request),
        'total_users': PassengerUser.objects.count(),
        'total_admins': AdminProfile.objects.count(),
        'total_drivers': 0,
        'total_bookings': 0,
    }
    return render(request, 'core/dashboard.html', context)


# Task 15: Placeholder views for future modules (Drivers, Users, Bookings)
@never_cache
@login_required
def drivers_placeholder(request):
    if not _is_admin_user(request.user):
        return redirect('core:admin_login')
    context = {
        **_get_admin_context(request),
        'module_name': 'Drivers',
        'module_description': 'Driver registration, license verification, and vehicle assignment will be managed here.',
    }
    return render(request, 'core/placeholder.html', context)


@never_cache
@login_required
def users_placeholder(request):
    if not _is_admin_user(request.user):
        return redirect('core:admin_login')
    context = {
        **_get_admin_context(request),
        'module_name': 'Users',
        'module_description': 'Passenger management module overview.',
    }
    return render(request, 'core/placeholder.html', context)


@never_cache
@login_required
def bookings_placeholder(request):
    if not _is_admin_user(request.user):
        return redirect('core:admin_login')
    context = {
        **_get_admin_context(request),
        'module_name': 'Bookings',
        'module_description': 'Taxi ride bookings, fare calculation, and dispatch tracking will be managed here.',
    }
    return render(request, 'core/placeholder.html', context)


# Task 17: User listing page for admin with add / edit / delete options
@never_cache
@login_required
def user_list(request):
    """List all Taxi Booking users and allow adding a new user."""
    if not _is_admin_user(request.user):
        return redirect('core:admin_login')

    form = PassengerUserForm(request.POST if request.method == 'POST' else None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'New user added successfully.')
        return redirect('core:user_list')

    users = PassengerUser.objects.order_by('-created_at')
    context = {
        **_get_admin_context(request),
        'users': users,
        'form': form,
    }
    return render(request, 'core/users_list.html', context)


@never_cache
@login_required
def user_edit(request, user_id):
    """Edit an existing user's details."""
    if not _is_admin_user(request.user):
        return redirect('core:admin_login')

    passenger = get_object_or_404(PassengerUser, pk=user_id)
    form = PassengerUserForm(request.POST if request.method == 'POST' else None, instance=passenger)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'User "{passenger.name}" updated successfully.')
        return redirect('core:user_list')

    context = {
        **_get_admin_context(request),
        'form': form,
        'passenger': passenger,
    }
    return render(request, 'core/user_edit.html', context)


@require_POST
@login_required
def user_delete(request, user_id):
    """Delete an existing user."""
    if not _is_admin_user(request.user):
        return redirect('core:admin_login')

    passenger = get_object_or_404(PassengerUser, pk=user_id)
    name = passenger.name
    passenger.delete()
    messages.success(request, f'User "{name}" deleted successfully.')
    return redirect('core:user_list')


@require_POST
def admin_logout(request):
    """Log out the current administrator and redirect to the login page."""
    logout(request)
    messages.success(request, 'You have been signed out successfully.')
    return redirect('core:admin_login')


OTP_EXPIRY_SECONDS = 600  # 10 minutes


def _find_admin_by_email(email):
    """Return an active admin User matching the given email, or None."""
    profile = AdminProfile.objects.select_related('user').filter(email__iexact=email).first()
    if profile and profile.is_active and profile.user.is_active and (profile.user.is_staff or profile.user.is_superuser):
        return profile.user

    user = User.objects.filter(email__iexact=email, is_active=True).first()
    if user and (user.is_staff or user.is_superuser):
        user_profile = getattr(user, 'admin_profile', None)
        if user_profile is None or user_profile.is_active:
            return user
    return None


def _clear_reset_session(request):
    """Remove password reset OTP state from the session."""
    for key in ('reset_otp', 'reset_email', 'reset_user_id', 'reset_otp_created_at', 'reset_verified'):
        request.session.pop(key, None)


@never_cache
def admin_forgot_password(request):
    """Accept admin email, generate a 6-digit OTP via random, and send it via console email."""
    form = AdminForgotPasswordForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        admin_user = _find_admin_by_email(email)

        if admin_user is None:
            form.add_error('email', 'No active administrator account was found with this email.')
        else:
            otp = str(random.randint(100000, 999999))
            request.session['reset_otp'] = otp
            request.session['reset_email'] = email
            request.session['reset_user_id'] = admin_user.pk
            request.session['reset_otp_created_at'] = time.time()
            request.session['reset_verified'] = False

            send_mail(
                subject='Taxi Booking System - Admin Password Reset OTP',
                message=(
                    f'Hello {admin_user.username},\n\n'
                    f'Your 6-digit OTP for resetting your Taxi Booking System admin password is: {otp}\n\n'
                    f'This OTP is valid for 10 minutes. If you did not request this, please ignore this email.'
                ),
                from_email='noreply@taxibooking.local',
                recipient_list=[email],
                fail_silently=False,
            )
            messages.success(request, f'A 6-digit OTP has been sent to {email} (check console output).')
            return redirect('core:admin_verify_otp')

    return render(request, 'core/forgot_password.html', {'form': form})


@never_cache
def admin_verify_otp(request):
    """Verify the 6-digit OTP stored in the session."""
    session_otp = request.session.get('reset_otp')
    reset_user_id = request.session.get('reset_user_id')
    created_at = request.session.get('reset_otp_created_at')

    if not session_otp or not reset_user_id or not created_at:
        messages.error(request, 'Please request a password reset OTP first.')
        return redirect('core:admin_forgot_password')

    if time.time() - float(created_at) > OTP_EXPIRY_SECONDS:
        _clear_reset_session(request)
        messages.error(request, 'Your OTP has expired. Please request a new one.')
        return redirect('core:admin_forgot_password')

    form = AdminVerifyOTPForm(request.POST if request.method == 'POST' else None)

    if request.method == 'POST' and form.is_valid():
        entered_otp = form.cleaned_data['otp']
        if entered_otp != session_otp:
            form.add_error('otp', 'Invalid OTP. Please check the console email and try again.')
        else:
            request.session['reset_verified'] = True
            messages.success(request, 'OTP verified. You can now set a new password.')
            return redirect('core:admin_reset_password')

    return render(
        request,
        'core/verify_otp.html',
        {'form': form, 'reset_email': request.session.get('reset_email', '')},
    )


@never_cache
def admin_reset_password(request):
    """Allow setting a new password after OTP verification."""
    reset_verified = request.session.get('reset_verified')
    reset_user_id = request.session.get('reset_user_id')

    if not reset_verified or not reset_user_id:
        messages.error(request, 'Please verify your OTP before resetting your password.')
        return redirect('core:admin_forgot_password')

    admin_user = User.objects.filter(pk=reset_user_id, is_active=True).first()
    if admin_user is None:
        _clear_reset_session(request)
        messages.error(request, 'Administrator account not found. Please start again.')
        return redirect('core:admin_forgot_password')

    form = AdminResetPasswordForm(
        request.POST if request.method == 'POST' else None,
        user=admin_user,
    )

    if request.method == 'POST' and form.is_valid():
        admin_user.set_password(form.cleaned_data['new_password'])
        admin_user.save(update_fields=['password'])
        _clear_reset_session(request)
        messages.success(request, 'Password reset successful. Please sign in with your new password.')
        return redirect('core:admin_login')

    return render(request, 'core/reset_password.html', {'form': form})
