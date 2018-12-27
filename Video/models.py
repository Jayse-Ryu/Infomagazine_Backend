from django.db import models
from Landing.models import Layout


class Video(models.Model):
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE)
    type = models.IntegerField(default=0)
    url = models.CharField(max_length=500, blank=True, null=True)
    desc = models.CharField(max_length=100, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'video'

    def __str__(self):
        return self.url
