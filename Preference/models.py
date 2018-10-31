from django.db import models
from Landing.models import Landing
from Files.models import Files


class Term(models.Model):
    landing_page = models.ForeignKey(Landing, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.CharField(max_length=5000, blank=True, null=True)
    image = models.ForeignKey(Files, blank=True, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Term'


class Urls(models.Model):
    landing_page = models.ForeignKey(Landing, on_delete=models.CASCADE)
    url = models.CharField(max_length=50)
    views = models.IntegerField(default=0)
    description = models.CharField(max_length=50, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Urls'
