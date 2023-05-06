import json

from channels.generic.websocket import WebsocketConsumer

class DashboardConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

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


class DoorMovementConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
    
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
