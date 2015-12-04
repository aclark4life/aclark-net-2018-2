from .models import Client
from .models import Project
from .models import Task
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


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    """
