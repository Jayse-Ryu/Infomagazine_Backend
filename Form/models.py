from django.db import models
from Landing.models import Landing


class Form(models.Model):
    landing_page = models.ForeignKey(Landing, null=True, on_delete=models.SET_NULL)
    section = models.IntegerField(default=0)
    title = models.CharField(max_length=40)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Form'

    def __str__(self):
        return self.title
