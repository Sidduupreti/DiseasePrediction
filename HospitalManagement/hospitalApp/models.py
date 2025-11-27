from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.urls import reverse

# this one is for contact 
class contactEnquiry(models.Model):
    your_name =models.CharField(max_length=50)
    your_email =models.EmailField(unique=True)
    subject =models.CharField(max_length=50)
    messages =models.CharField(max_length=500)



# this one is for appointment 
class Appointment(models.Model):
    name =models.CharField(max_length=50)
    email =models.EmailField(unique=False)
    date =models.DateField(blank=True)
    time =models.TimeField(blank=True)
    messages =models.CharField(max_length=500, null=True)



# this one is for HeartDisease 

class HeartDisease(models.Model):
    age =models.IntegerField(null=True)
    sex =models.IntegerField(null=True)
    chestPain =models.IntegerField(null=True)
    restingBloodPressure =models.IntegerField(null=True)
    cholesterol =models.IntegerField(null=True)
    fastingBloodSugar =models.IntegerField(null=True)
    restingElectrocardiographic =models.IntegerField(null=True)    
    maximumHeartRate =models.IntegerField(null=True)
    ExerciseInducedAngina =models.IntegerField(null=True)
    STdepression =models.IntegerField(null=True)

class DiabetesSubmission(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    pregnancies = models.IntegerField(null=True, blank=True)
    glucose = models.FloatField(null=True, blank=True)
    bp = models.FloatField(null=True, blank=True)
    st = models.FloatField(null=True, blank=True)
    insulin = models.FloatField(null=True, blank=True)
    bmi = models.FloatField(null=True, blank=True)
    dp = models.FloatField(null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)

    need_appointment = models.BooleanField(default=False)
    appointment_date = models.DateField(null=True, blank=True)
    appointment_time = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"DiabetesSubmission({self.user or 'anon'} - {self.created_at})"
