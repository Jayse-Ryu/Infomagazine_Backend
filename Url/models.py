# from django.db import models
# # from Landing.models import Landing
#
#
# class Url(models.Model):
#     # landing = models.ForeignKey(Landing, on_delete=models.CASCADE)
#     url = models.CharField(max_length=50)
#     desc = models.CharField(max_length=50, blank=True, null=True)
#     view = models.IntegerField(default=0)
#     hit = models.IntegerField(default=0)
#     created_date = models.DateTimeField(auto_now_add=True)
#     updated_date = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'url'
#
#     def __str__(self):
#         return self.url
