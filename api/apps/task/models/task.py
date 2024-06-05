from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class UserManager(BaseUserManager):


    def create_user(self, email, name, password=None, **extra_fields):

        if not email:
            raise ValueError('User must have an email address.')

        email = self.normalize_email(email)  # Modificação: Normalizar o email
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)  # Boas práticas

        return user

    def create_superuser(self, email, name, password):

        user = self.create_user(email, name, password)
        
        user.is_superuser = True
        user.save(using=self.db)

        return user


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        max_length=255,
        unique=True
    )
    name = models.CharField(
        max_length=255
    )

    objects = UserManager()  

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email

class TaskProfile(models.Model):

    title = models.CharField(
        _('Title'),
        max_length=255
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
        _('Deadline'),
        blank=True, 
        null=True
    )
    completed = models.BooleanField(
        _('Completed'),
        default=False
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
    created_in = models.DateTimeField(
        _('Created In'),
        auto_now_add=True
    )
    updated = models.DateTimeField(
        _('Updated'),
        auto_now=True
    )  
    responsible = models.ManyToManyField(
        User, 
        through='TaskResponsible', 
        related_name='tasks_responsible'
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

    def __str__(self):
        return f"{self.user} - {self.task}"



    
    
    
    
