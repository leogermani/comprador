from flask import request
from config import Config


class Testing:
    def get_user_and_message(self):
        if 'Client-Token' in request.headers and request.headers['Client-Token'] == Config.ZAPI_TOKEN:
            print('oi')
        payload = request.json
        # Process the payload here
        print("Received payload:", payload)
        return payload