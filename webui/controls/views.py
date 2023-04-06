from django.shortcuts import render

from django.views.generic import View
from django.shortcuts import redirect
from django.urls import reverse

from .forms import SystemConfigForm

# Create your views here.


class RedirectToControlsView(View):
    def get(self, request):
        return redirect("controls-page")


class ControlsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, "controls/controls.html")  # provide context when model is created
        else:
            return redirect("login")

    def post(self, request):
        # handle updated controls
        pass


class SystemConfigView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, "controls/systemconfig.html", {
                "systemconfig_form": SystemConfigForm()
            })
        else:
            return redirect("login")

    def post(self, request):
        systemconfg_form = SystemConfigForm(request.POST)
        TEMP = Post.objects.get(slug=slug)  # TODO save first startup?
        if systemconfg_form.is_valid():
            # we do the following instead of just saving because we excluded the post field from the form
            config = systemconfg_form.save(commit=False)  # creates a model instance but doesn't save it to the database
            config.first_login = TEMP  # TODO save first startup?
            config.save()
            # TODO if first startup send to controls, if not send to same page
            return reverse("systemconfig-page")

        # TODO if the form is invalid, we want to show the form again with previous data
        return render(request, "controls/systemconfig.html", {
            "systemconfig_form": systemconfg_form
        })


# if first login display system config page
