from django_celery_results.models import TaskResult
from idea_jet_async.serializers import TaskResultSerializer
from rest_framework import viewsets


class TaskResultViewset(viewsets.ModelViewSet):
    
    queryset = TaskResult.objects.all()
    serializer_class = TaskResultSerializer
    lookup_field =  "task_id"

