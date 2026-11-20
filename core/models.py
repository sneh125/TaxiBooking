from django.conf import settings
from django.db import models


class AdminProfile(models.Model):
    """Custom Admin profile table integrated with Django's authentication User model."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_profile',
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=60, default='System Administrator')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'admin_profiles'
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} ({self.user.username})'
