# GMGN 크립토 트래커 📈

GMGN.ai 웹사이트의 종목 정보를 실시간으로 추적하고 급등하는 암호화폐에 대한 알림을 제공하는 시스템입니다.

## 🚀 주요 기능

- **실시간 데이터 수집**: GMGN.ai trending 페이지에서 최신 종목 정보 수집
- **실시간 차트**: 가격 변동을 시각적으로 추적
- **스마트 알림**: 급등하는 종목에 대한 즉시 Telegram 알림
- **웹 대시보드**: 직관적인 웹 인터페이스로 종목 모니터링

## 🛠️ 기술 스택

- **Backend**: FastAPI, SQLAlchemy, Celery
- **Frontend**: HTML/CSS/JavaScript, Chart.js
- **Database**: SQLite (개발용) / PostgreSQL (프로덕션)
- **Cache**: Redis
- **Notification**: Telegram Bot API

## ⚡ 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
uv sync

# 환경변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 값들을 설정하세요
```

### 2. 데이터베이스 초기화

```bash
# 데이터베이스 마이그레이션
alembic upgrade head
```

### 3. 서비스 실행

```bash
# Redis 서버 시작 (별도 터미널)
redis-server

# Celery 워커 시작 (별도 터미널)
celery -A app.celery_app worker --loglevel=info

# FastAPI 서버 시작
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 웹 대시보드 접속

브라우저에서 `http://localhost:8000` 접속

## 📁 프로젝트 구조

```
gmgn_crawl/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 메인 애플리케이션
│   ├── config.py            # 설정 관리
│   ├── database.py          # 데이터베이스 설정
│   ├── models/              # SQLAlchemy 모델
│   ├── schemas/             # Pydantic 스키마
│   ├── api/                 # API 라우터
│   ├── services/            # 비즈니스 로직
│   ├── scrapers/            # 웹 스크래핑 모듈
│   ├── notifications/       # 알림 시스템
│   └── static/              # 정적 파일 (CSS, JS)
├── alembic/                 # 데이터베이스 마이그레이션
├── tests/                   # 테스트 코드
├── .env.example             # 환경변수 예시
├── pyproject.toml           # 프로젝트 설정
└── README.md
```

## 🔧 개발 가이드

### 코드 포맷팅

```bash
# 코드 포맷팅
black .
isort .

# 린팅
flake8 .
mypy .
```

### 테스트 실행

```bash
pytest tests/
```

## 📊 사용법

1. **대시보드 모니터링**: 웹 인터페이스에서 실시간 종목 상황 확인
2. **알림 설정**: Telegram 봇을 통한 개인화된 알림 수신
3. **차트 분석**: 가격 변동 패턴 및 트렌드 분석

## ⚠️ 주의사항

- 이 도구는 교육 및 연구 목적으로 제작되었습니다
- 투자 결정은 본인의 책임하에 이루어져야 합니다
- GMGN.ai 서비스 약관을 준수하여 사용해주세요

## 📄 라이센스

MIT License

## 🤝 기여하기

프로젝트 개선에 기여해주세요! Issue 등록이나 Pull Request를 환영합니다.