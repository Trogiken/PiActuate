import subprocess


class DaphneStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # check daphne only because thats the process we use to run the update script
        if request.method == 'POST' and not self.is_daphne_running():
            raise("Daphne service is not running, is a update in progress?")
        return self.get_response(request)
    
    def is_daphne_running(self):
        try:
            subprocess.run(['systemctl', 'is-active', '--quiet', 'daphne'], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
