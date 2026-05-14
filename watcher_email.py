import os
import re
import pandas as pd
import time
import requests
from dotenv import load_dotenv
from imapclient import IMAPClient
from datetime import datetime, timedelta
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

    #requests.post(url, data=payload)

def check_email():
    global seen_uids
    try:
        print("Connecting to IMAP server...")
        with IMAPClient(IMAP_SERVER, port=IMAP_PORT, ssl=True) as server:
            server.login(EMAIL, PASSWORD)
            print("Login success")

            server.select_folder('INBOX')
            messages = server.search(['SEEN'])

            response = server.fetch(
                messages,
                ['INTERNALDATE']
            )
            target_date = datetime(2026, 5, 13).date()
            
            for uid, data in response.items():
                if uid in seen_uids:
                    continue

                email_date = data[b'INTERNALDATE']

                if email_date.date() == target_date:
                    print(f"MATCH UID: {uid}")

                    raw_message = server.fetch([uid], ['BODY[]', 'FLAGS'])

                    message = pyzmail.PyzMessage.factory(
                        raw_message[uid][b'BODY[]']
                    )

                    subject = message.get_subject()

                    from_email = message.get_addresses('from')

                    body = ''

                    if message.text_part:
                        body = message.text_part.get_payload().decode(
                            message.text_part.charset or 'utf-8'
                        )

                    text = f'''
                        📩 EMAIL BARU

                        From: {from_email}

                        Subject: {subject}

                        Body:
                        {body}
                    '''

                    send_telegram(text)

                    seen_uids.add(uid)

                    print(f'Email sent to Telegram: {subject}')
                    time.sleep(2)

            return text
    except Exception as e:
        print("ERROR:")
        print(e)

def clean_email_body(body):

    # hilangkan multiple whitespace
    body = re.sub(r'\r', ' ', body)
    body = re.sub(r'\n+', '\n', body)
    body = re.sub(r'[ \t]+', ' ', body)

    return body.strip()

def extract_rows(body):

    # split berdasarkan nomor tabel
    pattern = r'\n(\d+)\s*\n'

    splits = re.split(pattern, body)

    rows = []

    # index 0 biasanya header
    for i in range(1, len(splits), 2):

        no = splits[i]
        content = splits[i + 1]
        print(content)
        # rows.append({
        #     "no": no,
        #     "raw_content": content
        # })

    return rows

# if __name__ == '__main__':
# text = check_email()
# print("pesan email", text)

with open('result_email.txt', 'r') as file:
    content = file.read()

cleaned_body = clean_email_body(content)
rows = extract_rows(cleaned_body)
df = pd.DataFrame(rows)
#df.to_excel("result_scrap.xlsx")