# app/src/layout.py

import streamlit as st

from src.params import PATHS, GITHUB_URL, REPORT_URL_MAIL, ABOUT_TEXT


def setup_layout(page_title: str, page_icon: str):
    st.set_page_config(
        layout='wide',
        page_title=page_title,
        page_icon=page_icon,
        initial_sidebar_state='expanded',
        menu_items={
            'Get Help': GITHUB_URL,
            'Report a bug': REPORT_URL_MAIL,
            'About': ABOUT_TEXT,
        },
    )

    st.logo(
        image=PATHS['logo'],
        link=GITHUB_URL,
    )
    st.markdown("""
        <style>
            img.stLogo {display:block; height: 150px; margin: 0}
        </style>
    """, unsafe_allow_html=True)

def setup_pages():
    pages = {
        'Home': [
            st.Page(
                page=PATHS['pages']['home'],
                title='B2B Client Prospecting',
                icon='🚀',
            ),
        ],
        'Settings': [
            st.Page(
                page=PATHS['pages']['prompt_engineering'],
                title='Prompt Engineering',
                icon='📝',
            ),
        ],
    }

    pg = st.navigation(pages)
    pg.run()
