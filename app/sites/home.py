# app/pages/home.py

import streamlit as st

from streamlit_autorefresh import st_autorefresh

import html
import time

from client_prospecting import (
    get_gmail, get_unanswered_emails, get_email, get_thread_history, send_email,
    get_response, get_client, get_prompts
)

from src.layout import setup_layout

setup_layout(page_title='B2B Client Prospecting', page_icon='🚀')

def update_emails():
    with st.spinner('Updating Emails...', show_time=True):
        st.session_state.emails = get_unanswered_emails(st.session_state.gmail)
        st.session_state.emails_ids = [
            f"{e['sender']} - {e['subject']}" for e in st.session_state.emails
        ]
        if len(st.session_state.emails) == 0:
            st.write('No emails to answer.')
            st.session_state.selected_email = None
        time.sleep(3)

def get_email_body(email_id):
    email = st.session_state.emails[st.session_state.emails_ids.index(email_id)]
    return get_email(st.session_state.gmail, email['thread_id'], email['message_id'])

def generate_answer():
    email = get_email_body(st.session_state.selected_email)
    thread_history = get_thread_history(
        st.session_state.gmail,
        email['thread_id']
    )
    response = get_response(
        client=st.session_state.client,
        system=st.session_state.system_prompt,
        prompt=email['text'],
        history=thread_history,
        model='gpt-4o',
        temperature=0.4
    )
    st.session_state.generated_answer = response

def log_answer(email, subject):
    st.session_state.answered_log.append({
        'email': email,
        'subject': subject,
        'time': time.strftime('%Y-%m-%d %H:%M:%S')
    })

if 'client' not in st.session_state:
    st.session_state.client = get_client()
if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = get_prompts()
if 'template_system_prompt' not in st.session_state:
    st.session_state.template_system_prompt = get_prompts(template=True)
if 'gmail' not in st.session_state:
    with st.spinner('Getting Gmail credentials...', show_time=True):
        st.session_state.gmail = get_gmail()
if 'emails' not in st.session_state or 'emails_ids' not in st.session_state:
    update_emails()
if 'selected_email' not in st.session_state:
    st.session_state.selected_email = st.session_state.emails_ids[0]
if 'automatic_answer' not in st.session_state:
    st.session_state.automatic_answer = False
if 'generated_answer' not in st.session_state:
    st.session_state.generated_answer = None
if 'answered_log' not in st.session_state:
    st.session_state.answered_log = list()

cols = st.columns([0.4, 0.4, 0.2])

with cols[0]:
    if st.button('Update Emails'):
        update_emails()

    automatic_answer = st.checkbox('Automatic answer', value=st.session_state.automatic_answer)
    st.session_state.automatic_answer = automatic_answer

    update_id = st_autorefresh(interval=60000, key='auto_refresh')
    if 'last_update' in st.session_state:
        if st.session_state.last_update != update_id:
            update_emails()
    st.session_state.last_update = update_id

    if st.session_state.automatic_answer and st.session_state.emails:
        for email_summary in st.session_state.emails:
            with st.spinner(f"Answering: {email_summary['subject']}...", show_time=True):
                st.session_state.selected_email = (
                    f"{email_summary['sender']} - {email_summary['subject']}"
                )
                generate_answer()
                email = get_email_body(st.session_state.selected_email)
                html_body = get_response(
                    client=st.session_state.client,
                    system=st.session_state.template_system_prompt,
                    prompt=st.session_state.generated_answer,
                    model='gpt-4o',
                    temperature=0.1
                )
                send_email(
                    gmail=st.session_state.gmail,
                    text=html_body,
                    to=email['sender_email'],
                    subject='Re: '+email['subject'],
                    thread_id=email['thread_id'],
                    message_id_reply=email['message_id']
                )
                log_answer(email['sender_email'], email['subject'])
                st.success(f"Answered and sent: {email['subject']}")

    if automatic_answer:
        st.write('Client Prospecting is automatically answering all unanswered emails.')
    else:
        if len(st.session_state.emails) > 0:
            if st.session_state.selected_email is None:
                st.session_state.selected_email = st.session_state.emails_ids[0]
            emails_dropdown = st.selectbox(
                'Choose an email:',
                options=st.session_state.emails_ids,
                index=st.session_state.emails_ids.index(st.session_state.selected_email),
            )
            if st.session_state.selected_email != emails_dropdown:
                st.session_state.selected_email = emails_dropdown
                st.session_state.generated_answer = None
            st.write(
                'If you want to answer the selected email, click on generate '
                'answer and then send mail.'
            )
            if st.button('Generate Answer'):
                with st.spinner('Generating answer...', show_time=True):
                    generate_answer()
                    st.success('Answer generated.')
            if st.button('Send mail') and st.session_state.generated_answer:
                with st.spinner('Sending mail...', show_time=True):
                    email = get_email_body(st.session_state.selected_email)
                    html_body = get_response(
                        client=st.session_state.client,
                        system=st.session_state.template_system_prompt,
                        prompt=st.session_state.generated_answer,
                        model='gpt-4o',
                        temperature=0.1
                    )
                    send_email(
                        gmail=st.session_state.gmail,
                        text=html_body,
                        to=email['sender_email'],
                        subject='Re: '+email['subject'],
                        thread_id=email['thread_id'],
                        message_id_reply=email['message_id']
                    )
                    st.success('Email sent.')
                    log_answer(email['sender_email'], email['subject'])

if st.session_state.selected_email is not None and not st.session_state.automatic_answer:
    with cols[1]:
        email = get_email_body(
            st.session_state.selected_email
        )
        email_html = (
            '<div style="'
            'border-radius:10px; box-shadow:0 2px 5px rgba(0,0,0,0.2);'
            'padding:20px;background-color:#ffffff; font-family:Segoe UI,Tahoma,sans-serif;">'
            '<h3 style="margin-top:0;color:#1B69E4;"">'
            f'{email["subject"]}</h3>'
            '<p style="'
            'border-bottom:1px solid #eee; padding-bottom:10px;margin-bottom:10px; color:#555;">'
            f'<strong>From:</strong> {email["sender_email"]}</p>'
            f'<div style="color:#333;line-height:1.6; white-space:pre-wrap;">{email["text"]}</div>'
            '</div>'
        )
        st.markdown(email_html, unsafe_allow_html=True)
        if st.session_state.generated_answer:
            generated_html = (
                '<div style="'
                'border-radius:10px;box-shadow:0 2px 5px rgba(27,105,228,0.3);'
                'padding:20px;margin-top:20px;background-color:#E6F0FF;'
                'font-family:Segoe UI,Tahoma,sans-serif;">'
                '<h3 style="margin-top:0;color:#1B69E4;">Generated Answer</h3>'
                f'<div style="color:#333;line-height:1.6;white-space:pre-wrap;">'
                f'{html.escape(st.session_state.generated_answer).replace(chr(10), "<br>")}'
                '</div></div>'
            )
            st.markdown(generated_html, unsafe_allow_html=True)
else:
    st.session_state.generated_answer = None

with cols[2]:
    st.markdown('### 📜 Answered Emails')
    if st.session_state.answered_log:
        for entry in reversed(st.session_state.answered_log):
            st.markdown(
                f"- **{entry['time']}**<br>"
                f"📨 {entry['email']}<br>"
                f"✏️ {entry['subject']}",
                unsafe_allow_html=True
            )
    else:
        st.info('No emails answered yet.')
