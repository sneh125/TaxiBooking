from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import AdminProfile
from user.models import User as PassengerUser

User = get_user_model()


class AdminLoginForm(forms.Form):
    """Manual login form for Taxi Booking System administrators."""

    username = forms.CharField(
        label='Username',
        max_length=150,
        strip=True,
        error_messages={
            'required': 'Please enter your username.',
            'max_length': 'Username must be 150 characters or fewer.',
        },
        widget=forms.TextInput(
            attrs={
                'id': 'id_username',
                'class': 'form-input',
                'placeholder': 'Enter your admin username',
                'autocomplete': 'username',
                'autofocus': True,
            }
        ),
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        error_messages={
            'required': 'Please enter your password.',
        },
        widget=forms.PasswordInput(
            attrs={
                'id': 'id_password',
                'class': 'form-input form-input-password',
                'placeholder': 'Enter your password',
                'autocomplete': 'current-password',
            }
        ),
    )


class AdminRegistrationForm(forms.Form):
    """Manual registration form for creating Taxi Booking System administrators."""

    full_name = forms.CharField(
        label='Full Name',
        max_length=150,
        strip=True,
        error_messages={
            'required': 'Please enter your full name.',
            'max_length': 'Full name must be 150 characters or fewer.',
        },
        widget=forms.TextInput(
            attrs={
                'id': 'id_full_name',
                'class': 'form-input',
                'placeholder': 'Enter your full name',
                'autocomplete': 'name',
                'autofocus': True,
            }
        ),
    )
    username = forms.CharField(
        label='Username',
        max_length=150,
        strip=True,
        error_messages={
            'required': 'Please choose a username.',
            'max_length': 'Username must be 150 characters or fewer.',
        },
        widget=forms.TextInput(
            attrs={
                'id': 'id_username',
                'class': 'form-input',
                'placeholder': 'Choose an admin username',
                'autocomplete': 'username',
            }
        ),
    )
    email = forms.EmailField(
        label='Email Address',
        max_length=254,
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Please enter a valid email address.',
        },
        widget=forms.EmailInput(
            attrs={
                'id': 'id_email',
                'class': 'form-input',
                'placeholder': 'admin@example.com',
                'autocomplete': 'email',
            }
        ),
    )
    password = forms.CharField(
        label='Password',
        strip=False,
        error_messages={
            'required': 'Please enter a password.',
        },
        widget=forms.PasswordInput(
            attrs={
                'id': 'id_password',
                'class': 'form-input form-input-password',
                'placeholder': 'Create a strong password',
                'autocomplete': 'new-password',
            }
        ),
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        strip=False,
        error_messages={
            'required': 'Please confirm your password.',
        },
        widget=forms.PasswordInput(
            attrs={
                'id': 'id_confirm_password',
                'class': 'form-input form-input-password',
                'placeholder': 'Re-enter your password',
                'autocomplete': 'new-password',
            }
        ),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('This username is already taken. Please choose another.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if (
            User.objects.filter(email__iexact=email).exists()
            or AdminProfile.objects.filter(email__iexact=email).exists()
        ):
            raise ValidationError('An account with this email address already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        if password:
            temp_user = User(username=username or '', email=email or '')
            try:
                validate_password(password, user=temp_user)
            except ValidationError as exc:
                self.add_error('password', exc)

        return cleaned_data

    def save(self):
        """Create the Django auth User (staff) and linked AdminProfile atomically."""
        full_name = self.cleaned_data['full_name']
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        name_parts = full_name.split(None, 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_staff=True,
                is_active=True,
            )
            admin_profile = AdminProfile.objects.create(
                user=user,
                full_name=full_name,
                email=email,
            )
        return admin_profile


class AdminForgotPasswordForm(forms.Form):
    """Form to request a password reset OTP via admin email."""

    email = forms.EmailField(
        label='Admin Email Address',
        max_length=254,
        error_messages={
            'required': 'Please enter your registered email address.',
            'invalid': 'Please enter a valid email address.',
        },
        widget=forms.EmailInput(
            attrs={
                'id': 'id_email',
                'class': 'form-input',
                'placeholder': 'Enter your registered admin email',
                'autocomplete': 'email',
                'autofocus': True,
            }
        ),
    )

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()


class AdminVerifyOTPForm(forms.Form):
    """Form to verify the 6-digit OTP sent for password reset."""

    otp = forms.CharField(
        label='6-Digit OTP',
        max_length=6,
        min_length=6,
        strip=True,
        error_messages={
            'required': 'Please enter the 6-digit OTP.',
            'min_length': 'OTP must be 6 digits.',
            'max_length': 'OTP must be 6 digits.',
        },
        widget=forms.TextInput(
            attrs={
                'id': 'id_otp',
                'class': 'form-input',
                'placeholder': 'Enter 6-digit OTP',
                'inputmode': 'numeric',
                'maxlength': '6',
                'autocomplete': 'one-time-code',
                'autofocus': True,
            }
        ),
    )

    def clean_otp(self):
        otp = self.cleaned_data['otp'].strip()
        if not otp.isdigit() or len(otp) != 6:
            raise ValidationError('OTP must be a valid 6-digit number.')
        return otp


class AdminResetPasswordForm(forms.Form):
    """Form to set a new password after OTP verification."""

    new_password = forms.CharField(
        label='New Password',
        strip=False,
        error_messages={'required': 'Please enter a new password.'},
        widget=forms.PasswordInput(
            attrs={
                'id': 'id_new_password',
                'class': 'form-input form-input-password',
                'placeholder': 'Create a new strong password',
                'autocomplete': 'new-password',
                'autofocus': True,
            }
        ),
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        strip=False,
        error_messages={'required': 'Please confirm your new password.'},
        widget=forms.PasswordInput(
            attrs={
                'id': 'id_confirm_password',
                'class': 'form-input form-input-password',
                'placeholder': 'Re-enter your new password',
                'autocomplete': 'new-password',
            }
        ),
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

        if new_password:
            try:
                validate_password(new_password, user=self.user)
            except ValidationError as exc:
                self.add_error('new_password', exc)

        return cleaned_data


class PassengerUserForm(forms.ModelForm):
    """Simple beginner-friendly form to create or edit a Taxi Booking User."""

    password = forms.CharField(
        label='Password',
        required=False,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter password'}
        ),
    )

    class Meta:
        model = PassengerUser
        fields = ['name', 'email', 'mobile', 'password']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile number'}),
        }

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        # Password is required when creating a new user, optional when editing
        if not self.instance.pk and not password:
            raise ValidationError('Please enter a password for the new user.')
        return password

    def save(self, commit=True):
        user_obj = super().save(commit=False)
        raw_password = self.cleaned_data.get('password')
        if raw_password:
            user_obj.password = raw_password
        elif self.instance.pk:
            # Keep the existing hashed password if left blank during edit
            user_obj.password = PassengerUser.objects.get(pk=self.instance.pk).password
        if commit:
            user_obj.save()
        return user_obj
