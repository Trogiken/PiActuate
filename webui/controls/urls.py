from django.urls import path

from . import views

urlpatterns = [
    path("", views.RedirectToControlsView.as_view(), name="redirect-to-controls-page"),
    path("controls/", views.ControlsView.as_view(), name="controls-page"),
    path("system-config/", views.SystemConfigView.as_view(), name="systemconfig-page"),
]