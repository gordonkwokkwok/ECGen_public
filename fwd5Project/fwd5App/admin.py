from django.contrib import admin
from .models import userModel
from .models import Profile

# Register your models here.
admin.site.register(userModel)
admin.site.register(Profile)
