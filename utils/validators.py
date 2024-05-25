from django.core.validators import RegexValidator
import os


iran_phone_number_validator = RegexValidator(
    regex=r'^09\d{9}',
    message="Phone number must be 11 digits, starting with '09' ."
)

just_number_validator = RegexValidator(
    regex=r'^[+]?[0-9]*$',
    message="Phone number must be digits. (+) can be at first"
)


def check_file_extension(file, extensions):
    ext = os.path.splitext(file.name)[1].lower()[1:]
    if ext in extensions:
        return True
    return False


def check_file_size(file, max_size=10):
    max_file_size = max_size * 1024 * 1024  #MB
    if file.size <= max_file_size:
        return True
    return False

