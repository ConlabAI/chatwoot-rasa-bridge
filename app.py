import os
import requests
import logging
from flask import Flask, request


rasa_url = os.environ.get('RASA_URL', 'http://localhost:5005')
chatwoot_url = os.environ.get('CHATWOOT_URL', 'http://localhost:3000')
chatwoot_bot_token = os.environ.get('CHATWOOT_API_TOKEN')

print(f'**** module name: {__name__}')


def send_to_bot(sender, message):
    data = {
        'sender': sender,
        'message': message
    }
    headers = {"Content-Type": "application/json",
               "Accept": "application/json"}

    r = requests.post(f'{rasa_url}/webhooks/rest/webhook',
                      json=data, headers=headers)
    application.logger.debug(f'-> To bot: {data}')
    application.logger.debug(f'<- Response from bot: {r.json()}')
    return r.json()[0]['text']


def send_to_chatwoot(account, conversation, message):
    data = {
        'content': message
    }
    url = f"{chatwoot_url}/api/v1/accounts/{account}/conversations/{conversation}/messages"
    headers = {"Content-Type": "application/json",
               "Accept": "application/json",
               "api_access_token": f"{chatwoot_bot_token}"}

    r = requests.post(url,
                      json=data, headers=headers)
    application.logger.debug(f'-> To chatwoot: {data}')
    application.logger.debug(f'<- Response from chatwoot: {r.json}')
    return r.json()


application = Flask(__name__)


@application.route('/rasa', methods=['POST'])
def rasa():
    data = request.get_json()
    application.logger.debug(f'<- Event from chatwoot: {data}')
    message_type = data['message_type']
    message = data['content']
    conversation = data['conversation']['id']
    contact = data['sender']['id']
    account = data['account']['id']

    if (message_type == "incoming"):
        bot_response = send_to_bot(contact, message)
        create_message = send_to_chatwoot(
            account, conversation, bot_response)
    return create_message


if __name__ == 'app':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    application.logger.handlers = gunicorn_logger.handlers
    application.logger.setLevel(gunicorn_logger.level)
    application.run(debug=1)
    # print(send_to_chatwoot(2,12,'3'))
