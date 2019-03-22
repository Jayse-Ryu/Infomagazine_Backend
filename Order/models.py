from django.db import models
# from django.db.models.signals import post_save
# from django.dispatch import receiver

from Landing.models import Layout
# from Company.models import Company
# from Landing.models import Landing

from Files.models import Image
from Form.models import FormGroup
from Video.models import Video


class Order(models.Model):
    layout = models.ForeignKey(Layout, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, default='ORDER')
    position = models.TextField(null=True, blank=True)
    type = models.IntegerField(default=0)
    image = models.ForeignKey(Image, on_delete=models.SET_NULL, blank=True, null=True)
    form_group = models.ForeignKey(FormGroup, on_delete=models.SET_NULL, blank=True, null=True)
    video = models.ForeignKey(Video, on_delete=models.SET_NULL, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order'

    def __str__(self):
        return self.name


# @receiver(post_save, sender=Layout)
# def create_user_access(sender, instance, created, **kwargs):
#     if created:
#         Order.objects.create(layout=instance)
