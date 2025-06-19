# # File: cloud_storage/backend/users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


class CustomUser(AbstractUser):
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z][a-zA-Z0-9]{3,19}$',
        message="Логин должен начинаться с буквы, содержать только латинские буквы и цифры, длина от 4 до 20 символов."
    )

    username = models.CharField(
        max_length=20,
        unique=True,
        validators=[username_validator]
    )
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    storage_path = models.CharField(max_length=255, blank=True)

    # Переопределите поля groups и user_permissions с уникальными related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',  # Уникальное имя для CustomUser
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',  # Уникальное имя для CustomUser
        related_query_name='user',
    )

    def save(self, *args, **kwargs):
        if not self.storage_path:
            self.storage_path = f"user_{self.id}/"
        super().save(*args, **kwargs)
