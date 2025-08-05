# GMGN 트래커 - 간단 버전 🚀

GMGN.ai 웹사이트의 종목 정보를 실시간으로 추적하는 초간단 버전입니다.

## 빠른 시작 ⚡

### 1. 설치
```bash
pip install -r requirements.txt
```

### 2. 데이터 수집 (한번 실행)
```bash
python gmgn_scraper.py
```

### 3. 웹 대시보드 실행
```bash
python web_app.py
```
브라우저에서 `http://localhost:5000` 접속

### 4. 자동 모니터링 (10분마다)
```bash
python auto_monitor.py
```

## 파일 설명 📁

- `gmgn_scraper.py` - GMGN 데이터 수집 스크립트
- `web_app.py` - Flask 웹 대시보드  
- `auto_monitor.py` - 자동 모니터링 (10분마다 실행)
- `latest.json` - 최신 데이터 저장 파일

## 기능 ⭐

- ✅ GMGN trending 토큰 수집
- ✅ 급등 토큰 알림 (30% 이상)
- ✅ 웹 대시보드
- ✅ 자동 새로고침 (30초마다)
- ✅ 수동 업데이트 버튼

## 사용법 💡

1. **한번만 실행**: `python gmgn_scraper.py`
2. **웹으로 보기**: `python web_app.py` → http://localhost:5000
3. **자동 모니터링**: `python auto_monitor.py` (백그라운드에서 계속 실행)

## 다음 단계 🎯

현재는 Mock 데이터를 사용합니다. 실제 GMGN 파싱을 원하면:
1. `gmgn_scraper.py`의 파싱 로직 개선
2. Telegram 알림 추가
3. 차트 기능 추가
4. 데이터베이스 연동

이렇게 단계별로 발전시켜 나가세요! 🚀