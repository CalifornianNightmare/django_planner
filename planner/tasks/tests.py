
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Task, TaskPermission

class TaskAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='password123', login='testuser_login')
        self.client.login(username='testuser', password='password123')

        self.task = Task.objects.create(
            title="Test Task",
            description="This is a test task",
            status="todo",
            creator=self.user
        )

        self.tasks_url = reverse('task-list')  # Маршрут на список задач
        self.task_detail_url = reverse('task-detail', args=[self.task.id])  # Маршрут на детальную задачу

    def test_create_task(self):
        data = {
            "title": "New Task",
            "description": "This is a new task",
            "status": "in_progress"
        }
        response = self.client.post(self.tasks_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(Task.objects.get(id=response.data['id']).title, "New Task")

    def test_get_tasks_list(self):
        response = self.client.get(self.tasks_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Проверка, что возвращается одна задача
        self.assertEqual(response.data[0]['title'], self.task.title)

    def test_get_task_detail(self):
        response = self.client.get(self.task_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.task.title)

    def test_update_task(self):
        data = {
            "title": "Updated Task",
            "description": "This task has been updated",
            "status": "done"
        }
        response = self.client.put(self.task_detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")
        self.assertEqual(self.task.status, "done")

    def test_delete_task(self):
        response = self.client.delete(self.task_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

class TaskPermissionAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser1', password='password123', login='testuser1_login')
        self.other_user = get_user_model().objects.create_user(username='testuser2', password='password123', login='testuser2_login')
        self.client.login(username='testuser1', password='password123')

        self.task = Task.objects.create(
            title="Test Task",
            description="This is a test task",
            status="todo",
            creator=self.user
        )

        self.permission_url = reverse('taskpermission-list')

    def test_create_permission(self):
        data = {
            "task": self.task.id,
            "user": self.other_user.id,
            "can_read": True,
            "can_update": False
        }
        response = self.client.post(self.permission_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TaskPermission.objects.count(), 1)

    def test_update_permission(self):
        permission = TaskPermission.objects.create(
            task=self.task,
            user=self.other_user,
            can_read=True,
            can_update=False
        )
        url = reverse('taskpermission-detail', args=[permission.id])
        data = {"can_update": True}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        permission.refresh_from_db()
        self.assertTrue(permission.can_update)

    def test_delete_permission(self):
        permission = TaskPermission.objects.create(
            task=self.task,
            user=self.other_user,
            can_read=True,
            can_update=False
        )
        url = reverse('taskpermission-detail', args=[permission.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TaskPermission.objects.count(), 0)
