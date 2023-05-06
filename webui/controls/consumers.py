import json

from channels.generic.websocket import WebsocketConsumer


class DashboardConsumer(WebsocketConsumer):
    def connect(self):
        # check if user is logged in before connecting to websocket
        if self.scope['user'].is_authenticated:
            self.accept()
        else:
            self.close(code=1000, reason='User is not authenticated')

    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data.get('message') == 'get_status':
            from controls.views import runtime
            self.send(text_data=json.dumps({
                "signal": "200",
                "message": runtime.door.status
                })
            ) # send door status


class DoorMovementConsumer(LoginRequiredMixin, WebsocketConsumer):
    def connect(self):
        if self.scope['user'].is_authenticated:
            self.accept()
        else:
            self.close(code=1000, reason='User is not authenticated')
    
    def disconnect(self, close_code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        from controls.views import runtime
        data = json.loads(text_data)
        if data.get('message') == 'open':
            runtime.door.move(2)
            self.send(text_data=json.dumps({
                "signal": "200",
                "message": "Door is opening"
                })
            )
        elif data.get('message') == 'close':
            runtime.door.move(1)
            self.send(text_data=json.dumps({
                "signal": "200",
                "message": "Door is closing"
                })
            )
        else:
            self.send(text_data=json.dumps({
                "signal": "400",
                "message": "Invalid request"
                })
            )
