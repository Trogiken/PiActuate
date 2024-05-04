from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views.generic import View
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SystemConfigForm, UserLoginForm, DetailForm
from .models import SystemConfig, StartupConfig

from time import sleep
from .api_comms import ApiComms

api = ApiComms()


def backend_init():
    """Init backend"""
    if SystemConfig.objects.exists() and StartupConfig.objects.exists():
        if api.runtime_alive():
            api.destroy()
        api.configure()


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
            startup_config.auxiliary = form_data["auxiliary"]
            startup_config.sunrise_offset = form_data["sunrise_offset"]
            startup_config.sunset_offset = form_data["sunset_offset"]
            startup_config.save()

            # update runtime data with new values
            # DEBUG: Return values
            auto = api.get_auto().json()["data"]
            if form_data["automation"]:
                if auto.get("sunrise_offset") != int(form_data["sunrise_offset"]):
                    api.alter_auto("sunrise_offset", int(form_data["sunrise_offset"]))
                if auto.get("sunset_offset") != int(form_data["sunset_offset"]):
                    api.alter_auto("sunset_offset", int(form_data["sunset_offset"]))
                if api.get_auto_status() is False:
                    api.alter_auto("start")
                else:
                    api.alter_auto("refresh")
                sleep(1)  # give the scheduler time to update
            else:
                if api.get_auto_status() is True:
                    api.alter_auto("stop")

            if form_data["auxiliary"]:
                if api.get_aux_status() is False:
                    api.alter_aux("start")
            else:
                if api.get_aux_status() is True:
                    api.alter_aux("stop")
            messages.add_message(request, messages.SUCCESS, "Saved")
            return redirect("dashboard-page")
        else:
            messages.add_message(request, messages.ERROR, "Problem Saving")
            return render(request, "controls/dashboard.html", {
                "detail_form": detail_form,
                "active_times": {'sunrise': auto.get("active_sunrise"), 'sunset': auto.get("active_sunset"), 'current': auto.get("active_current")},
            })
    

# do the same as above but with a view class
class DashboardView(LoginRequiredMixin, View):
    """View for the dashboard page"""
    def get(self, request):
        if not SystemConfig.objects.exists():  # if there is no system config force user to create one on the system config page
            return redirect("systemconfig-page")
        
        # check if automation or auxiliary running states are different from the database
        startup_config = StartupConfig.objects.first()
        if startup_config.automation is True and api.get_auto_status() is False:
            startup_config.automation = False
        if startup_config.auxiliary is True and api.get_aux_status() is False:
            startup_config.auxiliary = False
        startup_config.save()

        auto = api.get_auto().json()["data"]
        return render(request, "controls/dashboard.html", {
            "detail_form": DetailForm(instance=StartupConfig.objects.first()),
            "active_times": {'sunrise': auto.get("active_sunrise"), 'sunset': auto.get("active_sunset"), 'current': auto.get("active_current")},
            "has_update": api.has_update()
        })


class UpdateView(LoginRequiredMixin, View):
    """View for the update page"""
    def get(self, request):
        return render(request, "controls/update.html")


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
