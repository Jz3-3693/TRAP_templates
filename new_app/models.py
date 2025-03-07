from django.db import models
# class trap(models.Model):
 
#  place = models.CharField(max_length=255)
#  weather =models.CharField(max_length=255) 
#  time = models.DateTimeField()
 
class contact(models.Model):
 name = models.CharField(max_length=255)
 email = models.CharField(max_length=255)
 message =models.CharField(max_length=255)
 # Create your models here.
 
class AccidentPrediction(models.Model):
     latitude=models.FloatField()
     longitude=models.FloatField()
     cluster=models.IntegerField()
     timestamp=models.DateTimeField(auto_now_add=True)
     def __str__(self):
            return f"Cluster {self.cluster} at ({self.longitude},{self.latitude})"
    
         
