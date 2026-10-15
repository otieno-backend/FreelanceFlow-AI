from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegisterSerializer, LoginSerializer

from tasks.models import Task


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    'message': 'Account created successfully.',
                    'user': serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        return Response(
            {
                'message': 'Login successful.',
                'token': token.key,
                'username': user.username,
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()

        return Response(
            {'message': 'Logout successful.'},
            status=status.HTTP_200_OK,
        )



class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_tasks = Task.objects.filter(user=request.user)

        total_tasks = user_tasks.count()

        pending_tasks = user_tasks.filter(
            status=Task.Status.PENDING
        ).count()

        in_progress_tasks = user_tasks.filter(
            status=Task.Status.IN_PROGRESS
        ).count()

        completed_tasks = user_tasks.filter(
            status=Task.Status.COMPLETED
        ).count()

        cancelled_tasks = user_tasks.filter(
            status=Task.Status.CANCELLED
        ).count()

        overdue_tasks = user_tasks.filter(
            due_date__lt=timezone.now()
        ).exclude(
            status__in=[
                Task.Status.COMPLETED,
                Task.Status.CANCELLED,
            ]
        ).count()

        return Response(
            {
                "username": request.user.username,
                "email": request.user.email,
                "summary": {
                    "total_tasks": total_tasks,
                    "pending_tasks": pending_tasks,
                    "in_progress_tasks": in_progress_tasks,
                    "completed_tasks": completed_tasks,
                    "cancelled_tasks": cancelled_tasks,
                    "overdue_tasks": overdue_tasks,
                },
            },
            status=status.HTTP_200_OK,
        )
