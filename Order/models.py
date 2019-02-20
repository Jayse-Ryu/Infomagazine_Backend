from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from Landing.models import Layout
from Files.models import Image
from Company.models import Company
from Landing.models import Landing


class Order(models.Model):
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, default='ORDER')
    position = models.TextField(null=True, blank=True)
    type = models.IntegerField(default=0)
    # image = models.ForeignKey(Image, null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order'

    def __str__(self):
        return self.name


@receiver(post_save, sender=Layout)
def create_user_access(sender, instance, created, **kwargs):
    if created:
        Order.objects.create(layout=instance)
