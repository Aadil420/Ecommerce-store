# forms.py
from django import forms
from django.contrib.auth.models import User, Group

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'  # Specify the fields you want or use '__all__' for all fields

class CustomGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'  # Specify the fields you want or use '__all__' for all fields
