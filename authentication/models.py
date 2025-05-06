from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password

class UserManager(BaseUserManager):
    def create_user(self, username, code, email=None, phone=None, name=None, serviceNumber=None):
        if not username:
            raise ValueError('Users must have a username')
        if not code:
            raise ValueError('Users must have a passcode')

        user = self.model(
            username=username,
            email=email,
            phone=phone,
            name=name,
            serviceNumber=serviceNumber,
            plain_code=code  # Store the plain code
        )
        # Store the code as a hashed value for security
        user.code = make_password(code)
        user.save(using=self._db)
        return user
    
        
    def create_superuser(self, username, password=None, code=None, email=None, phone=None, name=None, serviceNumber=None):
        """
        Creates and saves a superuser with the given credentials.
        Accepts either password or code parameter to handle Django's createsuperuser command.
        """
        # If password is provided but code is not, use password as code
        if password and not code:
            code = password
            
        if not code:
            raise ValueError('Superuser must have a passcode')
            
        user = self.create_user(
            username=username,
            code=code,
            email=email,
            phone=phone,
            name=name,
            serviceNumber=serviceNumber
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100, blank=True, null=True)
    serviceNumber = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=128)  # Hashed code for authentication
    plain_code = models.CharField(max_length=6, verbose_name="Passcode")  # Plain code for display
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    
    # Admin fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'serviceNumber'
    REQUIRED_FIELDS = ['username', 'code', 'name', 'email', 'phone']
    
    objects = UserManager()
    
    def __str__(self):
        return self.username
        
    def has_perm(self, perm, obj=None):
        return self.is_admin
        
    def has_module_perms(self, app_label):
        return self.is_admin
        
    def check_password(self, raw_code):
        """
        Override the check_password method to use the code field instead
        """
        return check_password(raw_code, self.code)
        
    def set_password(self, raw_code):
        """
        Override the set_password method to use the code field instead
        """
        self.plain_code = raw_code  # Store plain code
        self.code = make_password(raw_code)
        self._password = None
