"""
URL configuration for ReservationSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from portal_app import views
# from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('signup/', views.signup, name='signup'),
                  path('login/', views.login_user, name='login'),
                  path('set_appointment/', views.set_appointment, name='set_appointment'),
                  path('home/', views.home, name='home'),
                  path('logout', views.logout_user, name='logout'),
                  path('appointments', views.appointments, name='appointments'),
                  path('my_appointments', views.my_appointments, name='my_appointments'),
                  path('update_profile', views.update_profile, name='update_profile'),
                  path('reserve_appointment/', views.reserve_appointment, name='reserve_appointment'),
                  path('cancel_appointment/', views.cancel_appointment, name='cancel_appointment'),
                  path('notifications/', views.notification_center, name='notification_center'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
