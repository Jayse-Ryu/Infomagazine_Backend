from django.db import models
from Landing.models import Landing
from Files.models import Image


class FormGroup(models.Model):
    landing = models.ForeignKey(Landing, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    back_color = models.CharField(max_length=7, default='', blank=True)
    text_color = models.CharField(max_length=7, default='', blank=True)
    fields = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'form_group'

    def __str__(self):
        return self.name


class Field(models.Model):
    form_group = models.ForeignKey(FormGroup, on_delete=models.CASCADE)
    type = models.IntegerField(default=0)
    name = models.CharField(max_length=10)
    holder = models.CharField(max_length=50, blank=True)
    value = models.CharField(max_length=50, blank=True, null=True)
    url = models.CharField(max_length=1000, blank=True, null=True)
    list = models.CharField(max_length=200, blank=True, null=True)
    width = models.IntegerField(default=12)
    back_color = models.CharField(max_length=7, default='', blank=True)
    text_color = models.CharField(max_length=7, default='', blank=True)
    image = models.ForeignKey(Image, blank=True, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'field'

    def __str__(self):
        return self.name
