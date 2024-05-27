import requests
from flask import request
from config import Config

class Zapi:
    def __init__(self):
        if 'Z-Api-Token' not in request.headers or request.headers['Z-Api-Token'] != Config.ZAPI_TOKEN:
            raise PermissionError('Unauthorized request')


    def get_user_and_message(self):
        payload = request.json
        # if 'fromMe' in payload and payload.fromMe:
        #     return None

        # Process the payload here
        print("Received payload:", payload)
        return {
            'phone': payload['phone'],
            'message': payload['text']['message']
        }

    def reply(self, message):
        payload = request.json
        phone = payload['phone']
        token = Config.ZAPI_TOKEN
        zapi_instance_id = Config.ZAPI_INSTANCE

        url=f'https://api.z-api.io/instances/{zapi_instance_id}/token/{token}/send-text'

        payload = {
            'phone': phone,
            'message': message
        }

        headers = { 'Client-Token': Config.ZAPI_CLIENT_TOKEN }

        response = requests.post( url, json=payload, headers=headers)
        return response.status_code

    def send_quote(self, phone, message):
        token = Config.ZAPI_TOKEN_QUOTER
        zapi_instance_id = Config.ZAPI_INSTANCE_QUOTER

        url=f'https://api.z-api.io/instances/{zapi_instance_id}/token/{token}/send-text'

        payload = {
            'phone': phone,
            'message': message
        }

        headers = { 'Client-Token': Config.ZAPI_CLIENT_TOKEN_QUOTER }

        response = requests.post( url, json=payload, headers=headers)
        return response.status_code
