# client_prospecting/email

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from datetime import datetime
import base64
import pickle
import os

from client_prospecting.params import SCOPES, CREDENTIALS_PATH, TOKEN_PATH, BANNER_EMAIL_PATH
from client_prospecting.utils import extract_plain_text, extract_mail, clean_subject

def get_gmail():
    credentials = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            credentials = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(credentials, token)
    return build('gmail', 'v1', credentials=credentials)

def get_unanswered_emails(gmail):
    threads = list()
    next_page = None
    while True:
        _threads = gmail.users().threads()
        response = _threads.list(userId='me', labelIds=['INBOX'], pageToken=next_page).execute()
        threads += response.get('threads', list())
        next_page = response.get('nextPageToken')
        if not next_page:
            break
    unanswered = list()
    for thread in threads:
        thread_detail = gmail.users().threads().get(userId='me', id=thread['id']).execute()
        messages = thread_detail.get('messages', list())
        last_msg = messages[-1]
        headers = {h['name']: h['value'] for h in last_msg['payload']['headers']}
        sender = headers.get('From', '')
        labels = last_msg.get('labelIds', list())
        if 'SENT' not in labels and 'me' not in sender:
            unanswered.append({
                'thread_id': thread['id'],
                'message_id': last_msg['id'],
                'subject': headers.get('Subject', '(no subject)'),
                'date': datetime.fromtimestamp(int(last_msg['internalDate'])/1000),
                'sender': sender
            })
    return unanswered

def get_email(gmail, thread_id, message_id):
    message = gmail.users().messages().get(userId='me', id=message_id, format='full').execute()
    payload = message['payload']
    text = extract_plain_text(payload)
    headers = {h['name']: h['value'] for h in payload['headers']}
    sender = headers.get('From', '')
    sender_name, sender_email = extract_mail(sender)
    subject = headers.get('Subject', '(no subject)')
    return dict(
        thread_id=thread_id,
        message_id=message_id,
        sender_name=sender_name,
        sender_email=sender_email,
        subject=subject,
        text=text
    )

def send_email( gmail, text: str, to: str, subject: str, thread_id: str, message_id_reply: str):
    msg = MIMEMultipart('related')
    msg['To'] = to
    msg['Subject'] = clean_subject(subject)
    msg['In-Reply-To'] = message_id_reply
    msg['References'] = message_id_reply
    alternative = MIMEMultipart('alternative')
    msg.attach(alternative)
    alternative.attach(MIMEText(
        'Este correo requiere un cliente compatible con HTML.',
        'plain'
    ))
    alternative.attach(MIMEText(text, 'html'))
    with open(BANNER_EMAIL_PATH, 'rb') as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', '<banner>')
        img.add_header(
            'Content-Disposition',
            'inline',
            filename=os.path.basename(BANNER_EMAIL_PATH)
        )
        msg.attach(img)
    raw_message = base64.urlsafe_b64encode(
        msg.as_bytes()
    ).decode()
    gmail.users().messages().send(
        userId='me',
        body={
            'raw': raw_message,
            'threadId': thread_id
        }
    ).execute()

def get_thread_history(gmail, thread_id):
    thread_detail = gmail.users().threads().get(
        userId='me', id=thread_id, format='full'
    ).execute()
    messages = thread_detail.get('messages', [])
    history = []
    for msg in messages:
        payload = msg['payload']
        headers = {h['name']: h['value'] for h in payload.get('headers', [])}
        sender = headers.get('From', 'Unknown sender')
        sender_name, sender_email = extract_mail(sender)
        text = extract_plain_text(payload)
        history.append({
            'sender': sender_email,
            'sender_name': sender_name,
            'text': text.strip(),
            'date': datetime.fromtimestamp(int(msg['internalDate'])/1000),
        })
    history.sort(key=lambda x: x['date'])
    return history
