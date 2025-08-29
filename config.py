# OpenAI API 설정
# Streamlit Cloud Secrets를 우선적으로 사용
import os

# toml 모듈이 없을 경우를 대비한 fallback
try:
    import toml
except ImportError:
    toml = None

# config.toml에서 설정 읽기 (로컬 개발용)
def load_config_from_toml():
    """config.toml 파일에서 설정을 읽어오는 함수"""
    if toml is None:
        return {}
    
    try:
        config_path = '.streamlit/config.toml'
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = toml.load(f)
                return config
    except Exception as e:
        print(f"Error loading config.toml: {e}")
    return {}

# config.toml에서 설정 로드 (로컬 개발용)
config_data = load_config_from_toml()

# Streamlit Cloud Secrets에서 설정 가져오기 (최우선순위)
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    st = None

try:
    if STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
        # Streamlit Cloud Secrets에서 API 키 가져오기
        if 'OPENAI_API_KEY' in st.secrets:
            OPENAI_API_KEY = st.secrets['OPENAI_API_KEY']
        else:
            # Secrets에 없으면 환경 변수에서 가져오기
            OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
        
        # Streamlit Cloud Secrets에서 패스워드 가져오기
        if 'OPENAI_API_USE_PW' in st.secrets:
            OPENAI_API_USE_PW = st.secrets['OPENAI_API_USE_PW']
        else:
            # Secrets에 없으면 config.toml에서 가져오기
            OPENAI_API_USE_PW = config_data.get('openai', {}).get('OPENAI_API_USE_PW', 'bslee73')
        
        # Streamlit Cloud Secrets에서 관리자 패스워드 가져오기
        if 'admin_pw' in st.secrets:
            ADMIN_PW = st.secrets['admin_pw']
        else:
            # Secrets에 없으면 환경 변수에서 가져오기
            ADMIN_PW = os.getenv('admin_pw', 'admin123')
    elif not STREAMLIT_AVAILABLE:
        # Streamlit이 없는 경우 (스크립트 실행 시)
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
        OPENAI_API_USE_PW = config_data.get('openai', {}).get('OPENAI_API_USE_PW', 'bslee73')
        ADMIN_PW = os.getenv('admin_pw', 'admin123')
    else:
        # Streamlit은 있지만 secrets가 없는 경우
        OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
        OPENAI_API_USE_PW = config_data.get('openai', {}).get('OPENAI_API_USE_PW', 'bslee73')
        ADMIN_PW = os.getenv('admin_pw', 'admin123')
        
except Exception as e:
    # Secrets 읽기 실패 시 fallback
    print(f"Error reading Streamlit secrets: {e}")
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')
    OPENAI_API_USE_PW = config_data.get('openai', {}).get('OPENAI_API_USE_PW', 'bslee73')
    ADMIN_PW = os.getenv('admin_pw', 'admin123')

# 로컬 개발 환경에서 config.toml 우선 사용 (Secrets가 없는 경우)
if OPENAI_API_KEY == 'your_openai_api_key_here' and 'openai' in config_data and 'OPENAI_API_KEY' in config_data['openai']:
    toml_key = config_data['openai']['OPENAI_API_KEY']
    if toml_key and toml_key != 'your_openai_api_key_here':
        OPENAI_API_KEY = toml_key

# 데이터베이스 설정
DB_FILE = "fund_returns.db"
TABLE_NAME = "fund_returns"

# OpenAI API 설정
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 1000
OPENAI_TEMPERATURE = 0.3
