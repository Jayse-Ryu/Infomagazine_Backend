from django.db import models
from Landing.models import Landing
from Files.models import Image


class Term(models.Model):
    landing = models.ForeignKey(Landing, on_delete=models.CASCADE)
    title = models.CharField(max_length=50, default='', blank=True)
    content = models.CharField(max_length=5000, blank=True, null=True)
    image = models.ForeignKey(Image, blank=True, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'term'

    def __str__(self):
        return str(self.title)
