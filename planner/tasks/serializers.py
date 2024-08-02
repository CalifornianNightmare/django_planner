from rest_framework import serializers
from .models import Task, TaskPermission

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'creator', 'created_at', 'updated_at']
        read_only_fields = ['creator', 'created_at', 'updated_at']

class TaskPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskPermission
        fields = ['id', 'task', 'user', 'can_read', 'can_update']
        read_only_fields = ['task', 'user']
