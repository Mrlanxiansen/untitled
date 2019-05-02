from django.db import models

# Create your models here.
class person(models.Model):

    user = models.CharField(max_length=128,unique=True,primary_key=True)
    passwd = models.CharField(max_length=128)
    username = models.CharField(max_length=128)
    user_email = models.EmailField
    isDelete = models.BooleanField(default=True)