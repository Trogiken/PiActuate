from django.shortcuts import render

from django.views.generic import View
from django.shortcuts import redirect

# Create your views here.


class RedirectToControlsView(View):
    def get(self, request):
        return redirect("controls-page")


class ControlsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return render(request, "controls/controls.html")
        else:
            return redirect("login")

    def post(self, request):
        # handle updated controls
        pass
