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
    pregnancies = data.get('pregnancies', 0) or 0
    glucose = data.get('glucose', 0) or 0
    bp = data.get('bp', 0) or 0
    st = data.get('st', 0) or 0
    insulin = data.get('insulin', 0) or 0
    bmi = data.get('bmi', 0) or 0
    dp = data.get('dp', 0) or 0
    age = data.get('age', 0) or 0

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
    scaler = gb = rf = svm = gb_accuracy = rf_accuracy = svm_accuracy = None
    try:
        model_dict = joblib.load(MODEL_PATH)

        # Extract the models, scaler, and accuracies from the dictionary
        scaler = model_dict.get('scaler')
        gb = model_dict.get('gradient_boosting')
        rf = model_dict.get('random_forest')
        svm = model_dict.get('svm')

        gb_accuracy = model_dict.get('gb_accuracy')
        rf_accuracy = model_dict.get('rf_accuracy')
        svm_accuracy = model_dict.get('svm_accuracy')

        if not all([scaler, gb, rf, svm]):
            raise ValueError("One or more models are missing from the dictionary")
    except Exception as e:
        messages.error(request, f"Error loading model: {e}")
        return redirect('diabetes')

    # Prepare the input data
    X = np.array([[pregnancies, glucose, bp, st, insulin, bmi, dp, age]])
    X_scaled = scaler.transform(X)

    # Make predictions with all models
    prediction_gb = gb.predict(X_scaled)[0]
    prediction_rf = rf.predict(X_scaled)[0]
    prediction_svm = svm.predict(X_scaled)[0]

    # Interpret the results and include accuracy in the output
    results = {
        'Gradient Boosting': f'You have diabetes (Model Accuracy: {gb_accuracy * 100:.2f}%)' if prediction_gb == 1 else f'You do not have diabetes (Model Accuracy: {gb_accuracy * 100:.2f}%)',
        'Random Forest': f'You have diabetes (Model Accuracy: {rf_accuracy * 100:.2f}%)' if prediction_rf == 1 else f'You do not have diabetes (Model Accuracy: {rf_accuracy * 100:.2f}%)',
        'SVM': f'You have diabetes (Model Accuracy: {svm_accuracy * 100:.2f}%)' if prediction_svm == 1 else f'You do not have diabetes (Model Accuracy: {svm_accuracy * 100:.2f}%)'
    }

    # Combine the results into a formatted string with each prediction on a new line
    result_text = '\n'.join([f"{model_name}: {prediction}" for model_name, prediction in results.items()])

    # Save submission always
    try:
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
            need_appointment=bool(data.get('save_and_appointment')),
            appointment_date=data.get('appointment_date') if data.get('save_and_appointment') else None,
            appointment_time=data.get('appointment_time') if data.get('save_and_appointment') else None,
        )
        submission.save()
        messages.success(request, "Submission saved successfully.")
    except Exception as e:
        messages.error(request, f"Error saving submission: {e}")
        return redirect('diabetes')

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



