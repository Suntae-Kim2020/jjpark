# OpenAI API 설정
# Streamlit Cloud에서는 환경 변수로 설정
import os

# 환경 변수에서 API 키 가져오기 (Streamlit Cloud Secrets에서 설정)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')

# Streamlit Cloud Secrets에서 API 키 가져오기 (우선순위)
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        OPENAI_API_KEY = st.secrets['OPENAI_API_KEY']
except:
    pass

# 데이터베이스 설정
DB_FILE = "fund_returns.db"
TABLE_NAME = "fund_returns"

# OpenAI API 설정
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.3
