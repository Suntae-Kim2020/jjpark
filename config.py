# OpenAI API 설정
# Streamlit Cloud에서는 환경 변수로 설정
import os

# 환경 변수에서 API 키 가져오기 (Streamlit Cloud Secrets에서 설정)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')

# Streamlit Cloud Secrets에서 API 키 가져오기 (우선순위)
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        secrets_key = st.secrets['OPENAI_API_KEY']
        if secrets_key and secrets_key != 'your_openai_api_key_here':
            # API 키 유효성 검사
            if secrets_key.startswith('sk-') and len(secrets_key) > 20:
                OPENAI_API_KEY = secrets_key
            else:
                print(f"Warning: Invalid API key format detected: {secrets_key[:10]}...")
except Exception as e:
    # Secrets 읽기 실패 시 로그 출력 (개발 중에만)
    print(f"Error reading secrets: {e}")

# 데이터베이스 설정
DB_FILE = "fund_returns.db"
TABLE_NAME = "fund_returns"

# OpenAI API 설정
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.3
