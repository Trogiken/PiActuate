import os


class UpdateStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.main_dir = os.path.dirname(os.path.abspath(__file__))
        self.lock_file = os.path.join(self.main_dir, 'update.lock')

    def __call__(self, request):
        # check daphne only because thats the process we use to run the update script
        if request.method == 'POST' and os.path.exists(self.lock_file):
            raise Exception("Update in progress, please wait.")
        return self.get_response(request)
