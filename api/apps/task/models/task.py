from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, email, name, password=None):

        if not email:
            raise ValueError('User must have an email address.')

        email = self.normalize_email(email)  # Modificação: Normalizar o email
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)  # Boas práticas

        return user

    def create_superuser(self, email, name, password):

        user = self.create_user(email, name, password)
        
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        _('Email Address'),
        unique=True,
        max_length=255   
    )
    name = models.CharField(
        _('Name'),
        max_length=255   
    )
    is_active = models.BooleanField(
        _('Active'),
        default=True
    )
    is_staff = models.BooleanField(
        _('Staff'),
        default=False
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name
    
    def __str__(self):
        return self.email    

class TaskProfile(models.Model):

    title = models.CharField(
        _('Title'),
        max_length=255
    )
    description = models.TextField(
        _('Description'),
        blank=True,
        null=True
    )
    deadline = models.DateField(
        _('Deadline'),
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
    created_by = models.ForeignKey(
        User,
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
        User,
        on_delete=models.PROTECT,
        related_name='task_profiles_finished',
        verbose_name=_('Finished By'),
        blank=True,
        null=True
    )
    responsible = models.ManyToManyField(
        User, 
        through='TaskResponsible', 
        related_name='tasks_responsible'
    )
    release = models.DateField(
        _('Release'),
        blank=True,
        null=True
    )
    completed = models.BooleanField(
        _('Completed'),
        default=False
    )

    def __str__(self):
        return self.title

class TaskResponsible(models.Model):

    task = models.ForeignKey(
        TaskProfile,
        on_delete=models.PROTECT,
        verbose_name=_('Task')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_('User')
    )
    
    class Meta:
        unique_together = [['task', 'user']]

    def __str__(self):
        return f"{self.user} - {self.task}"



    
    
    
    
