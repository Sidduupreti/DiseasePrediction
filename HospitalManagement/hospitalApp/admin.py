from django.contrib import admin
# from .models import Patient
# from .models import Doctor
from .models import Appointment
from .models import contactEnquiry
from .models import HeartDisease

# Register your models here.
# admin.site.register(Patient)
# admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(contactEnquiry)
admin.site.register(HeartDisease)
