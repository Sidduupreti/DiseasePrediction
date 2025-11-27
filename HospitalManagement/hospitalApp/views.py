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

MODEL_PATH = os.path.join(settings.BASE_DIR, "diabetes_model.pkl")



# from .models import Patient
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request,'home.html',{})


def diabetes(request):
    return render(request,'diabetes.html',{})


def diabetesprediction(request):
    try:
        # Load the model dictionary
        model_dict = joblib.load(MODEL_PATH)

        # Extract the models, scaler, and accuracies from the dictionary
        scaler = model_dict.get('scaler')
        gb_model = model_dict.get('gradient_boosting')
        rf_model = model_dict.get('random_forest')
        svm_model = model_dict.get('svm')

        gb_accuracy = model_dict.get('gb_accuracy')
        rf_accuracy = model_dict.get('rf_accuracy')
        svm_accuracy = model_dict.get('svm_accuracy')

        if not all([scaler, gb_model, rf_model, svm_model]):
            raise ValueError("One or more models are missing from the dictionary")

        # Extract features from the request
        pregnancies = float(request.POST.get('pregnancies', 0))
        glucose = float(request.POST.get('glucose', 0))
        bp = float(request.POST.get('bp', 0))
        st = float(request.POST.get('st', 0))
        insulin = float(request.POST.get('insulin', 0))
        bmi = float(request.POST.get('bmi', 0))
        dp = float(request.POST.get('dp', 0))
        age = float(request.POST.get('age', 0))


        # Prepare the input data
        X = np.array([[pregnancies, glucose, bp, st, insulin, bmi, dp, age]])
        X_scaled = scaler.transform(X)

        # Make predictions with all models
        prediction_gb = gb_model.predict(X_scaled)[0]
        prediction_rf = rf_model.predict(X_scaled)[0]
        prediction_svm = svm_model.predict(X_scaled)[0]

        # Interpret the results and include accuracy in the output
        results = {
            'Gradient Boosting': f'You have diabetes (Model Accuracy: {gb_accuracy * 100:.2f}%)' if prediction_gb == 1 else f'You do not have diabetes (Model Accuracy: {gb_accuracy * 100:.2f}%)',
            'Random Forest': f'You have diabetes (Model Accuracy: {rf_accuracy* 100:.2f}%)' if prediction_rf == 1 else f'You do not have diabetes (Model Accuracy: {rf_accuracy* 100:.2f}%)',
            'SVM': f'You have diabetes (Model Accuracy: {svm_accuracy* 100:.2f}%)' if prediction_svm == 1 else f'You do not have diabetes (Model Accuracy: {svm_accuracy* 100:.2f}%)'
        }

        # Combine the results into a formatted string with each prediction on a new line
        result_string = '\n'.join([f"{model_name}: {prediction}" for model_name, prediction in results.items()])

        # Return the result
        return render(request, 'diabetesresult.html', {'result': result_string})

    except Exception as e:
        print(f"Error during prediction: {e}")
        # Return an error message to the user
        return render(request, 'diabetesresult.html', {'result': 'An error occurred during prediction.'})





def contact(request):
    return render(request,'contact.html',{})


def services(request):
    return render(request,'services.html',{})

def doctors(request):
    return render(request,'doctors.html',{})


def about(request):
    return render(request,'about.html',{})



     