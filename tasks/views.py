from django.utils import timezone

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer


class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()

        if instance.status == Task.Status.COMPLETED:
            if instance.completed_at is None:
                instance.completed_at = timezone.now()
                instance.save(update_fields=["completed_at"])
        else:
            if instance.completed_at is not None:
                instance.completed_at = None
                instance.save(update_fields=["completed_at"])
