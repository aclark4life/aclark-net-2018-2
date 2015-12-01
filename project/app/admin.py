from .models import Client
from django.contrib import admin

# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    """
    """


admin.site.register(Client, ClientAdmin)
