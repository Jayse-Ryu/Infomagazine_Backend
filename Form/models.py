# from django.db import models
# # from Landing.models import Layout
# from Files.models import Image
#
#
# class FormGroup(models.Model):
#     # layout = models.ForeignKey(Layout, null=True, on_delete=models.CASCADE)
#     name = models.CharField(max_length=50, default='', blank=True)
#     back_color = models.CharField(max_length=7, default='', blank=True)
#     text_color = models.CharField(max_length=7, default='', blank=True)
#     created_date = models.DateTimeField(auto_now_add=True)
#     updated_date = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'form_group'
#
#     def __str__(self):
#         return self.name
#
#
# class Field(models.Model):
#     form_group = models.ForeignKey(FormGroup, null=True, on_delete=models.CASCADE)
#     type = models.IntegerField(default=0)
#     name = models.CharField(max_length=10, default='', blank=True)
#     holder = models.CharField(max_length=50, blank=True)
#     value = models.CharField(max_length=50, blank=True, null=True)
#     url = models.CharField(max_length=1000, blank=True, null=True)
#     list = models.TextField(blank=True, null=True)
#     width = models.IntegerField(default=12)
#     back_color = models.CharField(max_length=7, default='', blank=True)
#     text_color = models.CharField(max_length=7, default='', blank=True)
#     image = models.ForeignKey(Image, blank=True, null=True, on_delete=models.SET_NULL)
#     created_date = models.DateTimeField(auto_now_add=True)
#     updated_date = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'field'
#
#     def __str__(self):
#         return self.name
