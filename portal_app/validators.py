from django.core.exceptions import ValidationError






def phone_validator(phone_number):
    if len(phone_number) != 11:
        raise ValidationError("Phone number must be 11 Characters")
    if phone_number[:2] != "09":
        raise ValidationError("Invalid Phone number")
    pass

