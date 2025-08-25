# OpenAI API 설정
# Streamlit Cloud에서는 환경 변수로 설정
import os
import toml

# config.toml에서 설정 읽기
def load_config_from_toml():
    """config.toml 파일에서 설정을 읽어오는 함수"""
    try:
        config_path = '.streamlit/config.toml'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)
                return config
    except Exception as e:
        print(f"Error loading config.toml: {e}")
    return {}

# config.toml에서 설정 로드
config_data = load_config_from_toml()

# 환경 변수에서 API 키 가져오기 (Streamlit Cloud Secrets에서 설정)
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')

# config.toml에서 API 키 가져오기 (우선순위)
if 'openai' in config_data and 'OPENAI_API_KEY' in config_data['openai']:
    toml_key = config_data['openai']['OPENAI_API_KEY']
    if toml_key and toml_key != 'your_openai_api_key_here':
        # API 키 유효성 검사 (sk- 또는 sk-proj- 모두 허용)
        if (toml_key.startswith('sk-') or toml_key.startswith('sk-proj-')) and len(toml_key) > 20:
            OPENAI_API_KEY = toml_key

# config.toml에서 패스워드 가져오기
OPENAI_API_USE_PW = config_data.get('openai', {}).get('OPENAI_API_USE_PW', 'bslee73')

# Streamlit Cloud Secrets에서 API 키 가져오기 (최우선순위)
try:
    import streamlit as st
    if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
        secrets_key = st.secrets['OPENAI_API_KEY']
        if secrets_key and secrets_key != 'your_openai_api_key_here':
            # API 키 유효성 검사 (sk- 또는 sk-proj- 모두 허용)
            if (secrets_key.startswith('sk-') or secrets_key.startswith('sk-proj-')) and len(secrets_key) > 20:
                OPENAI_API_KEY = secrets_key
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
