from django.db import models
from Landing.models import Landing
from Form.models import FormGroup


class Collection(models.Model):
    landing = models.ForeignKey(Landing, on_delete=models.CASCADE)
    data = models.TextField(null=True, blank=True)
    url = models.CharField(max_length=200, blank=True)
    form_group = models.ForeignKey(FormGroup, blank=True, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'collection'

    def __str__(self):
        return self.data
