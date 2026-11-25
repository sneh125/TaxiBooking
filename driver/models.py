from django.contrib.auth.hashers import make_password
from django.db import models


class Driver(models.Model):
    """Driver model for the Taxi Booking System."""

    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    license_number = models.CharField(max_length=50, unique=True)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith(('pbkdf2_', 'argon2$', 'bcrypt$')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.license_number})'
