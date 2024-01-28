from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from portal_app.forms import *


def unread_notifications_count(request):
    if request.user.is_authenticated:
        unread_count = request.user.notification_set.filter(read=False).count()
    else:
        unread_count = 0
    return unread_count


context = {
    'page_title': '',
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

from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect


# Custom decorator to check user type
def user_type_required(user_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if getattr(request.user, 'user_type', None) != user_type:
                return HttpResponseForbidden("You do not have permission to view this page.")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


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


@user_type_required('C')
@login_required(login_url='/login/')
def set_appointment(request):
    if request.method == 'POST':
        form = SetAppointment(request.POST)
        if form.is_valid():
            # Save the appointment, but commit=False so it won't be saved to the database yet
            appointment = form.save(commit=False)
            # Assign the currently logged-in doctor to the appointment
            user = request.user
            appointment.dr_id = user

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


@login_required(login_url='/login/')
def home(request):
    context['unread_count'] = unread_notifications_count(request)
    return render(request, 'home.html', context)
    # return redirect('signup')


@user_type_required('P')
@login_required(login_url='/login/')
def appointments(request):
    appointments_ = Appointment.objects.filter(reservation_status="NR")
    print(appointments_)
    context['unread_count'] = unread_notifications_count(request)
    context['appointments'] = appointments_

    return render(request, 'appointments.html',context)


from django.shortcuts import redirect, get_object_or_404


@user_type_required('P')
@csrf_exempt
@login_required(login_url='/login/')
def cancel_appointment(request):
    data = json.loads(request.body)
    appointment_id = data['appointment_id']
    user = request.user

    appointment_ = Appointment.objects.get(appointment_id=appointment_id)
    appointment_.patient_reserved_id = None
    appointment_.reservation_status = 'NR'
    appointment_.save()

    dr_user = appointment_.dr_id

    notification = Notification(to_user=user, message="Appointment Canceled !")
    notification.save()

    notification_dr = Notification(to_user=dr_user,
                                   message=f"Appointment with id {appointment_.appointment_id} Canceled by User {user.id} !")
    notification_dr.save()

    return redirect('appointments')


@user_type_required('P')
@csrf_exempt
@login_required(login_url='/login/')
def reserve_appointment(request):
    data = json.loads(request.body)
    appointment_id = data['appointment_id']
    # appointment_id = request.appointment_id
    user = request.user
    print(user, "usereeeee iddddd")

    print(appointment_id, "hahahahahhhahhaahahah*****")

    appointment_ = Appointment.objects.get(appointment_id=appointment_id)
    appointment_.patient_reserved_id = user
    appointment_.reservation_status = 'R'
    appointment_.save()

    dr_user = appointment_.dr_id

    notification = Notification(to_user=user, message="Appointment RESERVED !")
    notification.save()

    notification_dr = Notification(to_user=dr_user,
                                   message=f"Appointment with id {appointment_.appointment_id} RESERVED by User {user.id} !")
    notification_dr.save()

    return redirect('appointments')


@user_type_required('P')
@login_required(login_url='/login/')
def my_appointments(request):
    user_id = request.user.id
    my_appointments_ = Appointment.objects.filter(patient_reserved_id=user_id)
    context['unread_count'] = unread_notifications_count(request)
    context['my_appointments'] = my_appointments_

    return render(request, 'my_appointments.html', context)


@login_required(login_url='/login/')
def update_profile(request):
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id=request.user.id)
    if not request.method == 'POST':
        form = UpdateProfile(user=user)
        context['form'] = form
    else:
        form = UpdateProfile(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile")
        else:
            context['form'] = form

    context['unread_count'] = unread_notifications_count(request)
    return render(request, 'update_profile.html', context)


@login_required(login_url='/login/')
def notification_center(request):
    user = request.user
    notifications = Notification.objects.filter(to_user=user).order_by('-date_time')
    for notification in notifications:
        notification.read = True
        notification.save()
    return render(request, 'notification_center.html', {'notifications': notifications})
