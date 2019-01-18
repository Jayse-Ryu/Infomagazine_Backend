from django.db import models
from Users.models import User


class Organization(models.Model):
    manager = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    sub_name = models.CharField(max_length=100, blank=True, null=True)
    header = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    corp_num = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=16, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    desc = models.CharField(max_length=200, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organization'

    def __str__(self):
        return self.name
