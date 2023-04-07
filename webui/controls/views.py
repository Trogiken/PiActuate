from django.shortcuts import render

from django.views.generic import View
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib import messages
# use messages to display errors

from .forms import SystemConfigForm
from .models import SystemConfig

# Create your views here.


class RedirectToControlsView(View):
    def get(self, request):
        return redirect("controls-page")


class ControlsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if not SystemConfig.objects.exists():  # first time login
                redirect("systemconfig-page")
            return render(request, "controls/controls.html")  # provide context when model is created
        else:
            return redirect("login")

    def post(self, request):
        # handle updated controls
        pass


class SystemConfigView(View):
    def get(self, request):
        if request.user.is_authenticated:
            if not SystemConfig.objects.exists():  # render form with existing data
                SystemConfig.objects.create()
            return render(request, "controls/systemconfig.html", {
                "systemconfig_form": SystemConfigForm(instance=SystemConfig.objects.first())
            })
        else:
            return redirect("login")

    def post(self, request):
        systemconfg_form = SystemConfigForm(request.POST)

        if systemconfg_form.is_valid():
            config = SystemConfig.objects.first()
            form_data = systemconfg_form.cleaned_data

            config.board_mode = config.board_mode
            config.relay1 = form_data["relay1"]
            config.relay2 = form_data["relay2"]
            config.switch1 = form_data["switch1"]
            config.switch2 = form_data["switch2"]
            config.switch3 = form_data["switch3"]
            config.switch4 = form_data["switch4"]
            config.switch5 = form_data["switch5"]
            config.off_state = form_data["off_state"]
            config.timezone = form_data["timezone"]
            config.longitude = form_data["longitude"]
            config.latitude = form_data["latitude"]
            config.travel_time = form_data["travel_time"]

            config.save()
            # TODO if first startup send to controls, if not send to same page
            return redirect("systemconfig-page")

        # TODO if the form is invalid, we want to show the form again with previous data
        return render(request, "controls/systemconfig.html", {
            "systemconfig_form": systemconfg_form
        })


# if first login display system config page
