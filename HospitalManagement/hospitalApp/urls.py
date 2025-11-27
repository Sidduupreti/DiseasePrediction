from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('home',views.home,name="home"),
    path('contact',views.contact,name="contact"),
    path('services',views.services,name="services"),
    path('doctors',views.doctors,name="Doctors"),
    path('about',views.about,name="About"),
    path('diabetes',views.diabetes,name="diabetes"),
    path('diabetesprediction',views.diabetesprediction,name="diabetesprediction"),
    path("signin/", views.signin, name="signin"),
    path("signout/", views.signout, name="signout"),
    path("my-appointments/", views.my_appointments, name="my_appointments"),
    path("appointment/<int:pk>/", views.appointment_detail, name="appointment_detail"),
    path("admin-appointments/", views.admin_appointments, name="admin_appointments"),
]
