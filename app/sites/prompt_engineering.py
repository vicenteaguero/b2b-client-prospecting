# app/pages/prompt_engineering.py

import streamlit as st

import re

from client_prospecting import get_prompts

from src.layout import setup_layout

setup_layout(page_title='Prompt Engineering', page_icon='📝')

if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = get_prompts()
if 'template_system_prompt' not in st.session_state:
    st.session_state.template_system_prompt = get_prompts(template=True)

def cleaning_prompt(prompt):
    lines = prompt.strip().splitlines()
    cleaned_lines = [re.sub(r'\s+', ' ', line).strip() for line in lines]
    return '\n'.join([
        '\n'+line if line.startswith('#') else line for line in cleaned_lines if line
    ])

st.title('Prompt Engineering')

system_prompt_area = st.text_area(
    'System Prompt',
    cleaning_prompt(st.session_state.system_prompt),
    height=500
)
if st.button('Save System Prompt'):
    st.session_state.system_prompt = cleaning_prompt(system_prompt_area)

template_system_prompt_area = st.text_area(
    'Template System Prompt',
    cleaning_prompt(st.session_state.template_system_prompt),
    height=500
)
if st.button('Save Template System Prompt'):
    st.session_state.template_system_prompt = cleaning_prompt(template_system_prompt_area)
