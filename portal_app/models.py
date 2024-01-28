from django.db import models
from django.core import validators
from portal_app.validators import *

# Create your models here.

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError(('The Username must be set'))
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(('Superuser must have is_superuser=True.'))

        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ("P", "patient"),
        ("C", "Clinic staff")
    ]

    username = models.CharField(max_length=20, unique=True,
                                validators=[validators.MinLengthValidator(5), validators.MaxLengthValidator(20),
                                            validators.RegexValidator(r'^[A-Za-z0-9_]*[a-zA-Z]+[A-Za-z0-9_]*$')])

    password = models.CharField(max_length=50, validators=[validators.MinLengthValidator(8)])

    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES)

    phone_number = models.CharField(max_length=11, null=False, validators=[phone_validator])

    email = models.EmailField(max_length=254, null=True, validators=[validators.EmailValidator()], blank=True)

    age = models.IntegerField(null=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number', 'age', 'user_type']  # Adjust this based on your needs

    def __str__(self):
        return self.username


# class User(models.Model):
#     USER_TYPE_CHOICES = [
#         ("P", "patient"),
#         ("C", "Clinic staff")
#     ]
#
#     username = models.CharField(max_length=20, unique=True,
#                                 validators=[validators.MinLengthValidator(5), validators.MaxLengthValidator(20),
#                                             validators.RegexValidator(r'^[A-Za-z0-9_]*[a-zA-Z]+[A-Za-z0-9_]*$')])
#
#     password = models.CharField(max_length=50, validators=[validators.MinLengthValidator(8)])
#
#     user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES)
#
#     phone_number = models.CharField(max_length=11, null=False, validators=[phone_validator])
#
#     email = models.EmailField(max_length=254, null=True, validators=[validators.EmailValidator()], blank=True)
#
#     age = models.IntegerField(null=False)
#
#     pass


# class PatientUser(User):
#     USER_TYPE_CHOICES = [
#         ("P", "patient"),
#         ("C", "Clinic staff")
#     ]
#     user_type = models.CharField('P')
#
#
# class ClinicUser(User):
#     USER_TYPE_CHOICES = [
#         ("P", "patient"),
#         ("C", "Clinic staff")
#     ]
#     user_type = models.CharField('C')


class Clinic(models.Model):
    STATUS_CHOICE = [

        ("O", "open"),
        ("C", "closed")

    ]

    clinic_id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=40)
    address = models.TextField()

    contact_number = models.CharField(max_length=11)

    status = models.CharField(max_length=1, choices=STATUS_CHOICE)

    pass


class Appointment(models.Model):
    STATUS_CHOICE = [

        ("R", "reserved"),
        ("C", "canceled"),
        ("NR", "not reserved")

    ]

    appointment_id = models.AutoField(primary_key=True)

    clinic_id = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='clinic_appointments', null=True,
                                  blank=True)

    dr_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments', null=True)

    patient_reserved_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True,
                                            related_name='reserved_appointments')

    reservation_time = models.DateTimeField()

    reservation_status = models.CharField(max_length=2, choices=STATUS_CHOICE, default="NR")

    pass


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    pass
