from django.core.validators import RegexValidator


phone_number_validator = RegexValidator(
    regex=r'^09\d{9}',
    message="Phone number must be 11 digits, starting with '09' ."
)