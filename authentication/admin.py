from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from django import forms
from django.utils.html import format_html
from .models import User
import random
import string

# Unregister Groups and Token models
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Token)
except admin.sites.NotRegistered:
    pass

def generate_random_code(length=6):
    """Generate a random numeric code of specified length."""
    return ''.join(random.choices(string.digits, k=length))

class UserCreationForm(forms.ModelForm):
    """A form for creating new users with auto-generated code."""
    # Define a hidden field to store the generated code
    generated_code = forms.CharField(
        label='Generated Passcode',
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        help_text="This is the auto-generated passcode that will be assigned to the user."
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'serviceNumber', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Generate a random code and store it as an attribute of the form
        self.random_code = generate_random_code()
        # Set the initial value of the generated_code field
        self.initial['generated_code'] = self.random_code
        
        # Remove code field as it will be auto-generated
        if 'code' in self.fields:
            del self.fields['code']

    def save(self, commit=True):
        # Save the provided code
        user = super().save(commit=False)
        # Use the random code generated in __init__
        user.set_password(self.random_code)
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):
    """A form for updating users."""
    class Meta:
        model = User
        fields = ('username', 'email', 'name', 'serviceNumber', 'profile_image', 'phone', 'is_active', 'is_admin', 'is_staff')

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    list_display = ('profile_image_thumbnail', 'serviceNumber', 'name', 'username', 'email', 'plain_code', 'is_admin', 'is_staff')
    list_filter = ()
    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Personal info', {'fields': ('name', 'serviceNumber', 'email', 'phone', 'profile_image',)}),
        ('Permissions', {'fields': ('is_admin', 'is_staff', 'is_active')}),
        ('Passcode', {'fields': ('plain_code',), 'classes': ('collapse',), 'description': 'Passcode is read-only and auto-generated'}),
    )
    
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'name', 'serviceNumber', 'email', 'phone', 'profile_image', 'is_admin', 'is_staff', 'is_active', 'generated_code'),
            'description': format_html('<strong>Note:</strong> The passcode will be auto-generated and will be assigned to this user. Please make note of it as it will be needed for verification.'),
        }),
    )
    search_fields = ('username', 'email', 'name')
    ordering = ('username',)
    filter_horizontal = ()
    readonly_fields = ('plain_code',)

    def get_readonly_fields(self, request, obj=None):
        """
        Override to make plain_code read-only for existing users
        and generated_code read-only for new users
        """
        if obj:  # editing an existing object
            return self.readonly_fields + ('plain_code',)
        return self.readonly_fields + ('generated_code',)
    
    def profile_image_thumbnail(self, obj):
        """Display a thumbnail of the profile image in the admin list view."""
        if obj.profile_image:
            return format_html('<img src="{}" width="45px" height="45px" style="border-radius: 50%; object-fit: cover;" />', obj.profile_image.url)
        else:
            return format_html('<div style="width: 45px; height: 45px; border-radius: 50%; background-color: #e0e0e0; display: flex; align-items: center; justify-content: center; color: #757575;font-size:10px;">No<br>Image</div>')
    profile_image_thumbnail.short_description = 'Profile'

# Register the model with the custom admin
admin.site.register(User, UserAdmin)
