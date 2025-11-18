from rest_framework import serializers
from .models import Workflow, Task, Heartbeat

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
    

class WorkflowSeializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)
    
    
    class Meta:
        model = Workflow
        fields = '__all__'


class HeartbeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heartbeat
        fields = '__all__'