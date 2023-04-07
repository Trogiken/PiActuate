from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def excluded_pin(value):
    if value in [31, 30]:
        raise ValidationError(
            _('pin %(value)s cannot be used for this operation'),
            params={'value': value},
        )