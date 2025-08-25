# OpenAI API 키 관리 가이드

## 현재 설정 방식
**Streamlit Cloud Secrets를 우선적으로 사용합니다.**

### 설정 우선순위
1. **Streamlit Cloud Secrets** (최우선순위)
2. **환경 변수** (로컬 개발용)
3. **config.toml** (로컬 개발용 fallback)

## Streamlit Cloud Secrets 설정 방법

### 1. Streamlit Cloud에서 Secrets 설정
1. [Streamlit Cloud](https://share.streamlit.io/)에 로그인
2. 해당 앱의 "Settings" → "Secrets" 메뉴로 이동
3. 다음 형식으로 Secrets 추가:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
OPENAI_API_USE_PW = "bslee73"
```

### 2. 로컬 개발 환경에서 Secrets 테스트
`.streamlit/secrets.toml` 파일을 생성하여 로컬에서 테스트:

```toml
OPENAI_API_KEY = "sk-your-api-key-here"
OPENAI_API_USE_PW = "bslee73"
```

## 문제 상황
새로운 OpenAI API 키를 생성하고 설정하면 기존 키가 삭제되는 문제가 발생할 수 있습니다.

## 해결 방법

### 1. 키 생성 전 백업
- 기존 키를 안전한 곳에 백업
- 키 생성 전 현재 키가 정상 작동하는지 확인

### 2. 키 생성 시 주의사항
- **새 키 추가**: 기존 키를 삭제하지 않고 새 키를 추가로 생성
- **키 테스트**: 새 키가 정상 작동하는지 확인 후 기존 키 처리
- **단계적 교체**: 한 번에 하나씩 키를 교체

### 3. 키 복구 방법
1. **OpenAI Platform 확인**
   - [OpenAI Platform](https://platform.openai.com/account/api-keys) 접속
   - 키 목록에서 삭제된 키 확인
   - 키가 "비활성화" 상태라면 "활성화" 버튼 클릭

2. **백업에서 복구**
   - Streamlit Cloud Secrets에서 백업 키로 교체
   - 또는 로컬 secrets.toml 파일에서 백업 키 사용

3. **새 키 재생성**
   - 기존 키가 완전히 삭제된 경우 새 키 생성
   - 키 생성 시 "프로젝트 키" 선택

### 4. 키 유형별 특징
- **프로젝트 키 (sk-proj-)**: 특정 프로젝트에 연결된 키
- **서비스 계정 키 (sk-svcacct-)**: 서비스 계정에 연결된 키
- **일반 키 (sk-)**: 개인 계정의 일반 키

### 5. 권장 사항
- **키 백업**: 중요한 키는 항상 백업
- **단계적 교체**: 키 교체 시 단계적으로 진행
- **테스트**: 새 키 설정 후 반드시 테스트
- **모니터링**: 키 사용량과 상태 정기적 확인

## 현재 설정
- **설정 방식**: Streamlit Cloud Secrets 우선 사용
- **API 키**: Streamlit Cloud Secrets에서 `OPENAI_API_KEY` 설정
- **패스워드**: Streamlit Cloud Secrets에서 `OPENAI_API_USE_PW` 설정 (기본값: bslee73)

## 다음 단계
1. Streamlit Cloud Secrets에서 `OPENAI_API_KEY`와 `OPENAI_API_USE_PW` 설정
2. 앱을 재시작하여 키가 정상 작동하는지 확인
3. AI 분석 기능 테스트

## 로컬 개발 환경
로컬에서 개발할 때는 `.streamlit/secrets.toml` 파일을 사용하거나 환경 변수를 설정할 수 있습니다:

```bash
# 환경 변수 설정 (Windows)
set OPENAI_API_KEY=sk-your-api-key-here
set OPENAI_API_USE_PW=bslee73

# 환경 변수 설정 (Linux/Mac)
export OPENAI_API_KEY=sk-your-api-key-here
export OPENAI_API_USE_PW=bslee73
```
