import os
import re
import pyzmail
import pandas as pd
import time
import requests
from io import StringIO
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from imapclient import IMAPClient
from datetime import datetime, timedelta

load_dotenv()
seen_uids = set()

IMAP_SERVER = os.getenv('IMAP_SERVER')
IMAP_PORT = int(os.getenv('IMAP_PORT'))
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
ATTACHMENT_DIR = "attachments"
os.makedirs(ATTACHMENT_DIR, exist_ok=True)

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
            latest_uid = messages[-1]
            
            response = server.fetch(
                messages,
                ['INTERNALDATE'],
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

                    #to get file attachment from body email
                    for part in message.mailparts:

                        filename = part.filename
                        if filename:

                            print("ATTACHMENT FOUND:", filename)
                            filepath = os.path.join(
                                ATTACHMENT_DIR,
                                filename
                            )
                            payload = part.get_payload()
                            # with open(filepath, "wb") as f:
                            #     f.write(payload)

                            # print("SAVED:", filepath)

                    subject = message.get_subject()
                    from_email = message.get_addresses('from')
                    body = ''

                    #get convert body email to plain text and get table in body email
                    if message.text_part and message.html_part:
                        body = message.text_part.get_payload().decode(
                            message.text_part.charset or 'utf-8'
                        )
                        html_body = message.html_part.get_payload().decode(
                            message.html_part.charset or 'utf-8'
                        )

                    text = f'''
                        EMAIL BARU

                        From: {from_email}
                        Subject: {subject}
                        Body:
                        {body}
                    '''

                    send_telegram(text)
                    seen_uids.add(uid)

                    print(f'Email sent to Telegram: {subject}')
                    time.sleep(2)

            return text, html_body
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

def parsing_table(html_body):
    soup = BeautifulSoup(html_body, 'lxml')
    tables = soup.find_all('table')
    print("TOTAL TABLE:", len(tables))

    for idx, table in enumerate(tables):

        try:
            df_table_body = pd.read_html(
                StringIO(str(table))
            )[0]
            print(f"\nTABLE {idx}")
            print(df_table_body)
            df_table_body.to_excel(f"table_email{idx}.xlsx")

        except Exception as e:
            print("ERROR PARSING TABLE:", e)

# if __name__ == '__main__':
text, html_body = check_email()
#parsing_table(html_body)

#print("pesan email", text)
# with open("result_email.txt", "w") as f:
#     f.write(text)

# with open('result_email.txt', 'r') as file:
#     content = file.read()

# cleaned_body = clean_email_body(content)
# rows = extract_rows(cleaned_body)
# df = pd.DataFrame(rows)
# df.to_excel("result_scrap.xlsx")