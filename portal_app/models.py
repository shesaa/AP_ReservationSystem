from django.db import models
from django.core import validators
from portal_app.validators import *


# Create your models here.


class User(models.Model):
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

    pass


class Clinic(models.Model):
    STATUS_CHOICE = [

        ("O", "open"),
        ("C", "closed")

    ]

    name = models.CharField(max_length=40)
    address = models.TextField()

    contact_number = models.CharField(max_length=11)

    status = models.CharField(max_length=1, choices=STATUS_CHOICE)

    pass


class Appointment(models.Model):
    STATUS_CHOICE = [

        ("R", "reserved"),
        ("C", "canceled"),
        ("P", "pending")

    ]

    clinic_id = models.ForeignKey(Clinic, on_delete=models.CASCADE)

    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    reservation_time = models.DateTimeField()

    reservation_status = models.CharField(max_length=1, choices=STATUS_CHOICE)

    pass


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    to_user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    date_time = models.DateTimeField(auto_now_add=True)
    # Add other necessary fields and methods
    pass
