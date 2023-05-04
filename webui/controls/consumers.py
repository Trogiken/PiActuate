import json

from channels.generic.websocket import WebsocketConsumer

class DashboardConsumer(WebsocketConsumer):
    def connect(self):
        print("Consumer connect")  # DEBUG
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        print("Consumer receive")  # DEBUG
        from controls.views import runtime
        print(f"Runtime: {runtime}")  # DEBUG
        self.send(text_data=json.dumps({
            "message": runtime.door.get_status()
            })
        )  # send door status