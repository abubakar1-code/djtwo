from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

def validate_password_strength(value):
    min_length = 8

    if len(value) < min_length:
        raise ValidationError(_('Password must be at least {0} characters '
                                'long.').format(min_length))

    # check for digit
    if not any(char.isdigit() for char in value):
        raise ValidationError(_('Password must contain at least 1 digit.'))

    # check for letter
    if not any(char.isalpha() for char in value):
        raise ValidationError(_('Password must contain at least 1 letter.'))

    # check for uppercase letter
    if not any(char.isupper() for char in value):
        raise ValidationError(_('Password must contain at least 1 Upper-Case letter.'))

    # check for lowercase letter
    if not any(char.islower() for char in value):
        raise ValidationError(_('Password must contain at least 1 Lower-Case letter.'))