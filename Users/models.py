from django.db import models

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import PermissionsMixin, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser
# from .managers import UserManager
from django.utils.translation import ugettext_lazy as _
import jwt


# Abstracted User manager.
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, full_name=None, organization=None,
                    email=None, phone=None, admin=False, staff=False, active=True):
        if not username:
            raise ValueError('아이디는 필수 항목입니다.')
        if not password:
            raise ValueError('비밀번호는 필수 항목입니다.')

        user_obj = self.model(
            username=username,
        )

        # Filled area from user
        user_obj.username = username
        user_obj.full_name = full_name
        user_obj.email = self.normalize_email(email)
        user_obj.organization = organization
        user_obj.phone = phone
        user_obj.set_password(password)

        # Invisible fields
        user_obj.is_superuser = admin
        user_obj.is_staff = staff
        user_obj.is_active = active

        user_obj.save(using=self._db)
        return user_obj

    def create_superuser(self, username, password=None, full_name=None, organization=None, email=None, phone=None):
        user = self.create_user(
            username=username,
            password=password,
            full_name=full_name,
            email=email,
            organization=organization,
            phone=phone,
            staff=True,
            admin=True,
        )
        user.save(using=self._db)
        return user


# Abstracted User fields with options
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        unique=True,
        error_messages={'unique': _('이미 존재하는 아이디 입니다.')},
    )
    full_name = models.CharField(
        _('first_name' + 'last_name'),
        max_length=30,
        null=True,
        blank=True,
        default='',
    )
    email = models.EmailField(
        _('email address'),
    )
    organization = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    phone = models.CharField(
        max_length=16,
        null=True,
        blank=True,
    )
    is_staff = models.BooleanField(
        _('is_staff'),
        default=False,
    )
    is_active = models.BooleanField(
        _('is_active'),
        default=True,
    )
    created_date = models.DateTimeField(
        _('date joined'),
        auto_now_add=True,
    )
    updated_date = models.DateTimeField(
        auto_now=True,
    )

    # User Management object
    objects = UserManager()
    # objects = BaseUserManager()

    # This field will be the 'username'
    USERNAME_FIELD = 'username'
    # USERNAME_FIELD = 'account'
    # Required for create user (without username, password)
    REQUIRED_FIELDS = ['full_name', 'email', 'organization', 'phone']

    class Meta:
        db_table = 'Users'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return self.username

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.username

    def _generate_jwt_token(self):
        """
        Generates a JSON Web Token that stores this user's ID and has an expiry
        date set to 60 days into the future.
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        return token.decode('utf-8')
