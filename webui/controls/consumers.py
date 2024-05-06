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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions_file_path = ""

    def connect(self):
        self.accept()
    
    def disconnect(self, code):
        return super().disconnect(code)
    
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data.get('message') == 'prepare_update':
            try:
                self.actions_file_path = api.prepare_update()
                self.send(text_data=json.dumps({
                    "signal": "200",
                    "command": data.get('message'),
                    "message": "Update Prepared"
                    })
                )
            except Exception as error:
                self.send(text_data=json.dumps({
                    "signal": "500",
                    "command": data.get('message'),
                    "message": str(error)
                    })
                )
        elif data.get('message') == 'update':
            # TODO: Handle errors!
            api.update(self.actions_file_path)
            # no point in sending a response here
        else:
            self.send(text_data=json.dumps({
                "signal": "400",
                "command": data.get('message'),
                "message": "Invalid request"
                })
            )
