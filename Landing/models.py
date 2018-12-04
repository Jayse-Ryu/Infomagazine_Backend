from django.db import models
from Company.models import Company


class Landing(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    title = models.CharField(max_length=50, blank=True, null=True)
    status = models.IntegerField(default=1)
    header_script = models.CharField(max_length=3000, blank=True, null=True)
    body_script = models.CharField(max_length=3000, blank=True, null=True)
    image_switch = models.BooleanField(default=False)
    mobile_only = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    hits = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'Landing'

    def __str__(self):
        return self.name
