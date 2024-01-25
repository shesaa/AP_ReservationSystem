from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from portal_app.forms import *

context = {
    'page_title': 'File Management System',
}

# def signup(request):
#     print(request.method)
#     if request.method == 'POST':
#         form = UserRegistration(request.POST)
#         print(request.POST)
#         print(form.is_valid())
#         print(form.errors)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('home')
#     else:
#         form = UserRegistration()
#     return render(request, 'signup.html', {"form" : form})


from django.contrib.auth import login
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
import json

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

from portal_app.models import *


def login_user(request):
    if request.method == 'POST':
        # Get the username and password from the POST request
        username = request.POST['username']
        password = request.POST['password']
        form = UserLogin(request.POST)

        user = form.is_valid()

        # If we have a user, log them in and redirect to the desired page
        if user is not None and User.objects.filter(username=username, password=password).exists():
            user = User.objects.get(username=username)
            login(request, user)
            # Redirect to 'home' or some other page where you want users to go after login
            return redirect('home')

        # If credentials are not correct, return an error message
        else:
            messages.error(request, 'Username or password not correct')
            return render(request, 'login.html')

    else:
        # For a GET request, just render the template
        return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        form = UserRegistration(request.POST)
        print(form.errors)
        if form.is_valid():
            # This saves the User object and returns it
            user = form.save(commit=False)
            user.password = form.cleaned_data.get('password')
            user.save()
            return redirect('login')  # Redirect them to some success page after signup

        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = UserRegistration()  # A form bound to the POST data
        return render(request, 'signup.html', {'form': form})




from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def set_appointment(request):
    if request.method == 'POST':
        form = SetAppointment(request.POST)
        if form.is_valid():
            # Save the appointment, but commit=False so it won't be saved to the database yet
            appointment = form.save(commit=False)
            # Assign the currently logged-in doctor to the appointment
            user = request.user
            appointment.dr_id = User.objects.get(username= user.username)

            # Now you can save the appointment to the database
            appointment.save()
            # Redirect to a success page or another URL
            return redirect('home')
    else:
        form = SetAppointment()
    return render(request, 'set_appointment.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('login/')

def home(request):
    return render(request, 'home.html')
    # return redirect('signup')


def show_all_appointments(request):

    pass
