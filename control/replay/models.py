from django.db import models

# Create your models here.
class ReplayJob(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    speed_factor = models.FloatField(default=1.0)

    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="pending")


    def __str__(self):
        return f"job {self.id} : {self.speed_factor}x"