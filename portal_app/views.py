from django.contrib.auth import logout

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

import json

from django.shortcuts import render
from django.contrib.auth import login
from django.contrib import messages

from portal_app.models import *

from functools import wraps
from django.http import HttpResponseForbidden


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
        # print(password, "passworde agha here")
        # print(User.objects.get(username=username).password)
        # print(User.objects.get(username=username).check_password(password))
        # If we have a user, log them in and redirect to the desired page
        if user is not None and User.objects.filter(username=username).exists() and User.objects.get(
                username=username).check_password(password):
            user = User.objects.get(username=username)
            login(request, user)
            if getattr(request.user, 'user_type', None) == "C":
                return redirect('main')
            return redirect('home')


        # If credentials are not correct, return an error message
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})

    else:
        # For a GET request, just render the template
        return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        form = UserRegistration(request.POST)
        # print(form.errors)
        if form.is_valid():
            # This saves the User object and returns it
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
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
            # Save the appointment, but commit=False, so it won't be saved to the database yet
            appointment = form.save(commit=False)
            # Assign the currently logged-in doctor to the appointment
            user = request.user
            appointment.dr = user

            # Now you can save the appointment to the database
            appointment.save()
            # Redirect to a success page or another URL
            return redirect('main')
    else:
        form = SetAppointment()
    return render(request, 'set_appointment.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('login/')


@user_type_required('P')
@login_required(login_url='/login/')
def home(request):
    context['unread_count'] = unread_notifications_count(request)
    if getattr(request.user, 'user_type', None) == "C":
        return render(request, 'main.html', context)
    return render(request, 'home.html', context)
    # return redirect('signup')


@user_type_required('C')
@login_required(login_url='/login/')
def main(request):
    context['unread_count'] = unread_notifications_count(request)

    return render(request, 'main.html', context)


from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


@user_type_required('P')
@login_required(login_url='/login/')
def appointments(request):
    appointments_ = Appointment.objects.filter(reservation_status="NR")

    page_size = request.GET.get('size', 5)

    if 'search' in request.GET:
        search_query = request.GET.get('search', '')

        appointments_by_dr = appointments_.filter(
            dr__username__regex=search_query
        )
        appointments_by_clinic = appointments_.filter(
            dr__username__regex=search_query
        )

        appointments_ = (appointments_by_dr | appointments_by_clinic).distinct()

    paginator = Paginator(appointments_, page_size)

    page_number = request.GET.get('page')
    try:
        appointments_ = paginator.page(page_number)
    except PageNotAnInteger:
        appointments_ = paginator.page(1)
    except EmptyPage:
        appointments_ = paginator.page(paginator.num_pages)

    context['unread_count'] = unread_notifications_count(request)
    context['appointments'] = appointments_

    return render(request, 'appointments.html', context)


from django.shortcuts import redirect


@csrf_exempt
@login_required(login_url='/login/')
def cancel_appointment(request):
    data = json.loads(request.body)
    appointment_id = data['appointment_id']
    user = request.user

    user_type = "C" if getattr(user, 'user_type', None) == "C" else "P"

    appointment_ = Appointment.objects.get(appointment_id=appointment_id)
    if user_type == "P":
        appointment_.patient_reserved = None
    appointment_.reservation_status = 'NR' if user_type == "P" else "C"
    appointment_.save()

    second_user = appointment_.dr if user_type == "P" else appointment_.patient_reserved

    notification = Notification(to_user=user, message=f"Appointment {appointment_id} Canceled !")
    notification.save()

    if user_type == "C" and appointment_.patient_reserved is None:
        return redirect('home' if user_type == "P" else "main")
    notification_second = Notification(to_user=second_user,
                                       message=f"Appointment with id {appointment_.appointment_id} Canceled by {user.username} !")
    notification_second.save()

    return redirect('home' if user_type == "P" else "main")


@user_type_required('P')
@csrf_exempt
@login_required(login_url='/login/')
def reserve_appointment(request):
    data = json.loads(request.body)
    appointment_id = data['appointment_id']
    # appointment_id = request.appointment_id
    user = request.user

    appointment_ = Appointment.objects.get(appointment_id=appointment_id)

    appointment_.patient_reserved = user
    appointment_.reservation_status = 'R'
    appointment_.save()

    dr_user = appointment_.dr

    notification = Notification(to_user=user, message=f"Appointment {appointment_id} RESERVED !")
    notification.save()

    notification_dr = Notification(to_user=dr_user,
                                   message=f"Appointment with id {appointment_id} RESERVED by User {user.username} !")
    notification_dr.save()

    return redirect('appointments')


@login_required(login_url='/login/')
def my_appointments(request):
    user = request.user
    user_type = "C" if getattr(user, 'user_type', None) == "C" else "P"

    if user_type == "P":
        my_appointments_ = Appointment.objects.filter(patient_reserved=user).order_by('-reservation_time')
    else:
        my_appointments_ = Appointment.objects.filter(dr_id=user).order_by('-reservation_time')

    hide_canceled = request.GET.get('hide_canceled') == 'on'

    if user_type == "C" and hide_canceled:
        my_appointments_ = my_appointments_.exclude(reservation_status='C')

    context = {
        'unread_count': unread_notifications_count(request),
        'my_appointments': my_appointments_,
        'user_type': user_type
    }
    return render(request, 'my_appointments.html', context)



@login_required(login_url='/login/')
def update_profile(request):
    context = {'page_title': 'Update Profile'}
    user = request.user
    # old_pass_user = user.password

    if request.method == 'POST':
        form = UpdateProfile(request.POST)
        # print(form)
        # print("formmmmmmmm")
        if form.is_valid():
            old_pass = form.cleaned_data.get('password')
            new_pass1 = form.cleaned_data.get('new_password1')
            new_pass2 = form.cleaned_data.get('new_password2')
            # print(old_pass, new_pass1, new_pass2, "sknvuoernwomfcec")
            # print(user.check_password(old_pass))
            if user.check_password(old_pass) and new_pass1 == new_pass2:
                user.set_password(new_pass1)
                user.save()
                messages.success(request, "Profile has been updated.")
                return redirect("home")
            else:
                messages.error(request, "Please correct the error below.")
    else:
        # form = UpdateProfile(user=user)
        form = UpdateProfile()

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


@csrf_exempt
@login_required(login_url='/login/')
def doctor_profile(request, doctor_id):
    if request.method == 'POST':
        return reserve_appointment(request)

    doctor = User.objects.get(id=doctor_id)
    available_appointments = Appointment.objects.filter(dr_id=doctor_id, reservation_status='NR')

    return render(request, 'doctor_profile.html', {
        'doctor': doctor,
        'appointments': available_appointments
    })
