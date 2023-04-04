from django.shortcuts import render
from django.views import View


# Create your views here.

class LoginView(View):
    def get(self, request):
        # if request.user.is_authenticated:
        #     return redirect("controls:controls")
        pass

    def post(self, request):
        pass