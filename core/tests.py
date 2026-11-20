from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import AdminProfile
from user.models import User as PassengerUser

User = get_user_model()


class AdminLoginTests(TestCase):
    """Tests for the manual administrator login flow in the core app."""

    def setUp(self):
        self.login_url = reverse('core:admin_login')
        self.dashboard_url = reverse('core:admin_dashboard')
        self.logout_url = reverse('core:admin_logout')
        self.home_url = reverse('core:home')

        self.admin_user = User.objects.create_superuser(
            username='adminuser',
            email='admin@example.com',
            password='AdminStrongPassword123!',
        )
        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='user@example.com',
            password='UserStrongPassword123!',
        )

    def test_home_redirects_to_login(self):
        response = self.client.get(self.home_url)
        self.assertRedirects(response, self.login_url)

    def test_login_page_renders_correctly(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'id="togglePassword"')
        self.assertContains(response, reverse('core:admin_register'))

    def test_empty_login_submission_shows_validation_errors(self):
        response = self.client.post(self.login_url, {'username': '', 'password': ''})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter your username.')
        self.assertContains(response, 'Please enter your password.')

    def test_invalid_credentials_show_error_message(self):
        response = self.client.post(
            self.login_url,
            {'username': 'adminuser', 'password': 'WrongPassword!'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password. Please try again.')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_non_admin_user_cannot_login(self):
        response = self.client.post(
            self.login_url,
            {'username': 'regularuser', 'password': 'UserStrongPassword123!'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Access denied. Administrator privileges are required to sign in.',
        )
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_valid_admin_login_redirects_to_dashboard(self):
        response = self.client.post(
            self.login_url,
            {'username': 'adminuser', 'password': 'AdminStrongPassword123!'},
            follow=True,
        )
        self.assertRedirects(response, self.dashboard_url)
        self.assertTemplateUsed(response, 'core/dashboard.html')
        self.assertContains(response, 'adminuser')
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_unauthenticated_dashboard_access_redirects_to_login(self):
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.dashboard_url}')

    def test_authenticated_admin_visiting_login_redirects_to_dashboard(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.dashboard_url)

    def test_admin_logout_redirects_to_login(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(self.logout_url, follow=True)
        self.assertRedirects(response, self.login_url)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, 'You have been signed out successfully.')


class AdminRegistrationAndDashboardTests(TestCase):
    """Tests for Task 5 (Admin Dashboard) and Task 6 (Manual Admin Registration)."""

    def setUp(self):
        self.register_url = reverse('core:admin_register')
        self.login_url = reverse('core:admin_login')
        self.dashboard_url = reverse('core:admin_dashboard')

        self.existing_user = User.objects.create_user(
            username='existingadmin',
            email='existing@example.com',
            password='StrongPassword123!',
            is_staff=True,
        )
        AdminProfile.objects.create(
            user=self.existing_user,
            full_name='Existing Admin',
            email='existing@example.com',
        )

    def test_register_page_renders_all_fields(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/register.html')
        self.assertContains(response, 'name="full_name"')
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'name="confirm_password"')

    def test_register_empty_submission_shows_required_errors(self):
        response = self.client.post(self.register_url, {})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter your full name.')
        self.assertContains(response, 'Please choose a username.')
        self.assertContains(response, 'Please enter your email address.')
        self.assertContains(response, 'Please enter a password.')
        self.assertContains(response, 'Please confirm your password.')

    def test_register_mismatched_passwords_rejected(self):
        response = self.client.post(
            self.register_url,
            {
                'full_name': 'New Admin',
                'username': 'newadmin',
                'email': 'newadmin@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'DifferentPassword123!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match.')
        self.assertFalse(User.objects.filter(username='newadmin').exists())

    def test_register_duplicate_username_rejected(self):
        response = self.client.post(
            self.register_url,
            {
                'full_name': 'Another Admin',
                'username': 'ExistingAdmin',
                'email': 'unique@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This username is already taken.')

    def test_register_duplicate_email_rejected(self):
        response = self.client.post(
            self.register_url,
            {
                'full_name': 'Another Admin',
                'username': 'uniqueadmin',
                'email': 'EXISTING@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'An account with this email address already exists.')

    def test_valid_registration_creates_hashed_user_and_profile_and_allows_login(self):
        response = self.client.post(
            self.register_url,
            {
                'full_name': 'Sneh Prajapati',
                'username': 'snehadmin',
                'email': 'sneh@example.com',
                'password': 'StrongPassword123!',
                'confirm_password': 'StrongPassword123!',
            },
            follow=True,
        )
        self.assertRedirects(response, self.login_url)
        self.assertContains(response, 'Admin account registered successfully. Please sign in.')

        user = User.objects.get(username='snehadmin')
        self.assertTrue(user.is_staff)
        self.assertNotEqual(user.password, 'StrongPassword123!')
        self.assertTrue(user.check_password('StrongPassword123!'))

        profile = AdminProfile.objects.get(user=user)
        self.assertEqual(profile.full_name, 'Sneh Prajapati')
        self.assertEqual(profile.email, 'sneh@example.com')

        login_response = self.client.post(
            self.login_url,
            {'username': 'snehadmin', 'password': 'StrongPassword123!'},
            follow=True,
        )
        self.assertRedirects(login_response, self.dashboard_url)
        self.assertTemplateUsed(login_response, 'core/dashboard.html')
        self.assertContains(login_response, 'Welcome, Sneh Prajapati')
        self.assertContains(login_response, 'Total Users')
        self.assertContains(login_response, 'Total Drivers')
        self.assertContains(login_response, 'Total Taxi Bookings')
        self.assertContains(login_response, 'sneh@example.com')
        self.assertEqual(login_response.context['total_users'], PassengerUser.objects.count())
        self.assertEqual(login_response.context['total_admins'], AdminProfile.objects.count())


class AdminForgotPasswordOTPTests(TestCase):
    """Tests for Tasks 7, 8, and 9 (Forgot Password, random OTP, console email)."""

    def setUp(self):
        self.forgot_url = reverse('core:admin_forgot_password')
        self.verify_url = reverse('core:admin_verify_otp')
        self.reset_url = reverse('core:admin_reset_password')
        self.login_url = reverse('core:admin_login')

        self.admin_user = User.objects.create_user(
            username='otpadmin',
            email='otpadmin@example.com',
            password='OldStrongPassword123!',
            is_staff=True,
        )
        AdminProfile.objects.create(
            user=self.admin_user,
            full_name='OTP Admin',
            email='otpadmin@example.com',
        )

    def test_forgot_password_page_renders_email_field(self):
        response = self.client.get(self.forgot_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/forgot_password.html')
        self.assertContains(response, 'name="email"')

    def test_unknown_email_shows_error_and_sends_no_email(self):
        response = self.client.post(self.forgot_url, {'email': 'unknown@example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No active administrator account was found with this email.')
        self.assertEqual(len(mail.outbox), 0)

    def test_full_otp_password_reset_flow(self):
        response = self.client.post(
            self.forgot_url,
            {'email': 'otpadmin@example.com'},
            follow=True,
        )
        self.assertRedirects(response, self.verify_url)
        self.assertEqual(len(mail.outbox), 1)

        otp = self.client.session.get('reset_otp')
        self.assertIsNotNone(otp)
        self.assertEqual(len(otp), 6)
        self.assertTrue(otp.isdigit())
        self.assertIn(otp, mail.outbox[0].body)

        bad_otp_response = self.client.post(self.verify_url, {'otp': '000000' if otp != '000000' else '111111'})
        self.assertEqual(bad_otp_response.status_code, 200)
        self.assertContains(bad_otp_response, 'Invalid OTP.')

        good_otp_response = self.client.post(self.verify_url, {'otp': otp}, follow=True)
        self.assertRedirects(good_otp_response, self.reset_url)

        reset_response = self.client.post(
            self.reset_url,
            {
                'new_password': 'NewStrongPassword456!',
                'confirm_password': 'NewStrongPassword456!',
            },
            follow=True,
        )
        self.assertRedirects(reset_response, self.login_url)
        self.assertContains(reset_response, 'Password reset successful.')
        self.assertIsNone(self.client.session.get('reset_otp'))

        login_response = self.client.post(
            self.login_url,
            {'username': 'otpadmin', 'password': 'NewStrongPassword456!'},
            follow=True,
        )
        self.assertRedirects(login_response, reverse('core:admin_dashboard'))


class BootstrapDashboardAndUserManagementTests(TestCase):
    """Tests for Tasks 11-17 (Bootstrap navbar, placeholder views, User model, User CRUD)."""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='bossadmin',
            email='boss@example.com',
            password='BossPassword123!',
        )
        self.client.force_login(self.admin_user)

    def test_dashboard_has_bootstrap_navbar_options_without_links_and_profile_image(self):
        response = self.client.get(reverse('core:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'bootstrap.min.css')
        self.assertContains(response, 'admin-avatar.svg')
        self.assertContains(response, '<span class="nav-link nav-option-text">Drivers</span>')
        self.assertContains(response, '<span class="nav-link nav-option-text">Users</span>')
        self.assertContains(response, '<span class="nav-link nav-option-text">Bookings</span>')

    def test_placeholder_views_render(self):
        for route in ('core:drivers_placeholder', 'core:users_placeholder', 'core:bookings_placeholder'):
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'core/placeholder.html')

    def test_user_create_list_edit_delete(self):
        list_url = reverse('core:user_list')
        create_res = self.client.post(
            list_url,
            {
                'name': 'Rahul Patel',
                'email': 'rahul@example.com',
                'mobile': '9876543210',
                'password': 'UserPass123!',
            },
            follow=True,
        )
        self.assertRedirects(create_res, list_url)
        self.assertContains(create_res, 'Rahul Patel')

        passenger = PassengerUser.objects.get(email='rahul@example.com')
        self.assertNotEqual(passenger.password, 'UserPass123!')

        edit_url = reverse('core:user_edit', args=[passenger.id])
        edit_res = self.client.post(
            edit_url,
            {
                'name': 'Rahul K Patel',
                'email': 'rahul@example.com',
                'mobile': '9998887776',
                'password': '',
            },
            follow=True,
        )
        self.assertRedirects(edit_res, list_url)
        self.assertContains(edit_res, 'Rahul K Patel')

        delete_url = reverse('core:user_delete', args=[passenger.id])
        delete_res = self.client.post(delete_url, follow=True)
        self.assertRedirects(delete_res, list_url)
        self.assertFalse(PassengerUser.objects.filter(pk=passenger.id).exists())
