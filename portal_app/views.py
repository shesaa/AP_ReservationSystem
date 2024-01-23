from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash

from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from portal_app.forms import UserRegistration



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





def login_user(request):
    logout(request)
    resp = {"status": 'failed', 'msg': ''}

    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status'] = 'success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp), content_type='application/json')



def signup(request):
    if request.method == 'POST':
        form = UserRegistration(request.POST)
        if form.is_valid():
            # This saves the User object and returns it
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            # Ensure the user is authenticated before logging them in
            if user.is_authenticated:
                login(request, user)
                return HttpResponseRedirect('/success_url/')  # Redirect them to some success page after signup
            else:
                # Handle cases where the user couldn't be authenticated
                pass
        else:
            return render(request, 'signup.html', {'form': form})
    else:
        form = UserRegistration()  # A form bound to the POST data
        return render(request, 'signup.html', {'form': form})



# def signup(request):
#     user = request.user
#     if user.is_authenticated:
#         return redirect('home-page')
#     context['page_title'] = "Register User"
#     if request.method == 'POST':
#         data = request.POST
#         form = UserRegistration(data)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             pwd = form.cleaned_data.get('password1')
#             loginUser = authenticate(username=username, password=pwd)
#             login(request, loginUser)
#             return redirect('/')
#         else:
#             context['reg_form'] = form
#
#     return render(request, 'signup.html', context)