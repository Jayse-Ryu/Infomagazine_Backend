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
    def create_user(self, account, password=None, full_name=None, organization=None,
                    email=None, phone=None, admin=False, staff=False, active=True):
        if not account:
            raise ValueError('아이디는 필수 항목입니다.')
        if not password:
            raise ValueError('비밀번호는 필수 항목입니다.')
        if not full_name:
            raise ValueError('사용자 이름은 필수 항목입니다.')
        if not email:
            raise ValueError('이메일은 필수 항목입니다.')
        user_obj = self.model(
            account=account,
            full_name=full_name,
            organization=organization,
            phone=phone,
        )

        # Filled area from user
        # user_obj.full_name = full_name
        # user_obj.organization = organization
        # user_obj.phone = phone
        user_obj.account = account
        user_obj.email = self.normalize_email(email)
        user_obj.set_password(password)

        # Invisible fields
        user_obj.is_superuser = admin
        user_obj.is_staff = staff
        user_obj.is_active = active

        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, account, password=None, full_name=None, organization=None, email=None, phone=None):
        user = self.create_user(
            account=account,
            password=password,
            full_name=full_name,
            email=email,
            organization=organization,
            phone=phone,
            staff=True,
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, account, password=None, full_name=None, organization=None, email=None, phone=None):
        user = self.create_user(
            account=account,
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
    account = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        unique=True,
        error_messages={'unique': _('이미 존재하는 아이디 입니다.')},
    )
    full_name = models.CharField(
        _('first_name' + 'last_name'),
        max_length=30,
        blank=True,
        default='',
    )
    email = models.EmailField(
        _('email address'),
    )
    organization = models.CharField(
        max_length=50,
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
    is_guest = models.BooleanField(
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
    USERNAME_FIELD = 'account'
    # USERNAME_FIELD = 'account'
    # Required for create user (without username, password)
    REQUIRED_FIELDS = ['full_name', 'email', 'organization', 'phone']

    class Meta:
        db_table = 'user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.account

    def get_full_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        if self.full_name:
            return self.full_name
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def token(self):
        """
        Allows us to get a user's token by calling `user.token` instead of
        `user.generate_jwt_token().

        The `@property` decorator above makes this possible. `token` is called
        a "dynamic property".
        """
        return self._generate_jwt_token()

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

    # Study property first
    # @property
    # def is_staff(self):
    #     return self.is_staff
    #
    # @property
    # def is_admin(self):
    #     return self.is_admin
    #
    # @property
    # def is_active(self):
    #     return self.is_active
    #
