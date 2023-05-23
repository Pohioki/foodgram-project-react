from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import F, Q, UniqueConstraint


class User(AbstractUser):
    """
    Custom user model representing a user of the application.
    """

    username_validator = UnicodeUsernameValidator()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)

    first_name = models.CharField(verbose_name='First Name',
                                  max_length=settings.LENGTH_USERS)
    last_name = models.CharField(verbose_name='Last Name',
                                 max_length=settings.LENGTH_USERS)
    email = models.EmailField(verbose_name='Email',
                              max_length=settings.LENGTH_USERS,
                              unique=True)
    username = models.CharField(verbose_name='Username',
                                max_length=settings.LENGTH_USERS,
                                unique=True)

    class Meta:
        ordering = ('username',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """
    Model representing the relationship
    between users for following each other.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='User',
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Author',
        related_name='following'
    )

    class Meta:
        ordering = ('-id',)
        constraints = [
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=~Q(user=F('author')),
                name='no_self_follow'
            )
        ]
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'

    def __str__(self):
        return (f'User {self.user} is following author {self.author}')
