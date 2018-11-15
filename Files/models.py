from django.db import models
from Landing.models import Landing


class Files(models.Model):
    landing_page = models.ForeignKey(Landing, on_delete=models.CASCADE)
    file = models.FileField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Files'

    def __str__(self):
        return self.file
