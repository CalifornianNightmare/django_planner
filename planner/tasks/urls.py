from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskPermissionViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet)
router.register(r'permissions', TaskPermissionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
