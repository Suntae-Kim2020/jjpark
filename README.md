# Fund Returns 분석 시스템

SQLite 기반의 펀드 수익률 분석 및 시각화 시스템입니다.

## 주요 기능

- 📤 **데이터 업로드**: 엑셀 파일을 통한 펀드 데이터 업로드
- 📈 **수익률 분석**: 히스토그램, 박스플롯, 통계 분석
- 🏢 **운용사별 분석**: 운용사별 상품 수, 수익률, 자산 규모 분석
- 📊 **상품별 분석**: 상품별 수익률 히트맵 및 자산 규모 분석
- 📅 **기간별 분석**: 시간에 따른 변화 추이 분석
- 📈 **시계열 수익률**: 개별 상품의 시계열 수익률 분석

## 배포 방법

### 1. GitHub에 코드 업로드

1. 이 프로젝트를 GitHub 저장소에 업로드합니다.
2. `fonts/NanumGothic.ttf` 파일이 포함되어 있는지 확인합니다.

### 2. Streamlit Cloud 배포

1. [Streamlit Cloud](https://share.streamlit.io/)에 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택 및 설정:
   - **Repository**: `your-username/your-repo-name`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. "Deploy!" 클릭

## 파일 구조

```
├── app.py                 # 메인 애플리케이션 파일
├── requirements.txt       # Python 패키지 의존성
├── .streamlit/
│   └── config.toml       # Streamlit 설정
├── fonts/
│   └── NanumGothic.ttf   # 한글 폰트 파일
└── README.md             # 이 파일
```

## 한글 폰트 지원

- GitHub의 `fonts/NanumGothic.ttf` 파일을 우선 사용
- 시스템에 설치된 한글 폰트 자동 감지
- 웹 폰트 fallback 지원

## 데이터베이스

- SQLite 파일 기반 데이터베이스 사용
- `fund_returns.db` 파일에 데이터 저장
- 서비스 재시작 시에도 데이터 유지

## 사용법

1. **데이터 업로드**: 엑셀 파일을 업로드하여 데이터베이스에 저장
2. **분석 실행**: 원하는 분석 메뉴를 선택하고 옵션 설정
3. **결과 확인**: 시각화 결과와 통계 데이터 확인

## 주의사항

- Streamlit Cloud에서는 파일 시스템 접근이 제한적일 수 있습니다
- 한글 폰트가 제대로 표시되지 않는 경우 웹 폰트로 자동 전환됩니다
- 대용량 데이터 처리 시 시간이 걸릴 수 있습니다
