# client_prospecting/prospecting.py

from openai import OpenAI

from datetime import datetime
import os

from client_prospecting.params import TEMPLATE_PATH, BUSINESS_INFO_PATH
from client_prospecting.utils import load_env, extract_mail, extract_plain_text

def get_client():
    load_env()
    if os.getenv('OPENAI_APIKEY') is None:
        raise Exception('OPENAI_APIKEY is not set')
    return OpenAI(api_key=os.getenv('OPENAI_APIKEY'))

def get_response(
    client,
    system: str,
    prompt: str,
    history: list = None,
    model: str = 'gpt-4o',
    temperature: float = 0.4
) -> str:
    if '{business_info}' in system:
        with open(BUSINESS_INFO_PATH) as file:
            business_info = file.read()
        system = system.format(business_info=business_info)
    if '{template_html}' in system:
        with open(TEMPLATE_PATH) as file:
            template_html = file.read()
        system = system.format(template_html=template_html)

    full_prompt = prompt
    if history:
        formatted_history = format_thread_for_prompt(history)
        full_prompt = (
            f'Conversation history:\n\n{formatted_history}\n\n---\n\nLast message:\n{prompt}'
        )

    return client.chat.completions.create(
        model=model,
        messages=[
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': full_prompt}
        ],
        temperature=temperature
    ).choices[0].message.content.strip()

def get_prompts(template=False):
    if template:
        from client_prospecting.prompts import TEMPLATE_SYSTEM_PROMPT
        return TEMPLATE_SYSTEM_PROMPT
    else:
        from client_prospecting.prompts import SYSTEM_PROMPT
        return SYSTEM_PROMPT

def format_thread_for_prompt(history):
    formatted = []
    for msg in history:
        sender = msg['sender_name'] or msg['sender']
        date_str = msg['date'].strftime('%Y-%m-%d %H:%M')
        text = msg['text']
        formatted.append(f'[{date_str}] {sender}:\n{text}')
    return '\n\n---\n\n'.join(formatted)
