from .models import Client
from .models import Project
from django.contrib import admin

# Register your models here.


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """
    """


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    """
