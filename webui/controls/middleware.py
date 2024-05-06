from django.http import HttpResponseServerError
from django.urls import reverse_lazy
import subprocess


class DaphneStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = reverse_lazy('login')

    def __call__(self, request):
        if request.method == 'POST' and not self.is_daphne_running() and request.path == self.login_url:
            return HttpResponseServerError('Daphne service is not running. Please try again later.')
        return self.get_response(request)
    
    def is_daphne_running(self):
        try:
            subprocess.run(['systemctl', 'is-active', '--quiet', 'daphne'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
