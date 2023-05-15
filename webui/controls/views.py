from django.shortcuts import render

from time import sleep
import os
import sys

from django.contrib.auth.views import LoginView
from django.views.generic import View
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


from .forms import SystemConfigForm, UserLoginForm, DetailForm
from .models import SystemConfig, StartupConfig

# append root directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'engine')))
from startup import Initialization

runtime = None

if SystemConfig.objects.exists() and StartupConfig.objects.exists() and runtime is None:
        runtime = Initialization(system_config=SystemConfig.objects.first(), startup_config=StartupConfig.objects.first())


def backend_init():
    """Init backend"""
    global runtime
    if SystemConfig.objects.exists() and StartupConfig.objects.exists():
        if runtime is not None:
            runtime.destroy()
        runtime = Initialization(system_config=SystemConfig.objects.first(), startup_config=StartupConfig.objects.first())


class RedirectToLoginView(View):
    """Redirects to login page"""

    def get(self, request):
        return redirect("login")


class UserLoginView(LoginView):
    """Login view for the user"""

    authentication_form = UserLoginForm
    redirect_authenticated_user = True

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password")
        return super().form_invalid(form)


class DetailPostView(LoginRequiredMixin, View):
    def post(self, request):
        detail_form = DetailForm(request.POST)
        if detail_form.is_valid():
            startup_config = StartupConfig.objects.first()
            form_data = detail_form.cleaned_data
            startup_config.automation = form_data["automation"]
            startup_config.auxillary = form_data["auxillary"]
            startup_config.sunrise_offset = form_data["sunrise_offset"]
            startup_config.sunset_offset = form_data["sunset_offset"]
            startup_config.save()

            # update runtime data with new values
            if form_data["automation"]:
                if runtime.auto.sunrise_offset != int(form_data["sunrise_offset"]):
                    runtime.auto.set_sunrise_offset(int(form_data["sunrise_offset"]))
                if runtime.auto.sunset_offset != int(form_data["sunset_offset"]):
                    runtime.auto.set_sunset_offset(int(form_data["sunset_offset"]))
                if runtime.auto.is_running is False:
                    runtime.auto.start()
                else:
                    runtime.auto.refresh()
                sleep(1)  # give the scheduler time to update
            else:
                if runtime.auto.is_running is True:
                    runtime.auto.stop()

            if form_data["auxillary"]:
                if runtime.door.aux_is_running is False:
                    runtime.door.run_aux()
            else:
                if runtime.door.aux_is_running is True:
                    runtime.door.stop_aux()
            messages.add_message(request, messages.SUCCESS, "Saved")
            return redirect("dashboard-page")
        else:
            messages.add_message(request, messages.ERROR, "Problem Saving")
            return render(request, "controls/dashboard.html", {
                "detail_form": detail_form,
                "active_times": {'sunrise': runtime.auto.active_sunrise(), 'sunset': runtime.auto.active_sunset(), 'current': runtime.auto.active_current()},
            })
    

# do the same as above but with a view class
class DashboardView(LoginRequiredMixin, View):
    """View for the dashboard page"""
    def get(self, request):
        if not SystemConfig.objects.exists():  # if there is no system config force user to create one on the system config page
            return redirect("systemconfig-page")
        
        # check if automation or auxillary running states are different from the database
        startup_config = StartupConfig.objects.first()
        if startup_config.automation is True and runtime.auto.is_running is False:
            startup_config.automation = False
        if startup_config.auxillary is True and runtime.door.aux_is_running is False:
            startup_config.auxillary = False
        startup_config.save()

        return render(request, "controls/dashboard.html", {
            "detail_form": DetailForm(instance=StartupConfig.objects.first()),
            "active_times": {'sunrise': runtime.auto.active_sunrise(), 'sunset': runtime.auto.active_sunset(), 'current': runtime.auto.active_current()},
        })


class SystemConfigView(LoginRequiredMixin, View):
    """View for the system configuration page"""
    def get(self, request):
        if SystemConfig.objects.exists():
            return render(request, "controls/systemconfig.html", {
                "systemconfig_form": SystemConfigForm(instance=SystemConfig.objects.first())
                })
        else:  # if there is no system config force user to create one on the system config page
            messages.add_message(request, messages.INFO, "Save the system config to continue to the dashboard")
            return render(request, "controls/systemconfig.html", {
                "systemconfig_form": SystemConfigForm(),
                })

    def post(self, request):
        systemconfg_form = SystemConfigForm(request.POST)

        if systemconfg_form.is_valid():
            if not SystemConfig.objects.exists():
                SystemConfig.objects.create()
            config = SystemConfig.objects.first()
            form_data = systemconfg_form.cleaned_data

            config.board_mode = form_data["board_mode"]
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

            # if first time setup, redirect to dashboard
            if not StartupConfig.objects.exists():
                StartupConfig.objects.create()
                backend_init()
                return redirect("dashboard-page")

            backend_init()

            messages.add_message(request, messages.SUCCESS, "System config saved!")
            return redirect("systemconfig-page")

        messages.add_message(request, messages.ERROR, "There was an error, please try again")
        return render(request, "controls/systemconfig.html", {
            "systemconfig_form": systemconfg_form
        })
