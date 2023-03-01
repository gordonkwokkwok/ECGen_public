from django.db import models
from django.contrib.auth.models import User, Group, Permission

# Create your models here.
class userModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission)
    
    # Other fields for your model
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=50, blank=True, null=True)
    serviceExpireDate = models.DateField(null=True, blank=True)
    freeTrial = models.BooleanField(default=True)
    
    def __str__(self):
        return str(self.user)
    
class Profile(models.Model):
    name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    job_description = models.TextField()

    def __str__(self):
        return self.name