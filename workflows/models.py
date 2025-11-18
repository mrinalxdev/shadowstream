from django.db import models

class Workflow(models.Model):
    name = models.DateTimeField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta :
        db_table = 'workflows'


class Task(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]


    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='tasks')
    task_id = models.CharField(max_length=100, unique=True)
    task_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payload = models.JSONField(null=True, blank=True)
    result = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    attempt = models.IntegerField(default=0)
    max_attempts = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'tasks'
        indexes = [
            models.Index(fields=['task_type', 'status']),
        ]

class Heartbeat(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='heartbeats')
    worker_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'heartbeats'