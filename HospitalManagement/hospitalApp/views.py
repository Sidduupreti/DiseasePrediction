from profile import Profile
from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
from django.shortcuts import  render, redirect
from .forms import signUpForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib import messages
from django.utils import timezone
from hospitalApp.models import contactEnquiry
from .models import Appointment
from .models import HeartDisease
import pandas as pd
# from sklearn.externals import joblib
import joblib
import os
import numpy as np
from django.conf import settings
from sklearn.metrics import accuracy_score  # Corrected import
from django.contrib.auth import authenticate, login, logout
from .models import DiabetesSubmission
from .forms import DiabetesForm, AccountForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

MODEL_PATH = os.path.join(settings.BASE_DIR, "diabetes_model.pkl")



# from .models import Patient

# Create your views here.
def home(request):
    return render(request,'home.html',{})


def diabetes(request):
    return render(request,'diabetes.html',{})


def diabetesprediction(request):
    if request.method != "POST":
        return redirect('diabetes')

    form = DiabetesForm(request.POST)
    account_form = AccountForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please correct the input fields.")
        return redirect('diabetes')

    data = form.cleaned_data
    pregnancies = data['pregnancies']
    glucose = data['glucose']
    bp = data['bp']
    st = data['st']
    insulin = data['insulin']
    bmi = data['bmi']
    dp = data['dp']
    age = data['age']

    # Handle account creation for anonymous users if saving appointment
    user = request.user if request.user.is_authenticated else None
    if data.get('save_and_appointment') and not user:
        if account_form.is_valid():
            email = account_form.cleaned_data['email']
            password = account_form.cleaned_data['password']
            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                # Check if password matches the existing user's password
                if existing_user.check_password(password):
                    user = existing_user
                    login(request, user)
                else:
                    messages.error(request, "Incorrect password for existing account. Please sign in with correct password.")
                    return redirect('diabetes')
            else:
                user = User.objects.create_user(username=email, email=email, password=password)
                login(request, user)
        else:
            messages.error(request, "Please provide valid email and password to save your submission and appointment.")
            return redirect('diabetes')

    # Load model file (see MODEL_PATH in this file)
    scaler = gb = rf = svm = None
    try:
        model_obj = joblib.load(MODEL_PATH)
        if isinstance(model_obj, dict):
            scaler = model_obj.get('scaler') or model_obj.get('standard_scaler')
            gb = model_obj.get('gb') or model_obj.get('gradient_boosting') or model_obj.get('model')
            rf = model_obj.get('rf')
            svm = model_obj.get('svm')
        else:
            # single model file
            gb = model_obj
    except Exception as e:
        messages.error(request, f"Error loading model: {e}")
        return redirect('diabetes')

    X = np.array([[pregnancies, glucose, bp, st, insulin, bmi, dp, age]])
    if scaler is not None:
        try:
            X = scaler.transform(X)
        except Exception:
            pass

    def readable(pred):
        return "Positive" if int(pred) == 1 else "Negative"

    results = []
    # helper to run model safely
    def run_model(name, model):
        if model is None:
            return
        try:
            pred = model.predict(X)[0]
            prob = None
            if hasattr(model, "predict_proba"):
                try:
                    prob = model.predict_proba(X)[0, 1]
                except Exception:
                    prob = None
            if prob is not None:
                results.append(f"{name}: {readable(pred)} (prob={prob:.3f})")
            else:
                results.append(f"{name}: {readable(pred)}")
        except Exception as e:
            results.append(f"{name}: error ({e})")

    run_model("GradientBoosting", gb)
    run_model("RandomForest", rf)
    run_model("SVM", svm)

    result_text = "\n".join(results) if results else "No predictions available."

    # Optionally save submission and appointment
    if data.get('save_and_appointment'):
        submission = DiabetesSubmission(
            user=user,
            pregnancies=pregnancies,
            glucose=glucose,
            bp=bp,
            st=st,
            insulin=insulin,
            bmi=bmi,
            dp=dp,
            age=age,
            need_appointment=True,
            appointment_date=data.get('appointment_date'),
            appointment_time=data.get('appointment_time'),
        )
        submission.save()

    return render(request, 'diabetesresult.html', {'result': result_text})


def contact(request):
    return render(request,'contact.html',{})


def services(request):
    return render(request,'services.html',{})

def doctors(request):
    return render(request,'doctors.html',{})


def about(request):
    return render(request,'about.html',{})

def signin(request):
    if request.method == "POST":
        form = AccountForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            # find user by email then authenticate by username
            user_qs = User.objects.filter(email=email).first()
            if user_qs:
                user = authenticate(request, username=user_qs.username, password=password)
                if user:
                    login(request, user)
                    return redirect("my_appointments")
            messages.error(request, "Invalid credentials")
    else:
        form = AccountForm()
    return render(request, "signin.html", {"form": form})

def signout(request):
    logout(request)
    return redirect("home")

@login_required
def my_appointments(request):
    # Filter DiabetesSubmission for appointments requested by the logged-in user
    qs = DiabetesSubmission.objects.filter(user=request.user, need_appointment=True).order_by("-appointment_date", "-appointment_time")
    return render(request, "my_appointments.html", {"appointments": qs})

@login_required
def appointment_detail(request, pk):
    appt = get_object_or_404(DiabetesSubmission, pk=pk, user=request.user, need_appointment=True)
    return render(request, "appointment_detail.html", {"appointment": appt})

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_appointments(request):
    # Show all appointments for all users
    qs = DiabetesSubmission.objects.filter(need_appointment=True).order_by("-appointment_date", "-appointment_time")
    return render(request, "admin_appointments.html", {"appointments": qs})



