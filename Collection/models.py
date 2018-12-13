from django.db import models
from Landing.models import Landing


class Collections(models.Model):
    landing_page = models.ForeignKey(Landing, on_delete=models.CASCADE)
    data = models.CharField(max_length=512, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Collections'

    def __str__(self):
        return self.data
