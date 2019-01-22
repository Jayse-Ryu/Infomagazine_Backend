from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from Users.models import User
from Company.models import Company
from Organization.models import Organization


class UserAccess(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access = models.IntegerField(default=1)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_access'

    def __str__(self):
        return str(self.user)


@receiver(post_save, sender=User)
def create_user_access(sender, instance, created, **kwargs):
    if created:
        UserAccess.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_access(sender, instance, **kwargs):
#     # sender = user model
#     # instance = account
#     # kwarg = signal created? t update? none using? default
#     print('sender is ', sender)
#     print('instance is ', instance)
#     instance.account.save()
