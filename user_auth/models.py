from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import rest_framework.authtoken.models

from .validators import phone_regex_validator


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)
    phone_number = models.CharField(validators=[phone_regex_validator], unique=True,
                                    blank=True, null=True, max_length=11)
    profile_image = models.ImageField(upload_to='profile_image/', blank=True, null=True)

    REQUIRED_FIELDS = ["email"]

    def save(self, *args, **kwargs):
        if not self.phone_number:
            self.phone_number = None

        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.email


class Token(rest_framework.authtoken.models.Token):
    """
    key is no longer primary key, but still indexed and unique.
    relation to user is a ForeignKey, so each user can have more than one token.
    """

    key = models.CharField(_("Key"), max_length=40, db_index=True, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='auth_tokens',
        on_delete=models.CASCADE, verbose_name=_("User")
    )
