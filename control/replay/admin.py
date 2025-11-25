from django.contrib import admin

from .models import ReplayJob
# Register your models here.

@admin.register(ReplayJob)
class ReplayJobAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "end_time", "speed_factor", "status")
