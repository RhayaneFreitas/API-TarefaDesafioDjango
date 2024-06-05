from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields): # Extra_fields(Podemos fornecer Argumentos de palavras Chave(ex: name))
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db) # Boas Práticas

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user
    


class User(AbstractBaseUser,
           PermissionsMixin): # Contém funcionalidades do sistema de autenticação | Funcionalidades para recursos de permissões do Django

    email = models.EmailField(
        max_length=255,
        unique=True
    )
    name = models.CharField(
        max_length=255
    )
    is_active = models.BooleanField(
        default=True
    )
    is_staff = models.BooleanField( # Se a equipe pode fazer login no admin do Django. Como não queremos usuários comuns, se pos Falso  
        default=False
    )

    objects = UserManager()

    USERNAME_FIELD = 'email' # Campo que queremos para authenticação | Substitui o campo padrão de models que usa o username