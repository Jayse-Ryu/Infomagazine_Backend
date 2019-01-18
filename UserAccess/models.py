from django.db import models
from Users.models import User
from Company.models import Company
from Organization.models import Organization


class UserAccess(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access = models.IntegerField(null=True, blank=True)
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_access'

    def __str__(self):
        return str(self.user)
