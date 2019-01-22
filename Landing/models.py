from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from Company.models import Company
from Users.models import User
from Files.models import Image


class Landing(models.Model):
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL)
    manager = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=50, blank=True, null=True)
    header_script = models.TextField(blank=True, null=True)
    body_script = models.TextField(blank=True, null=True)
    base_url = models.CharField(max_length=30)
    view = models.IntegerField(default=0)
    hit = models.IntegerField(default=0)
    is_hijack = models.BooleanField(default=False)
    hijack_url = models.CharField(max_length=300, blank=True, null=True)
    is_mobile = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'landing'

    def __str__(self):
        return self.name


class Layout(models.Model):
    landing = models.OneToOneField(Landing, on_delete=models.CASCADE)
    # order = models.CharField(max_length=3000, blank=True, null=True)
    is_banner = models.BooleanField(default=False)
    banner_url = models.CharField(max_length=1000, null=True, blank=True)
    banner_image = models.ForeignKey(Image, blank=True, null=True, on_delete=models.SET_NULL)
    inner_db = models.BooleanField(default=False)
    font = models.IntegerField(default=0)
    is_term = models.BooleanField(default=False)
    image_term = models.BooleanField(default=False)
    show_company = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'layout'

    def __str__(self):
        # return str(self.created_date) or ''
        if self.landing == None:
            return "ERROR-LANDING NAME IS NULL"
        return str(self.landing)


@receiver(post_save, sender=Landing)
def create_layout(sender, instance, created, **kwargs):
    if created:
        Layout.objects.create(landing=instance)


# @receiver(post_save, sender=Landing)
# def save_layout(sender, instance, **kwargs):
#     # sender = user model
#     # instance = account
#     # kwarg = signal created? t update? none using? default
#     print('sender is ', sender)
#     print('instance is ', instance)
#     instance.account.save()
