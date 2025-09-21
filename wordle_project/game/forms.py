from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser
import re

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if len(username) < 5:
            raise ValidationError("Username must be at least 5 characters long.")

        # 2. Check for mixed case (upper and lower)
        has_upper = any(c.isupper() for c in username)
        has_lower = any(c.islower() for c in username)
        
        if not (has_upper and has_lower):
            raise ValidationError("Username must contain both uppercase and lowercase letters.")

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        if password:
            # 1. Check length
            if len(password) < 5:
                raise ValidationError("Password must be at least 5 characters long.")
            
            # 2. Check for alpha, numeric, and special characters
            
            # Check for at least one alphabetic character (A-Z, a-z)
            if not re.search(r'[a-zA-Z]', password):
                raise ValidationError("Password must contain at least one alphabetic character.")

            # Check for at least one digit (0-9)
            if not re.search(r'[0-9]', password):
                raise ValidationError("Password must contain at least one numeric character.")

            # Check for at least one required special character ($, %, *, @)
            if not re.search(r'[$%*@]', password):
                raise ValidationError("Password must contain at least one special character from: $, %, *, or @.")

        return password

    def save(self, commit=True):
        # Override save method to hash the password securely
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        
        user.is_staff = False
        user.is_superuser = False
        
        if commit:
            user.save()
        return user