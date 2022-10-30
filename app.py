import os
import requests
import logging
import json
import time
from flask import Flask, request


rasa_url = os.environ.get('RASA_URL', 'http://localhost:5005')
chatwoot_url = os.environ.get('CHATWOOT_URL', 'http://localhost:3000')
chatwoot_api_key = os.environ.get('CHATWOOT_API_KEY')
message_delay = int(os.environ.get('CHATWOOT_MESSAGES_DELAY', 0))


def send_to_bot(sender, message, event):
    data = {
        'sender': sender,
        'message': message,
        'metadata': event
    }
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}

    r = requests.post(f'{rasa_url}/webhooks/rest/webhook',
                      json=data, headers=headers).json()
    application.logger.debug(f'-> To bot: {data}')
    application.logger.debug(f'<- Response from bot: {r}')
    return r


def send_to_chatwoot(account, conversation, message):
    data = {
        'content': message
    }
    url = f"{chatwoot_url}/api/v1/accounts/{account}/conversations/{conversation}/messages"
    headers = {"Content-Type": "application/json",
               "Accept": "application/json",
               "api_access_token": f"{chatwoot_api_key}"}

    r = requests.post(url,
                      json=data, headers=headers)
    application.logger.debug(f'-> To chatwoot: {json.dumps(data, indent=2)}')
    application.logger.debug(f'<- Response from chatwoot: {r.json()}')
    return r.json()


application = Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)


def valid_chatwoot_event(event):
    message_type = event['message_type']
    event_type = event['event']
    status = event['status']
    return (message_type == "incoming" and event_type == "message_created"
            and status == "pending")


@application.route('/rasa', methods=['POST'])
def rasa():
    event = request.get_json()
    message = event['content']
    conversation = event['conversation']['id']
    contact = event['sender']['id']
    account = event['account']['id']

    if valid_chatwoot_event(event):
        application.logger.debug(f'<- Event from chatwoot: {json.dumps(event, indent=2)}')
        bot_responses = send_to_bot(contact, message, event)
        if bot_responses:
            for response in bot_responses:
                create_message = send_to_chatwoot(account, conversation,
                                                  response['text'])
                if message_delay:
                    application.logger.debug(f'Sleeping {message_delay} seconds...')
                    time.sleep(message_delay)
            return create_message
    return {}


if __name__ == '__main__':
    application.run(debug=1)
    # print(send_to_chatwoot(2,12,'3'))
