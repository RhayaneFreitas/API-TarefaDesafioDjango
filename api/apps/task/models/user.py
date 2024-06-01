from django.contrib.auth.models import (
    User as AuthUser,
)
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserProfileManager(models.Manager):
    """Manager for user profiles"""
    
    def create_user(self, email, name, password=None):
        """Create a new user profile"""
        if not email:
            raise ValueError("User must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password) 
        user.save(using=self._db) 
        
        return user
    
    def create_superuser(self, email, name, password):
        """Create and save a new superuser with given details"""
        user = self.create_user(email, name, password)
        
        user.is_superuser = True
        user.save(using=self.db)

        return user

class TaskProfile(models.Model):
    
    title = models.CharField(
        _('Title'),
        max_length=255,
    )
    release = models.DateField(
        _('Release'),
        blank=True,
        null=True
    )
    description = models.TextField(
        _('Description'),
        blank=True,
        null=True
    )
    deadline = models.DateField(
        _('deadline'),
        blank=True,
        null=True
    )
    completed = models.BooleanField(
        _('Completed'),
        default=False
    )
    created_by = models.ForeignKey(
        AuthUser,
        on_delete=models.PROTECT,
        related_name='task_profiles_created',
        verbose_name=_('Created By')
    )
    finished_in = models.DateField(
        _('Finished In'),
        blank=True,
        null=True
    )
    finished_by = models.ForeignKey(
        AuthUser,
        on_delete=models.PROTECT,
        related_name='task_profiles_finished',
        verbose_name=_('Finished By'),
        blank=True,
        null=True
    )
    created_in = models.DateField(
        _('Created In'),
        blank=True,
        null=True
    )
    updated = models.DateField(
        _('Updated'),
        blank=True,
        null=True
    )
    responsible = models.ManyToManyField(
        AuthUser,
        through='TaskResponsible',
        related_name='tasks_responsible'
    )

    objects = UserProfileManager()

    def __str__(self):
        return self.title

class TaskResponsible(models.Model):
    task = models.ForeignKey(
        TaskProfile,
        on_delete=models.PROTECT,
        verbose_name=_('Task')
    )
    user = models.ForeignKey(
        AuthUser,
        on_delete=models.PROTECT,
        verbose_name=_('User')
    )

    def __str__(self):
        return f"{self.user} - {self.task}"


    
    
    
    
