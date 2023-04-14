from django.urls import path, include

from . import views

urlpatterns = [
     path("",
         views.RedirectToLoginView.as_view(), name="redirect-to-login"),

     path("dashboard/",
         views.DashboardView.as_view(), name="dashboard-page"),
     path("system-config/",
         views.SystemConfigView.as_view(), name="systemconfig-page"),
     path("movement-request/", 
          views.MovementRequestView.as_view(), name="movement-request"),
     path('auth/',
         include('django.contrib.auth.urls')),
     path('auth/login',
          views.UserLoginView.as_view(), name='login'),
]