from rest_framework import serializers

from .models import Task, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]


class TaskSerializer(serializers.ModelSerializer):
    category_details = CategorySerializer(
        source="category",
        read_only=True
    )

    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "due_date",
            "completed_at",
            "priority",
            "status",
            "recurrence",
            "category",
            "category_details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "completed_at",
            "created_at",
            "updated_at",
        ]
    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError(
                "Task title cannot be empty."
            )
        return value.strip()

    def validate_due_date(self, value):
        if value is not None:
            from django.utils import timezone

            if value < timezone.now():
                raise serializers.ValidationError(
                    "Due date cannot be in the past."
                )
        return value

    def validate_category(self, category):
        request = self.context.get("request")

        if category and request and category.user != request.user:
            raise serializers.ValidationError(
                "You can only use your own categories."
            )

        return category
    