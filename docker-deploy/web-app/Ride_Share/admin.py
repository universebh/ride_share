from django.contrib import admin

from .models import *

admin.site.register(MyUser)
admin.site.register(Vehicle)
admin.site.register(Sharer)
admin.site.register(Ride)
admin.site.register(RegisteredSharer)
# Register your models here.
