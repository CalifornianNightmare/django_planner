from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response

from .models import Task, TaskPermission
from .serializers import TaskSerializer, TaskPermissionSerializer
from django.core.exceptions import PermissionDenied

class TaskPermissionViewSet(viewsets.ModelViewSet):
    queryset = TaskPermission.objects.all()
    serializer_class = TaskPermissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Возвращает только те права доступа, которые связаны с задачами, созданными текущим пользователем
        return TaskPermission.objects.filter(task__creator=self.request.user)

    def perform_create(self, serializer):
        task_id = self.request.data.get('task')
        user_id = self.request.data.get('user')

        if not task_id or not user_id:
            raise serializers.ValidationError("Task and User must be provided.")

        try:
            task = Task.objects.get(id=task_id)
            user = get_user_model().objects.get(id=user_id)
        except Task.DoesNotExist:
            raise serializers.ValidationError("Task does not exist.")
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        if task.creator != self.request.user:
            raise PermissionDenied("You do not have permission to manage access for this task.")

        serializer.save(task=task, user=user)

    def perform_update(self, serializer):
        task_permission = self.get_object()
        if task_permission.task.creator != self.request.user:
            raise PermissionDenied("У вас нет прав на изменение доступа к этой задаче.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.task.creator != self.request.user:
            raise PermissionDenied("У вас нет прав на удаление доступа к этой задаче.")
        instance.delete()

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        # Фильтрация задач, доступных текущему пользователю
        return Task.objects.filter(creator=self.request.user) | Task.objects.filter(permissions__user=self.request.user, permissions__can_read=True)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        if task.creator != request.user:
            return Response({'detail': 'Нет прав на обновление этой задачи'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        if task.creator != request.user:
            return Response({'detail': 'Нет прав на удаление этой задачи'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(
            Q(creator=user) |
            Q(permissions__user=user, permissions__can_read=True)
        ).distinct()
