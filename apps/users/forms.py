
from django import forms
from .models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from .constants import GROUP_CUSTOMER

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password']

    def save(self, commit=True, group_name=GROUP_CUSTOMER):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            customer_group = Group.objects.get(name=group_name)
            user.groups.add(customer_group)
        return user
    
class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        if email and password:
            if not authenticate(email=email, password=password):
                raise forms.ValidationError("Invalid email or password")

        return cleaned_data