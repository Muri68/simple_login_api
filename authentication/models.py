from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError

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


def validate_nigerian_phone(value):
    """
    Validate that the phone number is a Nigerian phone number.
    Nigerian numbers start with 0 followed by a carrier code and are 11 digits,
    or start with +234 followed by 10 digits.
    """
    import re
    # Pattern for Nigerian phone numbers (0XX... or +234XX...)
    pattern = r'^(0[789][01]\d{8}|\+234[789][01]\d{8})$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Enter a valid Nigerian phone number (e.g., 08012345678 or +2348012345678)'
        )
        
        
class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100, blank=True, null=True)
    serviceNumber = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=128)  # Hashed code for authentication
    plain_code = models.CharField(max_length=6, verbose_name="Passcode")
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=14, blank=True, null=True,
        validators=[
            MinLengthValidator(11, message="Phone Number must be at least 11 characters long."),
            validate_nigerian_phone
        ],
        help_text="Nigerian phone number (e.g., 08012345678 or +2348012345678)"
    )
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
    
    def save(self, *args, **kwargs):
        self.username = self.username.lower()
        self.email = self.email.lower()
        self.serviceNumber = self.serviceNumber.upper()
        super().save(*args, **kwargs)
