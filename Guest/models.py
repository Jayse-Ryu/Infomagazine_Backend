from django.db import models
from Users.models import User
from Company.models import Company
from Landing.models import Landing


class GuestFilter(models.Model):
    guest = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'guest_filter'

    def __str__(self):
        return self.guest_id
