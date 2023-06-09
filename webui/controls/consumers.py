import json
import os
import sys

from channels.generic.websocket import WebsocketConsumer




class DoorConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runtime = None

    def connect(self):
        if self.runtime is None:
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'engine')))
            from start import runtime  # import runtime in connect to avoid None import
            self.runtime = runtime
        self.accept()
    
    def disconnect(self, code):
        return super().disconnect(code)
    
    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data.get('message') == 'get_status':
            self.send(text_data=json.dumps({
                "signal": "200",
                "command": data.get('message'),
                "message": self.runtime.door.status
                })
            )
        elif data.get('message') == 'open':
            self.runtime.door.move(2)
            self.send(text_data=json.dumps({
                "signal": "200",
                "command": data.get('message'),
                "message": "Door is opening"
                })
            )
        elif data.get('message') == 'close':
            self.runtime.door.move(1)
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
