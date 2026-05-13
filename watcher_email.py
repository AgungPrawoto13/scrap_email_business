import os
import time
import requests
from dotenv import load_dotenv
from imapclient import IMAPClient
import pyzmail

load_dotenv()

IMAP_SERVER = os.getenv('IMAP_SERVER')
IMAP_PORT = int(os.getenv('IMAP_PORT'))
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

seen_uids = set()

def send_telegram(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }

    requests.post(url, data=payload)


def check_email():
    global seen_uids

    with IMAPClient(IMAP_SERVER, port=IMAP_PORT, ssl=True) as server:
        server.login(EMAIL, PASSWORD)
        server.select_folder('INBOX')

        messages = server.search(['UNSEEN'])

        print(messages)
        # for uid in messages:
        #     if uid in seen_uids:
        #         continue

        #     raw_message = server.fetch([uid], ['BODY[]', 'FLAGS'])

        #     message = pyzmail.PyzMessage.factory(
        #         raw_message[uid][b'BODY[]']
        #     )

        #     subject = message.get_subject()

        #     from_email = message.get_addresses('from')

        #     body = ''

        #     if message.text_part:
        #         body = message.text_part.get_payload().decode(
        #             message.text_part.charset or 'utf-8'
        #         )

        #     text = f'''
        #         📩 EMAIL BARU

        #         From: {from_email}

        #         Subject: {subject}

        #         Body:
        #         {body[:1000]}
        #     '''

        #     send_telegram(text)

        #     seen_uids.add(uid)

        #     print(f'Email sent to Telegram: {subject}')


if __name__ == '__main__':
    while True:
        try:
            check_email()
        except Exception as e:
            print('ERROR:', e)

        time.sleep(15)