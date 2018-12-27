from django.db import models


class Image(models.Model):
    image = models.FileField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image'

    def __str__(self):
        return self.image
