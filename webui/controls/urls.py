from django.urls import path, include

from . import views

urlpatterns = [
     path("",
         views.RedirectToLoginView.as_view(), name="redirect-to-login"),

     path("dashboard/",
         views.DashboardView.as_view(), name="dashboard-page"),
     path("system-config/",
         views.SystemConfigView.as_view(), name="systemconfig-page"),

    path("dashboard/door_up/",
         views.door_up, name="door_up-post"),
    path("dashboard/door_down/",
        views.door_down, name="door_down-post"),
    path("detail-post/",
         views.DetailPostView.as_view(), name="detail-post"),

     path('auth/',
         include('django.contrib.auth.urls')),
     path('auth/login',
          views.UserLoginView.as_view(), name='login'),
]