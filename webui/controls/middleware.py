from django.http import HttpResponseServerError
from django.shortcuts import render
from pathlib import Path
import os


class UpdateStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.main_dir = str(Path(__file__).resolve().parents[2])
        self.lock_file = os.path.join(self.main_dir, 'update.lock')

    def __call__(self, request):
        # check daphne only because thats the process we use to run the update script
        if request.method == 'POST' and os.path.exists(self.lock_file):
            context = {'update_message': 'Update in progress, check back later'}
            return HttpResponseServerError(render(request, '403.html', context))
        return self.get_response(request)
