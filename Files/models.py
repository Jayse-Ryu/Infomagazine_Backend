from django.db import models
from Landing.models import Landing


class Image(models.Model):
    landing = models.ForeignKey(Landing, on_delete=models.CASCADE)
    image = models.FileField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image'

    def __str__(self):
        return self.image
