from django.db import models


class Authority(models.Model):
    name = models.CharField(max_length=15)
    description = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'Authority'


class Users(models.Model):
    account = models.CharField(max_length=20)
    name = models.CharField(max_length=30)
    organization = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    authority = models.ForeignKey(Authority, default=3, null=True, on_delete=models.SET_NULL)
    password = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Users'
