from django.http import HttpResponseServerError
import subprocess


class DaphneStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # check daphne only because thats the process we use to run the update script
        if request.method == 'POST' and not self.is_daphne_running():
            return HttpResponseServerError('Daphne service is not running. Please try again later.')
        return self.get_response(request)
    
    def is_daphne_running(self):
        try:
            subprocess.run(['systemctl', 'is-active', '--quiet', 'daphne'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
