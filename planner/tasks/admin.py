from django.contrib import admin
from .models import Task, TaskPermission, CustomUser

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'status', 'created_at', 'updated_at')
    search_fields = ('title', 'description')

@admin.register(TaskPermission)
class TaskPermissionAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'can_read', 'can_update')
    list_filter = ('can_read', 'can_update')
    
