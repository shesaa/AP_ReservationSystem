import sched
from unicodedata import category
from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
# from django.contrib.auth.models import User
# from more_itertools import quantify
from portal_app.models import *
from datetime import datetime
from portal_app.models import User


class UserRegistration(forms.ModelForm):
    USER_TYPE_CHOICES = [
        ("P", "patient"),
        ("C", "Clinic staff"),
    ]

    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)
    phone_number = forms.CharField(max_length=11)
    email = forms.EmailField(max_length=254)
    age = forms.IntegerField()

    class Meta:
        model = User
        fields = ('username', 'password', 'user_type', 'phone_number', 'email', 'age')


class UserLogin(forms.ModelForm):

    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)  # Use PasswordInput widget


    class Meta:
        model = User
        fields = ('username', 'password')




class SetAppointment(forms.ModelForm):

    reservation_time = forms.CharField(max_length="250")

    clinic_id = models.CharField(max_length="250")

    # reservation_time = models.DateTimeField()

    class Meta:
        model = Appointment
        fields = ('reservation_time', 'clinic_id')


# class UserRegistration(forms.ModelForm):
#     USER_TYPE_CHOICES = [
#         ("P", "patient"),
#         ("C", "Clinic staff")
#     ]
#
#     username = forms.CharField(max_length=20)
#
#     password = forms.CharField(max_length=50)
#
#     user_type = forms.CharField()
#
#     phone_number = forms.CharField(max_length=11)
#
#     email = forms.EmailField(max_length=254)
#
#     age = forms.IntegerField()
#
#     class Meta:
#         model = User
#         fields = ('username', 'password', 'user_type', 'phone_number', 'email', 'age')
#         field_classes = {'username': forms.CharField, 'password': forms.CharField, 'user_type': forms.CharField, 'phone_number': forms.CharField, 'email': forms.EmailField, 'age': forms.IntegerField}
#
#     def clean_email(self):
#         email = self.cleaned_data['email']
#         try:
#             user = User.objects.get(email=email)
#         except Exception as e:
#             return email
#         raise forms.ValidationError(f"The {user.email} mail is already exists/taken")
#
#     def clean_username(self):
#         username = self.cleaned_data['username']
#         try:
#             user = User.objects.get(username=username)
#         except Exception as e:
#             return username
#         raise forms.ValidationError(f"The {user.username} mail is already exists/taken")


class UpdateProfile(UserChangeForm):
    username = forms.CharField(max_length=250, help_text="The Username field is required.")
    email = forms.EmailField(max_length=250, help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250, help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250, help_text="The Last Name field is required.")
    current_password = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name')

    def clean_current_password(self):
        if not self.instance.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError(f"Password is Incorrect")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(email=email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(username=username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already exists/taken")


class UpdatePasswords(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm rounded-0'}), label="Old Password")
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm rounded-0'}), label="New Password")
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control form-control-sm rounded-0'}),
        label="Confirm New Password")

    class Meta:
        model = User
        fields = ('old_password', 'new_password1', 'new_password2')


