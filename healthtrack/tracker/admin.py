from django.contrib import admin
from .models import Measurement


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ('user', 'measured_at', 'systolic', 'diastolic', 'pulse', 'status_label')
    list_filter = ('user', 'measured_at')
    search_fields = ('user__username', 'note')
    date_hierarchy = 'measured_at'