import streamlit as st
import pandas as pd
import traceback
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import os
import requests
import json
import base64
from io import BytesIO
from config import *

# 한글 폰트 지원을 위한 CSS 스타일 추가
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

/* 전체 앱에 한글 폰트 적용 */
.stApp {
    font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
}

/* 모든 Streamlit 컴포넌트에 한글 폰트 적용 */
.stMarkdown, .stText, .stButton, .stSelectbox, .stMultiselect, 
.stDateInput, .stSlider, .stCheckbox, .stMetric, .stDataFrame,
.stNumberInput, .stTextArea, .stFileUploader, .stProgress,
.stExpander, .stTabs, .stSidebar, .stMain {
    font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
}

/* 제목과 헤더에 한글 폰트 적용 */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
}

/* 테이블에 한글 폰트 적용 */
table, th, td {
    font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
}

/* 버튼과 입력 필드에 한글 폰트 적용 */
button, input, select, textarea {
    font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
}

/* 사이드바에 한글 폰트 적용 */
.sidebar .sidebar-content {
    font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
}

/* 메인 컨텐츠에 한글 폰트 적용 */
.main .block-container {
    font-family: 'Noto Sans KR', 'Malgun Gothic', 'AppleGothic', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# matplotlib 한글 폰트 설정 (Streamlit Cloud 호환)
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import seaborn as sns

# Streamlit Cloud 환경에서 한글 폰트 설정
def setup_korean_font():
    """Streamlit Cloud 환경에서 한글 폰트를 설정하는 함수"""
    try:
        # 1. GitHub fonts 디렉토리의 NanumGothic.ttf 우선 사용
        github_font_path = 'fonts/NanumGothic.ttf'
        if os.path.exists(github_font_path):
            # 폰트 파일을 matplotlib에 등록
            fm.fontManager.addfont(github_font_path)
            font_prop = fm.FontProperties(fname=github_font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            plt.rcParams['font.size'] = 10
            plt.rcParams['axes.unicode_minus'] = False
            st.success("✅ NanumGothic 폰트를 사용합니다.")
            return font_prop
        
        # 2. 시스템에 설치된 한글 폰트 찾기
        korean_fonts = ['NanumGothic', 'Malgun Gothic', 'AppleGothic', 'Noto Sans CJK KR', 'Source Han Sans KR', 'Noto Sans KR']
        for font_name in korean_fonts:
            try:
                font_prop = fm.FontProperties(family=font_name)
                if font_prop.get_name() != 'DejaVu Sans':  # 기본 폰트가 아닌 경우
                    plt.rcParams['font.family'] = font_name
                    plt.rcParams['font.size'] = 10
                    plt.rcParams['axes.unicode_minus'] = False
                    st.info(f"ℹ️ {font_name} 폰트를 사용합니다.")
                    return font_prop
            except:
                continue
        
        # 3. 웹 폰트 사용 (Streamlit Cloud에서 안정적)
        plt.rcParams['font.family'] = ['Noto Sans KR', 'DejaVu Sans', 'Arial Unicode MS', 'Liberation Sans', 'sans-serif']
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.unicode_minus'] = False
        st.info("ℹ️ 웹 폰트를 사용합니다.")
        return None
        
    except Exception as e:
        st.warning(f"⚠️ 폰트 설정 중 오류: {e}")
        # 기본 설정 사용
        plt.rcParams['font.family'] = ['Noto Sans KR', 'DejaVu Sans', 'Arial Unicode MS', 'Liberation Sans', 'sans-serif']
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.unicode_minus'] = False
        return None

# 한글 폰트 설정 실행
korean_font = setup_korean_font()

# 시각화용 폰트 설정 함수
def get_plot_font():
    """시각화에서 사용할 폰트를 반환하는 함수"""
    return korean_font

# OpenAI API 설정은 config.py에서 관리
# API 키 상태 확인 및 안내
if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here' or 'sk-proj-' in OPENAI_API_KEY:
    st.sidebar.warning("⚠️ OpenAI API 키가 설정되지 않았거나 유효하지 않습니다.\n\nAI 분석 기능을 사용하려면 `config.py`에서 유효한 API 키를 설정하세요.")

def analyze_with_openai(image_base64, table_data=None, analysis_type="시계열 수익률"):
    """OpenAI API를 사용하여 이미지와 표를 분석하는 함수"""
    try:
        # API 키 유효성 검사
        if not OPENAI_API_KEY or OPENAI_API_KEY == 'your_openai_api_key_here' or 'sk-proj-' in OPENAI_API_KEY:
            return "⚠️ **AI 분석 기능이 비활성화되었습니다.**\n\nAPI 키가 설정되지 않았거나 유효하지 않습니다. AI 분석을 사용하려면:\n\n1. [OpenAI Platform](https://platform.openai.com/account/api-keys)에서 새로운 API 키를 생성하세요\n2. `config.py` 파일에서 `OPENAI_API_KEY`를 업데이트하세요\n3. 애플리케이션을 재시작하세요"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }
        
        # 메시지 구성
        messages = [
            {
                "role": "system",
                "content": f"당신은 금융 데이터 분석 전문가입니다. {analysis_type} 차트와 표를 분석하여 한국어로 명확하고 전문적인 해석을 제공해주세요. 주요 인사이트, 트렌드, 패턴을 중심으로 분석해주세요."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"다음 {analysis_type} 차트와 표를 분석해주세요. 주요 인사이트, 트렌드, 패턴을 한국어로 설명해주세요."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
        
        # 표 데이터가 있으면 추가
        if table_data is not None:
            messages[1]["content"].append({
                "type": "text",
                "text": f"\n\n표 데이터:\n{table_data}"
            })
        
        payload = {
            "model": OPENAI_MODEL,
            "messages": messages,
            "max_tokens": OPENAI_MAX_TOKENS,
            "temperature": OPENAI_TEMPERATURE
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "🔐 **API 키 인증 오류**\n\nAPI 키가 유효하지 않습니다. 다음을 확인해주세요:\n\n1. API 키가 올바르게 설정되었는지 확인\n2. API 키가 만료되지 않았는지 확인\n3. [OpenAI Platform](https://platform.openai.com/account/api-keys)에서 새로운 키 생성"
        else:
            return f"API 호출 오류: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"분석 중 오류 발생: {str(e)}"

def save_plot_as_base64(fig):
    """matplotlib 그래프를 base64로 인코딩하는 함수"""
    try:
        # 그래프를 바이트로 저장
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        
        # base64로 인코딩
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        buffer.close()
        
        return image_base64
    except Exception as e:
        st.error(f"이미지 변환 오류: {e}")
        return None

# SQLite 데이터베이스 설정은 config.py에서 관리

# 데이터베이스 초기화 함수
def init_database():
    """SQLite 데이터베이스와 테이블을 초기화하는 함수"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 테이블 생성
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asof_date TEXT,
            manager TEXT,
            product_name TEXT,
            r_1m REAL,
            r_3m REAL,
            r_6m REAL,
            r_1y REAL,
            r_2y REAL,
            r_3y REAL,
            since_inception REAL,
            total_amount REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()
        st.success("✅ SQLite 데이터베이스 초기화 완료")
    except Exception as e:
        st.error(f"데이터베이스 초기화 오류: {e}")

# 데이터베이스 연결 함수
def get_db_connection():
    """SQLite 데이터베이스 연결을 반환하는 함수"""
    return sqlite3.connect(DB_FILE)

# SQLite 쿼리 실행 함수 (pandas 경고 해결)
def execute_sql_query(query, params=None):
    """SQLite 쿼리를 실행하고 DataFrame을 반환하는 함수"""
    conn = get_db_connection()
    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

# 데이터베이스 초기화 (강화된 보호 로직)
if not os.path.exists(DB_FILE):
    st.info("🆕 새로운 SQLite 데이터베이스를 생성합니다...")
    init_database()
else:
    # DB 파일이 존재하면 테이블 존재 여부만 확인
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 테이블 존재 여부 확인
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{TABLE_NAME}'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # 기존 데이터 개수 확인
            cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
            data_count = cursor.fetchone()[0]
            conn.close()
            
            if data_count > 0:
                st.success(f"✅ 기존 SQLite 데이터베이스 연결 완료 (총 {data_count:,}개 레코드)")
            else:
                st.info("✅ 기존 SQLite 데이터베이스 연결 완료 (데이터 없음)")
        else:
            conn.close()
            st.info("📋 테이블이 없어서 새로 생성합니다...")
            init_database()
            
    except Exception as e:
        st.error(f"데이터베이스 확인 중 오류: {e}")
        st.warning("⚠️ 오류로 인해 데이터베이스를 재생성합니다...")
        init_database()

# 사이드바 메뉴
st.sidebar.title("📊 Fund Returns 시스템 (SQLite)")

# 데이터 저장 섹션
st.sidebar.subheader("💾 데이터 저장")
if st.sidebar.button("📤 데이터 업로드", use_container_width=True):
    st.session_state.menu = "📤 데이터 업로드"

# 데이터 초기화 섹션
st.sidebar.subheader("🗑️ 데이터 관리")
if st.sidebar.button("🗑️ 데이터 초기화", use_container_width=True, type="secondary"):
    st.session_state.menu = "🗑️ 데이터 초기화"

# 데이터 분석 섹션
st.sidebar.subheader("📊 데이터 분석")
col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("📈 수익률 분석", use_container_width=True):
        st.session_state.menu = "📈 수익률 분석"
    
    if st.button("🏢 운용사별 분석", use_container_width=True):
        st.session_state.menu = "🏢 운용사별 분석"
    
    if st.button("📈 시계열 수익률", use_container_width=True):
        st.session_state.menu = "📈 시계열 수익률"

with col2:
    if st.button("📊 상품별 분석", use_container_width=True):
        st.session_state.menu = "📊 상품별 분석"
    
    if st.button("📅 기간별 분석", use_container_width=True):
        st.session_state.menu = "📅 기간별 분석"

# 기본 메뉴 설정
if 'menu' not in st.session_state:
    st.session_state.menu = "📤 데이터 업로드"

menu = st.session_state.menu

if menu == "📤 데이터 업로드":
    st.title("📊 Fund Returns 업로드 시스템 (SQLite)")
    
    # 날짜 선택
    asof_date = st.date_input("업로드 기준일 (asof_date)을 선택하세요:")
    
    # 파일 업로드
    uploaded_file = st.file_uploader("엑셀 파일 업로드", type=["xlsx"])

    if uploaded_file:
        try:
            # 엑셀 로드
            df = pd.read_excel(uploaded_file, sheet_name=0)
            
            st.subheader("데이터 미리보기")
            st.dataframe(df.head())
            
            # 엑셀 컬럼 확인
            st.info(f"엑셀 컬럼: {list(df.columns)}")
            
        except Exception as e:
            st.error(f"엑셀 파일 로드 오류: {e}")
            st.stop()

        # DB 저장 버튼
        if st.button("데이터 저장하기"):
            # 진행 상황 표시
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # 1단계: 데이터 전처리
                status_text.text("1단계: 데이터 전처리 중...")
                progress_bar.progress(10)
                
                # None/NaN 안전 변환 함수
                def safe_convert(value):
                    if pd.isna(value) or value is None:
                        return None
                    return str(value).strip() if isinstance(value, str) else value
                
                # 날짜 변환
                asof_date_str = str(asof_date) if asof_date else None
                
                # 2단계: 데이터 변환
                status_text.text("2단계: 데이터 변환 중...")
                progress_bar.progress(30)
                
                records = []
                for idx, row in df.iterrows():
                    try:
                        record = {
                            "asof_date": asof_date_str,
                            "manager": safe_convert(row.get("운용사")),
                            "product_name": safe_convert(row.get("상품명")),
                            "r_1m": safe_convert(row.get("1M")),
                            "r_3m": safe_convert(row.get("3M")),
                            "r_6m": safe_convert(row.get("6M")),
                            "r_1y": safe_convert(row.get("1Y")),
                            "r_2y": safe_convert(row.get("2Y")),
                            "r_3y": safe_convert(row.get("3Y")),
                            "since_inception": safe_convert(row.get("설정일이후")),
                            "total_amount": safe_convert(row.get("총액"))
                        }
                        records.append(record)
                    except Exception as row_error:
                        st.error(f"행 {idx} 처리 오류: {row_error}")
                        continue
                
                if not records:
                    st.error("변환된 데이터가 없습니다.")
                    st.stop()
                
                st.info(f"변환 완료: {len(records)}개 레코드")
                
                # 3단계: SQLite DB 연결
                status_text.text("3단계: SQLite DB 연결 중...")
                progress_bar.progress(50)
                
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    st.success("✅ SQLite DB 연결 성공!")
                    
                    # 4단계: 데이터 저장
                    status_text.text("4단계: 데이터 저장 중...")
                    progress_bar.progress(70)
                    
                    # INSERT 쿼리
                    insert_sql = f"""
                        INSERT INTO {TABLE_NAME} (
                            asof_date, manager, product_name,
                            r_1m, r_3m, r_6m, r_1y, r_2y, r_3y,
                            since_inception, total_amount
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    
                    # 레코드를 튜플로 변환
                    values_list = []
                    for record in records:
                        values = (
                            record["asof_date"],
                            record["manager"],
                            record["product_name"],
                            record["r_1m"],
                            record["r_3m"],
                            record["r_6m"],
                            record["r_1y"],
                            record["r_2y"],
                            record["r_3y"],
                            record["since_inception"],
                            record["total_amount"]
                        )
                        values_list.append(values)
                    
                    # 배치 실행
                    cursor.executemany(insert_sql, values_list)
                    conn.commit()
                    
                    status_text.text("5단계: 완료!")
                    progress_bar.progress(100)
                    
                    st.success(f"✅ 데이터 저장 완료! (처리 건수: {cursor.rowcount})")
                    
                    # 저장 확인
                    cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE asof_date = ?", (asof_date_str,))
                    count = cursor.fetchone()[0]
                    st.info(f"현재 기준일({asof_date_str})의 총 레코드 수: {count}")
                    
                except Exception as save_error:
                    st.error(f"데이터 저장 오류: {save_error}")
                    if conn:
                        conn.rollback()
                    st.code(traceback.format_exc())
                
            except Exception as e:
                st.error(f"예상치 못한 오류: {e}")
                st.code(traceback.format_exc())
            
            finally:
                # 연결 정리
                try:
                    if cursor:
                        cursor.close()
                    if conn:
                        conn.close()
                    st.info("SQLite DB 연결 종료 완료")
                except:
                    pass
                
                # 진행 상황 초기화
                progress_bar.empty()
                status_text.empty()

elif menu == "📈 수익률 분석":
    st.title("📈 수익률 분석 (SQLite)")
    
    # 분석 옵션 설정
    st.subheader("🔧 분석 옵션 설정")
    
    # 날짜 선택 (session_state로 상태 유지)
    if 'start_date' not in st.session_state:
        st.session_state.start_date = pd.Timestamp.now() - pd.Timedelta(days=365)
    if 'end_date' not in st.session_state:
        st.session_state.end_date = pd.Timestamp.now()
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("시작일 선택", value=st.session_state.start_date, key="start_date_input")
        st.session_state.start_date = start_date
    with col2:
        end_date = st.date_input("종료일 선택", value=st.session_state.end_date, key="end_date_input")
        st.session_state.end_date = end_date
    
    # 분석 기간 선택 (session_state로 상태 유지)
    if 'analysis_periods' not in st.session_state:
        st.session_state.analysis_periods = ["1Y", "3Y"]
    
    analysis_periods = st.multiselect(
        "분석할 수익률 기간 선택",
        ["1M", "3M", "6M", "1Y", "2Y", "3Y", "설정일이후"],
        default=st.session_state.analysis_periods,
        key="analysis_periods_select"
    )
    st.session_state.analysis_periods = analysis_periods
    
    # 시각화 옵션 (session_state로 상태 유지)
    st.subheader("📊 시각화 옵션")
    
    if 'show_histogram' not in st.session_state:
        st.session_state.show_histogram = True
    if 'show_boxplot' not in st.session_state:
        st.session_state.show_boxplot = True
    if 'show_statistics' not in st.session_state:
        st.session_state.show_statistics = True
    
    show_histogram = st.checkbox("히스토그램 표시", value=st.session_state.show_histogram, key="show_histogram_check")
    st.session_state.show_histogram = show_histogram
    
    show_boxplot = st.checkbox("박스플롯 표시", value=st.session_state.show_boxplot, key="show_boxplot_check")
    st.session_state.show_boxplot = show_boxplot
    
    show_statistics = st.checkbox("통계 테이블 표시", value=st.session_state.show_statistics, key="show_statistics_check")
    st.session_state.show_statistics = show_statistics
    
    if st.button("📈 수익률 분석 실행", type="primary"):
        try:
            # SQLite DB에서 데이터 조회
            query = f"""
                SELECT asof_date, manager, product_name, 
                       r_1m, r_3m, r_6m, r_1y, r_2y, r_3y, since_inception, total_amount
                FROM {TABLE_NAME}
                WHERE asof_date BETWEEN ? AND ?
                ORDER BY asof_date DESC
            """
            
            df_analysis = execute_sql_query(query, params=[start_date, end_date])
            
            if not df_analysis.empty:
                # 분석 결과를 session_state에 저장
                st.session_state.df_analysis = df_analysis
                st.session_state.analysis_completed = True
                st.session_state.analysis_periods = analysis_periods
                st.session_state.show_histogram = show_histogram
                st.session_state.show_boxplot = show_boxplot
                st.session_state.show_statistics = show_statistics
                
                st.success(f"✅ 분석 데이터 로드 완료: {len(df_analysis)}개 레코드")
                
                # 컬럼 매핑
                period_mapping = {
                    "1M": "r_1m",
                    "3M": "r_3m", 
                    "6M": "r_6m",
                    "1Y": "r_1y",
                    "2Y": "r_2y",
                    "3Y": "r_3y",
                    "설정일이후": "since_inception"
                }
                
                # 선택된 기간의 컬럼만 필터링
                selected_cols = [period_mapping[period] for period in analysis_periods if period in period_mapping]
                
                if not selected_cols:
                    st.warning("분석할 수익률 기간을 선택해주세요.")
                    st.stop()
                
                # 통계 테이블
                if show_statistics:
                    st.subheader("📊 수익률 통계")
                    stats_df = df_analysis[selected_cols].describe()
                    st.dataframe(stats_df, use_container_width=True)
                
                # 수익률 분포 히스토그램
                if show_histogram:
                    st.subheader("📈 수익률 분포 히스토그램")
                    
                    # 히스토그램 분석 기간 선택 (session_state로 상태 유지)
                    if 'histogram_period' not in st.session_state:
                        st.session_state.histogram_period = analysis_periods[0] if analysis_periods else "1Y"
                    
                    selected_period = st.selectbox("히스토그램 분석 기간 선택", analysis_periods, key="histogram_period_select_1")
                    st.session_state.histogram_period = selected_period
                    col_name = period_mapping[selected_period]
                    
                    fig, ax = plt.subplots(figsize=(10, 6))
                    font_prop = get_plot_font()
                    ax.hist(df_analysis[col_name].dropna(), bins=30, alpha=0.7, edgecolor='black', color='skyblue')
                    if font_prop:
                        ax.set_xlabel(f'{selected_period} 수익률 (%)', fontsize=12, fontproperties=font_prop)
                        ax.set_ylabel('빈도', fontsize=12, fontproperties=font_prop)
                        ax.set_title(f'{selected_period} 수익률 분포', fontsize=14, fontweight='bold', fontproperties=font_prop)
                    else:
                        ax.set_xlabel(f'{selected_period} 수익률 (%)', fontsize=12)
                        ax.set_ylabel('빈도', fontsize=12)
                        ax.set_title(f'{selected_period} 수익률 분포', fontsize=14, fontweight='bold')
                    ax.grid(True, alpha=0.3)
                    plt.tight_layout()
                    st.pyplot(fig)
                
                # 박스플롯
                if show_boxplot:
                    st.subheader("📦 수익률 박스플롯")
                    fig2, ax2 = plt.subplots(figsize=(12, 6))
                    font_prop = get_plot_font()
                    df_analysis[selected_cols].boxplot(ax=ax2)
                    if font_prop:
                        ax2.set_ylabel('수익률 (%)', fontsize=12, fontproperties=font_prop)
                        ax2.set_title('기간별 수익률 분포', fontsize=14, fontweight='bold', fontproperties=font_prop)
                    else:
                        ax2.set_ylabel('수익률 (%)', fontsize=12)
                        ax2.set_title('기간별 수익률 분포', fontsize=14, fontweight='bold')
                    ax2.tick_params(axis='x', rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig2)
                
                # 추가 분석: 상위/하위 수익률 상품
                st.subheader("🏆 수익률 순위")
                
                # 순위 분석 기간 선택 (session_state로 상태 유지)
                if 'rank_period' not in st.session_state:
                    st.session_state.rank_period = analysis_periods[0] if analysis_periods else "1Y"
                
                rank_period = st.selectbox("순위 분석 기간 선택", analysis_periods, key="rank_period_select_1")
                st.session_state.rank_period = rank_period
                rank_col = period_mapping[rank_period]
                
                st.write("**상위 10개 상품**")
                top_products = df_analysis.nlargest(10, rank_col)[['manager', 'product_name', rank_col]]
                st.dataframe(top_products, use_container_width=True)
                
                st.write("**하위 10개 상품**")
                bottom_products = df_analysis.nsmallest(10, rank_col)[['manager', 'product_name', rank_col]]
                st.dataframe(bottom_products, use_container_width=True)
                
            else:
                st.warning("선택한 기간에 데이터가 없습니다.")
                
        except Exception as e:
            st.error(f"분석 중 오류 발생: {e}")
    
    # 분석 결과가 있으면 계속 표시
    if 'analysis_completed' in st.session_state and st.session_state.analysis_completed:
        df_analysis = st.session_state.df_analysis
        analysis_periods = st.session_state.analysis_periods
        show_histogram = st.session_state.show_histogram
        show_boxplot = st.session_state.show_boxplot
        show_statistics = st.session_state.show_statistics
        
        # 컬럼 매핑
        period_mapping = {
            "1M": "r_1m",
            "3M": "r_3m", 
            "6M": "r_6m",
            "1Y": "r_1y",
            "2Y": "r_2y",
            "3Y": "r_3y",
            "설정일이후": "since_inception"
        }
        
        # 선택된 기간의 컬럼만 필터링
        selected_cols = [period_mapping[period] for period in analysis_periods if period in period_mapping]
        
        # 통계 테이블
        if show_statistics:
            st.subheader("📊 수익률 통계")
            stats_df = df_analysis[selected_cols].describe()
            st.dataframe(stats_df, use_container_width=True)
        
        # 수익률 분포 히스토그램
        if show_histogram:
            st.subheader("📈 수익률 분포 히스토그램")
            
            # 히스토그램 분석 기간 선택 (session_state로 상태 유지)
            if 'histogram_period' not in st.session_state:
                st.session_state.histogram_period = analysis_periods[0] if analysis_periods else "1Y"
            
            selected_period = st.selectbox("히스토그램 분석 기간 선택", analysis_periods, key="histogram_period_select_2")
            st.session_state.histogram_period = selected_period
            col_name = period_mapping[selected_period]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            font_prop = get_plot_font()
            ax.hist(df_analysis[col_name].dropna(), bins=30, alpha=0.7, edgecolor='black', color='skyblue')
            if font_prop:
                ax.set_xlabel(f'{selected_period} 수익률 (%)', fontsize=12, fontproperties=font_prop)
                ax.set_ylabel('빈도', fontsize=12, fontproperties=font_prop)
                ax.set_title(f'{selected_period} 수익률 분포', fontsize=14, fontweight='bold', fontproperties=font_prop)
            else:
                ax.set_xlabel(f'{selected_period} 수익률 (%)', fontsize=12)
                ax.set_ylabel('빈도', fontsize=12)
                ax.set_title(f'{selected_period} 수익률 분포', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
        
        # 박스플롯
        if show_boxplot:
            st.subheader("📦 수익률 박스플롯")
            fig2, ax2 = plt.subplots(figsize=(12, 6))
            font_prop = get_plot_font()
            df_analysis[selected_cols].boxplot(ax=ax2)
            if font_prop:
                ax2.set_ylabel('수익률 (%)', fontsize=12, fontproperties=font_prop)
                ax2.set_title('기간별 수익률 분포', fontsize=14, fontweight='bold', fontproperties=font_prop)
            else:
                ax2.set_ylabel('수익률 (%)', fontsize=12)
                ax2.set_title('기간별 수익률 분포', fontsize=14, fontweight='bold')
            ax2.tick_params(axis='x', rotation=45)
            plt.tight_layout()
            st.pyplot(fig2)
        
        # 추가 분석: 상위/하위 수익률 상품
        st.subheader("🏆 수익률 순위")
        
        # 순위 분석 기간 선택 (session_state로 상태 유지)
        if 'rank_period' not in st.session_state:
            st.session_state.rank_period = analysis_periods[0] if analysis_periods else "1Y"
        
        rank_period = st.selectbox("순위 분석 기간 선택", analysis_periods, key="rank_period_select_2")
        st.session_state.rank_period = rank_period
        rank_col = period_mapping[rank_period]
        
        st.write("**상위 10개 상품**")
        top_products = df_analysis.nlargest(10, rank_col)[['manager', 'product_name', rank_col]]
        st.dataframe(top_products, use_container_width=True)
        
        st.write("**하위 10개 상품**")
        bottom_products = df_analysis.nsmallest(10, rank_col)[['manager', 'product_name', rank_col]]
        st.dataframe(bottom_products, use_container_width=True)

elif menu == "🏢 운용사별 분석":
    st.title("🏢 운용사별 분석 (SQLite)")
    
    # 분석 옵션 설정
    st.subheader("🔧 분석 옵션 설정")
    
    # 분석 기준 선택
    analysis_criteria = st.selectbox(
        "분석 기준 선택",
        ["총 자산", "상품 수", "평균 수익률"],
        help="어떤 기준으로 운용사를 분석할지 선택하세요"
    )
    
    # 상위 N개 운용사 선택
    top_n = st.slider("상위 N개 운용사", min_value=5, max_value=20, value=10)
    
    # 시각화 옵션
    st.subheader("📊 시각화 옵션")
    show_product_count = st.checkbox("상품 수 차트", value=True)
    show_returns = st.checkbox("수익률 차트", value=True)
    show_assets = st.checkbox("자산 규모 차트", value=True)
    show_details = st.checkbox("상세 데이터 테이블", value=True)
    
    if st.button("🏢 운용사별 분석 실행", type="primary"):
        try:
            # SQLite DB에서 데이터 조회
            query = f"""
                SELECT manager, 
                       COUNT(*) as product_count,
                       AVG(r_1y) as avg_1y_return,
                       AVG(r_3y) as avg_3y_return,
                       SUM(total_amount) as total_assets
                FROM {TABLE_NAME}
                WHERE manager IS NOT NULL
                GROUP BY manager
                ORDER BY total_assets DESC
            """
            
            df_manager = execute_sql_query(query)
            
            if not df_manager.empty:
                st.success(f"✅ 운용사별 분석 완료: {len(df_manager)}개 운용사")
                
                # 분석 기준에 따른 정렬
                if analysis_criteria == "총 자산":
                    df_manager_sorted = df_manager.sort_values('total_assets', ascending=False)
                    sort_col = 'total_assets'
                    sort_title = '총 자산'
                elif analysis_criteria == "상품 수":
                    df_manager_sorted = df_manager.sort_values('product_count', ascending=False)
                    sort_col = 'product_count'
                    sort_title = '상품 수'
                else:  # 평균 수익률
                    df_manager_sorted = df_manager.sort_values('avg_1y_return', ascending=False)
                    sort_col = 'avg_1y_return'
                    sort_title = '평균 1년 수익률'
                
                # 운용사별 상품 수
                if show_product_count:
                    st.subheader("📊 운용사별 상품 수")
                    fig1, ax1 = plt.subplots(figsize=(12, 6))
                    font_prop = get_plot_font()
                    df_manager_sorted.head(top_n).plot(x='manager', y='product_count', kind='bar', ax=ax1, color='skyblue')
                    if font_prop:
                        ax1.set_xlabel('운용사', fontsize=12, fontproperties=font_prop)
                        ax1.set_ylabel('상품 수', fontsize=12, fontproperties=font_prop)
                        ax1.set_title(f'운용사별 상품 수 (상위 {top_n}개)', fontsize=14, fontweight='bold', fontproperties=font_prop)
                    else:
                        ax1.set_xlabel('운용사', fontsize=12)
                        ax1.set_ylabel('상품 수', fontsize=12)
                        ax1.set_title(f'운용사별 상품 수 (상위 {top_n}개)', fontsize=14, fontweight='bold')
                    ax1.tick_params(axis='x', rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig1)
                
                # 운용사별 평균 수익률
                if show_returns:
                    st.subheader("📈 운용사별 평균 수익률")
                    fig2, ax2 = plt.subplots(figsize=(12, 6))
                    font_prop = get_plot_font()
                    df_manager_sorted.head(top_n).plot(x='manager', y=['avg_1y_return', 'avg_3y_return'], kind='bar', ax=ax2)
                    if font_prop:
                        ax2.set_xlabel('운용사', fontsize=12, fontproperties=font_prop)
                        ax2.set_ylabel('평균 수익률 (%)', fontsize=12, fontproperties=font_prop)
                        ax2.set_title(f'운용사별 평균 수익률 (상위 {top_n}개)', fontsize=14, fontweight='bold', fontproperties=font_prop)
                        ax2.legend(['1년 수익률', '3년 수익률'], fontsize=10, prop=font_prop)
                    else:
                        ax2.set_xlabel('운용사', fontsize=12)
                        ax2.set_ylabel('평균 수익률 (%)', fontsize=12)
                        ax2.set_title(f'운용사별 평균 수익률 (상위 {top_n}개)', fontsize=14, fontweight='bold')
                        ax2.legend(['1년 수익률', '3년 수익률'], fontsize=10)
                    ax2.tick_params(axis='x', rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig2)
                
                # 운용사별 총 자산
                if show_assets:
                    st.subheader("💰 운용사별 총 자산")
                    fig3, ax3 = plt.subplots(figsize=(12, 6))
                    font_prop = get_plot_font()
                    df_manager_sorted.head(top_n).plot(x='manager', y='total_assets', kind='bar', ax=ax3, color='green')
                    if font_prop:
                        ax3.set_xlabel('운용사', fontsize=12, fontproperties=font_prop)
                        ax3.set_ylabel('총 자산 (원)', fontsize=12, fontproperties=font_prop)
                        ax3.set_title(f'운용사별 총 자산 (상위 {top_n}개)', fontsize=14, fontweight='bold', fontproperties=font_prop)
                    else:
                        ax3.set_xlabel('운용사', fontsize=12)
                        ax3.set_ylabel('총 자산 (원)', fontsize=12)
                        ax3.set_title(f'운용사별 총 자산 (상위 {top_n}개)', fontsize=14, fontweight='bold')
                    ax3.tick_params(axis='x', rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig3)
                
                # 상세 데이터 테이블
                if show_details:
                    st.subheader("📋 운용사별 상세 데이터")
                    st.dataframe(df_manager_sorted, use_container_width=True)
                
                # 요약 정보
                st.subheader("📊 분석 요약")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("총 운용사 수", len(df_manager))
                
                with col2:
                    avg_products = df_manager['product_count'].mean()
                    st.metric("평균 상품 수", f"{avg_products:.1f}개")
                
                with col3:
                    total_assets = df_manager['total_assets'].sum()
                    st.metric("전체 총 자산", f"{total_assets:,.0f}원")
                
            else:
                st.warning("운용사별 데이터가 없습니다.")
                
        except Exception as e:
            st.error(f"분석 중 오류 발생: {e}")

elif menu == "📊 상품별 분석":
    st.title("📊 상품별 분석 (SQLite)")
    
    # 분석 옵션 설정
    st.subheader("🔧 분석 옵션 설정")
    
    # 운용사 선택
    try:
        # 운용사 목록 조회
        manager_query = f"SELECT DISTINCT manager FROM {TABLE_NAME} WHERE manager IS NOT NULL ORDER BY manager"
        df_managers = execute_sql_query(manager_query)
        
        if not df_managers.empty:
            selected_manager = st.selectbox("운용사 선택", df_managers['manager'].tolist())
            
            # 분석 기준 선택
            product_analysis_criteria = st.selectbox(
                "분석 기준 선택",
                ["자산 규모", "수익률", "상품명"],
                help="어떤 기준으로 상품을 정렬할지 선택하세요"
            )
            
            # 시각화 옵션
            st.subheader("📊 시각화 옵션")
            show_heatmap = st.checkbox("수익률 히트맵", value=True)
            show_assets_chart = st.checkbox("자산 규모 차트", value=True)
            show_product_details = st.checkbox("상품별 상세 데이터", value=True)
            
            if st.button("📊 상품별 분석 실행", type="primary"):
                try:
                    # 선택된 운용사의 상품 데이터 조회
                    query = f"""
                        SELECT product_name, r_1m, r_3m, r_6m, r_1y, r_2y, r_3y, since_inception, total_amount
                        FROM {TABLE_NAME}
                        WHERE manager = ?
                        ORDER BY total_amount DESC
                    """
                    
                    df_products = execute_sql_query(query, params=[selected_manager])
                    
                    if not df_products.empty:
                        st.success(f"✅ {selected_manager} 상품 분석 완료: {len(df_products)}개 상품")
                        
                        # 분석 기준에 따른 정렬
                        if product_analysis_criteria == "자산 규모":
                            df_products_sorted = df_products.sort_values('total_amount', ascending=False)
                        elif product_analysis_criteria == "수익률":
                            df_products_sorted = df_products.sort_values('r_1y', ascending=False)
                        else:  # 상품명
                            df_products_sorted = df_products.sort_values('product_name')
                        
                        # 상품별 수익률 히트맵
                        if show_heatmap:
                            st.subheader("🔥 상품별 수익률 히트맵")
                            
                            try:
                                import plotly.express as px
                                import plotly.graph_objects as go
                                
                                # 수익률 데이터 준비
                                numeric_cols = ['r_1m', 'r_3m', 'r_6m', 'r_1y', 'r_2y', 'r_3y', 'since_inception']
                                df_heatmap = df_products_sorted[numeric_cols].copy()
                                
                                # 컬럼명을 한글로 변경
                                col_mapping = {
                                    'r_1m': '1개월',
                                    'r_3m': '3개월', 
                                    'r_6m': '6개월',
                                    'r_1y': '1년',
                                    'r_2y': '2년',
                                    'r_3y': '3년',
                                    'since_inception': '설정일이후'
                                }
                                df_heatmap.columns = [col_mapping[col] for col in df_heatmap.columns]
                                
                                # 히트맵 생성 (데이터 전치하여 올바른 방향으로 표시)
                                fig = px.imshow(
                                    df_heatmap.values.T,  # 전치하여 올바른 방향으로 표시
                                    x=df_products_sorted['product_name'],
                                    y=list(col_mapping.values()),
                                    color_continuous_scale='RdYlGn',
                                    aspect='auto',
                                    title=f'{selected_manager} 상품별 수익률 히트맵'
                                )
                                
                                # 차트 스타일링
                                fig.update_layout(
                                    title_font_size=16,
                                    title_font_color='#2E86AB',
                                    xaxis_title='상품명',
                                    yaxis_title='수익률 기간',
                                    height=500,
                                    xaxis_tickangle=-45
                                )
                                
                                # 호버 템플릿 설정
                                fig.update_traces(
                                    hovertemplate="<b>%{y}</b><br>" +
                                                "상품: %{x}<br>" +
                                                "수익률: %{z:.2f}%<extra></extra>"
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                            except ImportError:
                                # Plotly가 없는 경우 seaborn 사용
                                numeric_cols = ['r_1m', 'r_3m', 'r_6m', 'r_1y', 'r_2y', 'r_3y', 'since_inception']
                                
                                fig, ax = plt.subplots(figsize=(14, 8))
                                font_prop = get_plot_font()
                                sns.heatmap(df_products_sorted[numeric_cols].T, 
                                          annot=True, fmt='.2f', cmap='RdYlGn', 
                                          xticklabels=df_products_sorted['product_name'],
                                          yticklabels=numeric_cols)
                                if font_prop:
                                    ax.set_title(f'{selected_manager} 상품별 수익률 히트맵', fontsize=14, fontweight='bold', fontproperties=font_prop)
                                else:
                                    ax.set_title(f'{selected_manager} 상품별 수익률 히트맵', fontsize=14, fontweight='bold')
                                plt.xticks(rotation=45, ha='right')
                                plt.tight_layout()
                                st.pyplot(fig)
                        
                        # 상품별 자산 규모
                        if show_assets_chart:
                            st.subheader("💰 상품별 자산 규모")
                            
                            # Plotly를 사용한 인터랙티브 차트
                            try:
                                import plotly.express as px
                                import plotly.graph_objects as go
                                
                                # 자산 규모를 억원 단위로 변환
                                df_chart = df_products_sorted.copy()
                                df_chart['자산규모_억원'] = df_chart['total_amount'] / 100000000
                                
                                fig = px.bar(
                                    df_chart,
                                    x='product_name',
                                    y='자산규모_억원',
                                    title=f'{selected_manager} 상품별 자산 규모',
                                    labels={'product_name': '상품명', '자산규모_억원': '자산 규모 (억원)'},
                                    color='자산규모_억원',
                                    color_continuous_scale='Oranges',
                                    hover_data={'total_amount': True, '자산규모_억원': False}
                                )
                                
                                # 차트 스타일링
                                fig.update_layout(
                                    title_font_size=16,
                                    title_font_color='#2E86AB',
                                    xaxis_title_font_size=12,
                                    yaxis_title_font_size=12,
                                    xaxis_tickangle=-45,
                                    height=500,
                                    showlegend=False
                                )
                                
                                # 호버 템플릿 설정
                                fig.update_traces(
                                    hovertemplate="<b>%{x}</b><br>" +
                                                "자산 규모: %{y:.1f}억원<br>" +
                                                "총액: %{customdata[0]:,}원<extra></extra>"
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                                
                            except ImportError:
                                # Plotly가 없는 경우 matplotlib 사용
                                fig2, ax2 = plt.subplots(figsize=(14, 8))
                                font_prop = get_plot_font()
                                bars = ax2.bar(range(len(df_products_sorted)), df_products_sorted['total_amount'], color='orange', alpha=0.7)
                                if font_prop:
                                    ax2.set_xlabel('상품명', fontsize=12, fontproperties=font_prop)
                                    ax2.set_ylabel('자산 규모 (원)', fontsize=12, fontproperties=font_prop)
                                    ax2.set_title(f'{selected_manager} 상품별 자산 규모', fontsize=14, fontweight='bold', fontproperties=font_prop)
                                else:
                                    ax2.set_xlabel('상품명', fontsize=12)
                                    ax2.set_ylabel('자산 규모 (원)', fontsize=12)
                                    ax2.set_title(f'{selected_manager} 상품별 자산 규모', fontsize=14, fontweight='bold')
                                
                                # x축 레이블 설정
                                ax2.set_xticks(range(len(df_products_sorted)))
                                ax2.set_xticklabels(df_products_sorted['product_name'], rotation=45, ha='right')
                                
                                # 그리드 추가
                                ax2.grid(True, alpha=0.3, axis='y')
                                
                                # 값 표시
                                for i, bar in enumerate(bars):
                                    height = bar.get_height()
                                    ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                            f'{height:,.0f}', ha='center', va='bottom', fontsize=9)
                                
                                plt.tight_layout()
                                st.pyplot(fig2)
                        
                        # 상세 데이터 테이블
                        if show_product_details:
                            st.subheader("📋 상품별 상세 데이터")
                            st.dataframe(df_products_sorted, use_container_width=True)
                        
                        # 요약 정보
                        st.subheader("📊 상품 분석 요약")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("총 상품 수", len(df_products))
                        
                        with col2:
                            avg_return = df_products['r_1y'].mean()
                            st.metric("평균 1년 수익률", f"{avg_return:.2f}%")
                        
                        with col3:
                            total_assets = df_products['total_amount'].sum()
                            st.metric("총 자산", f"{total_assets:,.0f}원")
                        
                    else:
                        st.warning(f"{selected_manager}의 상품 데이터가 없습니다.")
                        
                except Exception as e:
                    st.error(f"분석 중 오류 발생: {e}")
        else:
            st.error("운용사 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"운용사 목록 조회 중 오류 발생: {e}")

elif menu == "🗑️ 데이터 초기화":
    st.title("🗑️ 데이터 초기화")
    
    # 경고 메시지
    st.warning("⚠️ **주의**: 이 작업은 되돌릴 수 없습니다!")
    st.info("데이터 초기화를 하면 모든 기존 데이터가 영구적으로 삭제됩니다.")
    
    # 현재 데이터 현황 표시
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 전체 레코드 수 확인
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        total_records = cursor.fetchone()[0]
        
        # 기준일별 데이터 수 확인
        cursor.execute(f"SELECT asof_date, COUNT(*) as count FROM {TABLE_NAME} GROUP BY asof_date ORDER BY asof_date DESC")
        date_counts = cursor.fetchall()
        
        conn.close()
        
        st.subheader("📊 현재 데이터 현황")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("총 레코드 수", f"{total_records:,}개")
        
        with col2:
            st.metric("기준일 수", f"{len(date_counts)}개")
        
        # 기준일별 데이터 현황
        if date_counts:
            st.write("**기준일별 데이터 현황:**")
            date_df = pd.DataFrame(date_counts, columns=['기준일', '레코드 수'])
            st.dataframe(date_df, use_container_width=True)
        
    except Exception as e:
        st.error(f"데이터 현황 조회 중 오류: {e}")
    
    # 확인 절차
    st.subheader("🔐 초기화 확인")
    
    # 1단계: 확인 체크박스
    confirm_checkbox = st.checkbox("모든 데이터가 삭제됨을 이해합니다")
    
    # 2단계: 확인 텍스트 입력
    confirm_text = st.text_input(
        "초기화를 확인하려면 '초기화'를 입력하세요:",
        placeholder="초기화"
    )
    
    # 3단계: 초기화 버튼
    if confirm_checkbox and confirm_text == "초기화":
        if st.button("🗑️ 데이터 초기화 실행", type="primary", use_container_width=True):
            try:
                # 진행 상황 표시
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("데이터베이스 연결 중...")
                progress_bar.progress(20)
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                status_text.text("기존 데이터 삭제 중...")
                progress_bar.progress(50)
                
                # 모든 데이터 삭제
                cursor.execute(f"DELETE FROM {TABLE_NAME}")
                deleted_count = cursor.rowcount
                
                status_text.text("변경사항 저장 중...")
                progress_bar.progress(80)
                
                conn.commit()
                conn.close()
                
                status_text.text("초기화 완료!")
                progress_bar.progress(100)
                
                st.success(f"✅ 데이터 초기화 완료! (삭제된 레코드: {deleted_count:,}개)")
                st.info("이제 새로운 데이터를 업로드할 수 있습니다.")
                
                # 진행 상황 초기화
                progress_bar.empty()
                status_text.empty()
                
                # 페이지 새로고침을 위한 JavaScript 실행
                st.rerun()
                
            except Exception as e:
                st.error(f"데이터 초기화 중 오류 발생: {e}")
                st.code(traceback.format_exc())
                
                # 연결 정리
                try:
                    if cursor:
                        cursor.close()
                    if conn:
                        conn.close()
                except:
                    pass
    elif confirm_checkbox and confirm_text != "초기화":
        st.error("❌ 정확히 '초기화'를 입력해주세요.")
    elif not confirm_checkbox:
        st.info("💡 초기화를 진행하려면 위의 확인 체크박스를 선택하고 정확한 텍스트를 입력해주세요.")

elif menu == "📅 기간별 분석":
    st.title("📅 기간별 분석 (SQLite)")
    
    # 분석 옵션 설정
    st.subheader("🔧 분석 옵션 설정")
    
    # 분석 기간 선택
    col1, col2 = st.columns(2)
    with col1:
        analysis_start = st.date_input("분석 시작일", value=pd.Timestamp.now() - pd.Timedelta(days=365))
    with col2:
        analysis_end = st.date_input("분석 종료일", value=pd.Timestamp.now())
    
    # 분석 지표 선택
    analysis_metrics = st.multiselect(
        "분석할 지표 선택",
        ["상품 수", "평균 수익률", "총 자산"],
        default=["상품 수", "평균 수익률", "총 자산"]
    )
    
    # 시각화 옵션
    st.subheader("📊 시각화 옵션")
    show_product_trend = st.checkbox("상품 수 변화 추이", value=True)
    show_return_trend = st.checkbox("수익률 변화 추이", value=True)
    show_asset_trend = st.checkbox("자산 변화 추이", value=True)
    show_timeline_details = st.checkbox("기간별 상세 데이터", value=True)
    
    if st.button("📅 기간별 분석 실행", type="primary"):
        try:
            # DB에서 데이터 조회
            query = f"""
                SELECT asof_date, 
                       COUNT(*) as product_count,
                       AVG(r_1m) as avg_1m_return,
                       AVG(r_3m) as avg_3m_return,
                       AVG(r_6m) as avg_6m_return,
                       AVG(r_1y) as avg_1y_return,
                       SUM(total_amount) as total_assets
                FROM {TABLE_NAME}
                WHERE asof_date BETWEEN ? AND ?
                GROUP BY asof_date
                ORDER BY asof_date
            """
            
            df_timeline = execute_sql_query(query, params=[analysis_start, analysis_end])
            
            if not df_timeline.empty:
                st.success(f"✅ 기간별 분석 완료: {len(df_timeline)}개 기간")
                
                # 기간별 상품 수 변화
                if show_product_trend and "상품 수" in analysis_metrics:
                    st.subheader("📈 기간별 상품 수 변화")
                    fig1, ax1 = plt.subplots(figsize=(12, 6))
                    font_prop = get_plot_font()
                    ax1.plot(df_timeline['asof_date'], df_timeline['product_count'], marker='o', linewidth=2, markersize=6, color='blue')
                    if font_prop:
                        ax1.set_xlabel('날짜', fontsize=12, fontproperties=font_prop)
                        ax1.set_ylabel('상품 수', fontsize=12, fontproperties=font_prop)
                        ax1.set_title('기간별 상품 수 변화', fontsize=14, fontweight='bold', fontproperties=font_prop)
                    else:
                        ax1.set_xlabel('날짜', fontsize=12)
                        ax1.set_ylabel('상품 수', fontsize=12)
                        ax1.set_title('기간별 상품 수 변화', fontsize=14, fontweight='bold')
                    ax1.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig1)
                
                # 기간별 평균 수익률 변화
                if show_return_trend and "평균 수익률" in analysis_metrics:
                    st.subheader("📊 기간별 평균 수익률 변화")
                    fig2, ax2 = plt.subplots(figsize=(12, 6))
                    font_prop = get_plot_font()
                    ax2.plot(df_timeline['asof_date'], df_timeline['avg_1m_return'], label='1개월', marker='o', linewidth=2)
                    ax2.plot(df_timeline['asof_date'], df_timeline['avg_3m_return'], label='3개월', marker='s', linewidth=2)
                    ax2.plot(df_timeline['asof_date'], df_timeline['avg_6m_return'], label='6개월', marker='^', linewidth=2)
                    ax2.plot(df_timeline['asof_date'], df_timeline['avg_1y_return'], label='1년', marker='d', linewidth=2)
                    if font_prop:
                        ax2.set_xlabel('날짜', fontsize=12, fontproperties=font_prop)
                        ax2.set_ylabel('평균 수익률 (%)', fontsize=12, fontproperties=font_prop)
                        ax2.set_title('기간별 평균 수익률 변화', fontsize=14, fontweight='bold', fontproperties=font_prop)
                        ax2.legend(fontsize=10, prop=font_prop)
                    else:
                        ax2.set_xlabel('날짜', fontsize=12)
                        ax2.set_ylabel('평균 수익률 (%)', fontsize=12)
                        ax2.set_title('기간별 평균 수익률 변화', fontsize=14, fontweight='bold')
                        ax2.legend(fontsize=10)
                    ax2.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig2)
                
                # 기간별 총 자산 변화
                if show_asset_trend and "총 자산" in analysis_metrics:
                    st.subheader("💰 기간별 총 자산 변화")
                    fig3, ax3 = plt.subplots(figsize=(12, 6))
                    font_prop = get_plot_font()
                    ax3.plot(df_timeline['asof_date'], df_timeline['total_assets'], marker='o', color='green', linewidth=2, markersize=6)
                    if font_prop:
                        ax3.set_xlabel('날짜', fontsize=12, fontproperties=font_prop)
                        ax3.set_ylabel('총 자산 (원)', fontsize=12, fontproperties=font_prop)
                        ax3.set_title('기간별 총 자산 변화', fontsize=14, fontweight='bold', fontproperties=font_prop)
                    else:
                        ax3.set_xlabel('날짜', fontsize=12)
                        ax3.set_ylabel('총 자산 (원)', fontsize=12)
                        ax3.set_title('기간별 총 자산 변화', fontsize=14, fontweight='bold')
                    ax3.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig3)
                
                # 상세 데이터 테이블
                if show_timeline_details:
                    st.subheader("📋 기간별 상세 데이터")
                    st.dataframe(df_timeline, use_container_width=True)
                
                # 요약 정보
                st.subheader("📊 기간별 분석 요약")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    total_periods = len(df_timeline)
                    st.metric("분석 기간 수", f"{total_periods}개")
                
                with col2:
                    avg_products = df_timeline['product_count'].mean()
                    st.metric("평균 상품 수", f"{avg_products:.1f}개")
                
                with col3:
                    total_assets = df_timeline['total_assets'].sum()
                    st.metric("전체 총 자산", f"{total_assets:,.0f}원")
                
            else:
                st.warning("선택한 기간에 데이터가 없습니다.")
                
        except Exception as e:
            st.error(f"분석 중 오류 발생: {e}")

elif menu == "📈 시계열 수익률":
    st.title("📈 시계열 수익률 분석 (SQLite)")
    
    # 분석 옵션 설정
    st.subheader("🔧 분석 옵션 설정")
    
    # 분석 기간 선택
    col1, col2 = st.columns(2)
    with col1:
        timeline_start = st.date_input("분석 시작일", value=pd.Timestamp.now() - pd.Timedelta(days=365))
    with col2:
        timeline_end = st.date_input("분석 종료일", value=pd.Timestamp.now())
    
    # 운용사 선택
    try:
        # 운용사 목록 조회
        manager_query = f"""
            SELECT DISTINCT manager 
            FROM {TABLE_NAME} 
            WHERE manager IS NOT NULL 
            AND asof_date BETWEEN ? AND ?
            ORDER BY manager
        """
        df_managers = execute_sql_query(manager_query, params=[timeline_start, timeline_end])
        
        if not df_managers.empty:
            selected_manager = st.selectbox("운용사 선택", df_managers['manager'].tolist())
            
            # 상품 선택
            try:
                # 선택된 운용사의 상품 목록 조회
                product_query = f"""
                    SELECT DISTINCT product_name 
                    FROM {TABLE_NAME} 
                    WHERE manager = ?
                    AND asof_date BETWEEN ? AND ?
                    ORDER BY product_name
                """
                df_products = execute_sql_query(product_query, params=[selected_manager, timeline_start, timeline_end])
                
                if not df_products.empty:
                    selected_products = st.multiselect(
                        "상품 선택 (여러 개 선택 가능)",
                        df_products['product_name'].tolist(),
                        default=df_products['product_name'].tolist()[:3]  # 기본값으로 처음 3개
                    )
                    
                    # 수익률 기간 선택
                    return_periods = st.multiselect(
                        "수익률 기간 선택",
                        ["1M", "3M", "6M", "1Y", "2Y", "3Y", "설정일이후"],
                        default=["1Y", "3Y"]
                    )
                    
                    # 시각화 옵션
                    st.subheader("📊 시각화 옵션")
                    show_individual_lines = st.checkbox("개별 상품 라인 표시", value=True)
                    show_average_line = st.checkbox("평균 라인 표시", value=True)
                    show_legend = st.checkbox("범례 표시", value=True)
                    
                    if st.button("📈 시계열 수익률 분석 실행", type="primary"):
                        try:
                            if not selected_products:
                                st.warning("분석할 상품을 선택해주세요.")
                                st.stop()
                            
                            if not return_periods:
                                st.warning("분석할 수익률 기간을 선택해주세요.")
                                st.stop()
                            
                            # 선택된 상품들의 시계열 데이터 조회
                            # 컬럼 매핑
                            period_mapping = {
                                "1M": "r_1m",
                                "3M": "r_3m", 
                                "6M": "r_6m",
                                "1Y": "r_1y",
                                "2Y": "r_2y",
                                "3Y": "r_3y",
                                "설정일이후": "since_inception"
                            }
                            
                            selected_cols = [period_mapping[period] for period in return_periods if period in period_mapping]
                            
                            # 데이터 조회
                            products_str = "', '".join(selected_products)
                            query = f"""
                                SELECT asof_date, product_name, {', '.join(selected_cols)}
                                FROM {TABLE_NAME}
                                WHERE manager = ?
                                AND product_name IN ({','.join(['?'] * len(selected_products))})
                                AND asof_date BETWEEN ? AND ?
                                ORDER BY asof_date, product_name
                            """
                            
                            params = [selected_manager] + selected_products + [timeline_start, timeline_end]
                            df_timeline = execute_sql_query(query, params=params)
                            
                            if not df_timeline.empty:
                                st.success(f"✅ 시계열 분석 완료: {len(df_timeline)}개 데이터 포인트")
                                
                                # 각 수익률 기간별로 시계열 그래프 생성
                                for period in return_periods:
                                    if period in period_mapping:
                                        col_name = period_mapping[period]
                                        
                                        st.subheader(f"📈 {period} 수익률 시계열")
                                        
                                        fig, ax = plt.subplots(figsize=(14, 8))
                                        font_prop = get_plot_font()
                                        
                                        # 개별 상품 라인
                                        if show_individual_lines:
                                            for product in selected_products:
                                                product_data = df_timeline[df_timeline['product_name'] == product]
                                                if not product_data.empty:
                                                    ax.plot(product_data['asof_date'], product_data[col_name], 
                                                           marker='o', linewidth=2, markersize=4, 
                                                           label=f'{product}', alpha=0.8)
                                        
                                        # 평균 라인
                                        if show_average_line:
                                            avg_data = df_timeline.groupby('asof_date')[col_name].mean().reset_index()
                                            ax.plot(avg_data['asof_date'], avg_data[col_name], 
                                                   marker='s', linewidth=3, markersize=6, 
                                                   label='평균', color='red', linestyle='--')
                                        
                                        if font_prop:
                                            ax.set_xlabel('날짜', fontsize=12, fontproperties=font_prop)
                                            ax.set_ylabel(f'{period} 수익률 (%)', fontsize=12, fontproperties=font_prop)
                                            ax.set_title(f'{selected_manager} - {period} 수익률 시계열', fontsize=14, fontweight='bold', fontproperties=font_prop)
                                            if show_legend:
                                                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, prop=font_prop)
                                        else:
                                            ax.set_xlabel('날짜', fontsize=12)
                                            ax.set_ylabel(f'{period} 수익률 (%)', fontsize=12)
                                            ax.set_title(f'{selected_manager} - {period} 수익률 시계열', fontsize=14, fontweight='bold')
                                            if show_legend:
                                                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
                                        
                                        ax.grid(True, alpha=0.3)
                                        plt.xticks(rotation=45)
                                        plt.tight_layout()
                                        st.pyplot(fig)
                                        
                                        # OpenAI API로 그래프 분석
                                        with st.spinner("🤖 AI가 그래프를 분석하고 있습니다..."):
                                            try:
                                                # 그래프를 base64로 변환
                                                image_base64 = save_plot_as_base64(fig)
                                                if image_base64:
                                                    # OpenAI API 호출
                                                    analysis_result = analyze_with_openai(
                                                        image_base64, 
                                                        analysis_type=f"{period} 수익률 시계열"
                                                    )
                                                    
                                                    # 분석 결과 표시
                                                    st.subheader("🤖 AI 분석 결과")
                                                    st.markdown(analysis_result)
                                            except Exception as e:
                                                st.error(f"AI 분석 중 오류: {e}")
                                
                                # 요약 통계 테이블
                                st.subheader("📊 시계열 요약 통계")
                                
                                summary_data = []
                                for product in selected_products:
                                    product_data = df_timeline[df_timeline['product_name'] == product]
                                    if not product_data.empty:
                                        for period in return_periods:
                                            if period in period_mapping:
                                                col_name = period_mapping[period]
                                                avg_return = product_data[col_name].mean()
                                                max_return = product_data[col_name].max()
                                                min_return = product_data[col_name].min()
                                                std_return = product_data[col_name].std()
                                                
                                                summary_data.append({
                                                    '상품명': product,
                                                    '수익률 기간': period,
                                                    '평균 수익률': avg_return,  # 숫자로 저장
                                                    '최고 수익률': max_return,  # 숫자로 저장
                                                    '최저 수익률': min_return,  # 숫자로 저장
                                                    '표준편차': std_return     # 숫자로 저장
                                                })
                                
                                if summary_data:
                                    summary_df = pd.DataFrame(summary_data)
                                    # 숫자 컬럼을 소수점 2자리로 포맷팅 (정렬 가능하도록)
                                    numeric_columns = ['평균 수익률', '최고 수익률', '최저 수익률', '표준편차']
                                    for col in numeric_columns:
                                        if col in summary_df.columns:
                                            # NaN 값을 0으로 처리하여 정렬 가능하게 만듦
                                            summary_df[col] = summary_df[col].fillna(0)
                                    st.dataframe(summary_df, use_container_width=True)
                                    
                                    # OpenAI API로 표 분석
                                    with st.spinner("🤖 AI가 통계 표를 분석하고 있습니다..."):
                                        try:
                                            # 표 데이터를 문자열로 변환
                                            table_data = summary_df.to_string(index=False)
                                            
                                            # 더미 이미지 생성 (표 분석용)
                                            fig_dummy, ax_dummy = plt.subplots(figsize=(1, 1))
                                            ax_dummy.text(0.5, 0.5, '통계 분석', ha='center', va='center', transform=ax_dummy.transAxes)
                                            ax_dummy.axis('off')
                                            
                                            # 그래프를 base64로 변환
                                            image_base64 = save_plot_as_base64(fig_dummy)
                                            if image_base64:
                                                # OpenAI API 호출
                                                analysis_result = analyze_with_openai(
                                                    image_base64, 
                                                    table_data=table_data,
                                                    analysis_type="시계열 수익률 통계"
                                                )
                                                
                                                # 분석 결과 표시
                                                st.subheader("🤖 AI 통계 분석 결과")
                                                st.markdown(analysis_result)
                                        except Exception as e:
                                            st.error(f"AI 분석 중 오류: {e}")
                                
                                # 상세 데이터 테이블
                                st.subheader("📋 상세 시계열 데이터")
                                st.dataframe(df_timeline, use_container_width=True)
                                
                                # OpenAI API로 상세 데이터 분석
                                with st.spinner("🤖 AI가 상세 데이터를 분석하고 있습니다..."):
                                    try:
                                        # 상세 데이터를 문자열로 변환 (처음 10행만)
                                        detail_data = df_timeline.head(10).to_string(index=False)
                                        
                                        # 더미 이미지 생성 (데이터 분석용)
                                        fig_dummy2, ax_dummy2 = plt.subplots(figsize=(1, 1))
                                        ax_dummy2.text(0.5, 0.5, '데이터 분석', ha='center', va='center', transform=ax_dummy2.transAxes)
                                        ax_dummy2.axis('off')
                                        
                                        # 그래프를 base64로 변환
                                        image_base64 = save_plot_as_base64(fig_dummy2)
                                        if image_base64:
                                            # OpenAI API 호출
                                            analysis_result = analyze_with_openai(
                                                image_base64, 
                                                table_data=detail_data,
                                                analysis_type="시계열 상세 데이터"
                                            )
                                            
                                            # 분석 결과 표시
                                            st.subheader("🤖 AI 상세 데이터 분석 결과")
                                            st.markdown(analysis_result)
                                    except Exception as e:
                                        st.error(f"AI 분석 중 오류: {e}")
                                
                            else:
                                st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
                                
                        except Exception as e:
                            st.error(f"시계열 분석 중 오류 발생: {e}")
                else:
                    st.warning(f"{selected_manager}의 상품 데이터가 없습니다.")
                    
            except Exception as e:
                st.error(f"상품 목록 조회 중 오류 발생: {e}")
        else:
            st.warning("선택한 기간에 운용사 데이터가 없습니다.")
            
    except Exception as e:
        st.error(f"운용사 목록 조회 중 오류 발생: {e}")
