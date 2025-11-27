from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Create your forms here.

class signUpForm(UserCreationForm):
	email = forms.EmailField(required=True)

	class Meta:
		model = User
		fields = ("first_name","last_name", "email", "password")

	def save(self, commit=True):
		user = super(signUpForm, self).save(commit=False)
		user.email = self.cleaned_data['email']
		if commit:
			user.save()
		return user

class DiabetesForm(forms.Form):
    gender = forms.ChoiceField(choices=(('M','Male'),('F','Female')), required=False)
    pregnancies = forms.IntegerField(min_value=0, max_value=20, initial=0)
    glucose = forms.FloatField(min_value=0)
    bp = forms.FloatField(min_value=0)
    st = forms.FloatField(min_value=0)
    insulin = forms.FloatField(min_value=0)
    bmi = forms.FloatField(min_value=0)
    dp = forms.FloatField(min_value=0)
    age = forms.IntegerField(min_value=0, max_value=120)

    save_and_appointment = forms.BooleanField(required=False)
    appointment_date = forms.DateField(required=False)
    appointment_time = forms.TimeField(required=False)

class AccountForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)