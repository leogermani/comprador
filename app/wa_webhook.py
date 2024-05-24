import time
from wa_apis.testing import Testing
from wa_apis.zapi import Zapi
from assistant import Assistant
from app import app
from flask import abort

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        testing_instance = Testing()
    except:
        abort(403)
    user_and_message = testing_instance.get_user_and_message()
    assistant = Assistant( phone=user_and_message['phone'], message=user_and_message['message'] )
    return assistant.process()

@app.route('/zapi-message-received', methods=['PUT','POST'])
def handle_zapi_webhook():
    try:
        zapi_instance = Zapi()
    except:
        abort(403)
    user_and_message = zapi_instance.get_user_and_message()
    if user_and_message is None:
        abort(418)
    assistant = Assistant( phone=user_and_message['phone'], message=user_and_message['message'] )
    response = assistant.process()
    response_code = zapi_instance.reply(response)
    return '', response_code