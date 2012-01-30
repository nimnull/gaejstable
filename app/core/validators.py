import re
from wtforms.validators import Regexp


email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'  # quoted-string
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE)  # domain


class Email(Regexp):
    """
    Validates an email address. Note that this uses a very primitive regular
    expression and should only be used in instances where you later verify by
    other means, such as email activation or lookups.

    :param message:
        Error message to raise in case
        of a validation error.
    """
    def __init__(self, message=None):
        super(Email, self).__init__(email_re, message=message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'Invalid email address.')
        super(Email, self).__call__(form, field)


def strip_validator(prop, value):
    return value.strip()
