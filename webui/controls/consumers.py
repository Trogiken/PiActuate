import requests
import json
from channels.generic.websocket import WebsocketConsumer
from .api_comms import ApiComms

api = ApiComms()


class DoorConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
    
    def disconnect(self, code):
        return super().disconnect(code)
    
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data.get('message') == 'get_status':
            self.send(text_data=json.dumps({
                "signal": "200",
                "command": data.get('message'),
                "message": api.get_door_status()
                })
            )
        elif data.get('message') == 'open':
            api.open_door()
            self.send(text_data=json.dumps({
                "signal": "200",
                "command": data.get('message'),
                "message": "Door is opening"
                })
            )
        elif data.get('message') == 'close':
            api.close_door()
            self.send(text_data=json.dumps({
                "signal": "200",
                "command": data.get('message'),
                "message": "Door is closing"
                })
            )
        else:
            self.send(text_data=json.dumps({
                "signal": "400",
                "command": data.get('message'),
                "message": "Invalid request"
                })
            )


class UpdateConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
    
    def disconnect(self, code):
        return super().disconnect(code)
    
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data.get('update'):
            api.update()
        else:
            self.send(text_data=json.dumps({
                "signal": "400",
                "command": data.get('message'),
                "message": "Invalid request"
                })
            )