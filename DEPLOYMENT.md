# 🚀 GMGN 크롤러 배포 가이드

## 빠른 배포

### 1️⃣ 자동 배포 스크립트 사용
```bash
./deploy.sh
```

### 2️⃣ 중지
```bash
./stop.sh
```

## 배포 옵션들

### 🐳 Docker 배포 (권장)

#### 단일 컨테이너
```bash
# 이미지 빌드
docker build -t gmgn-crawler .

# 컨테이너 실행
docker run -d \
  --name gmgn-crawler \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  gmgn-crawler
```

#### Docker Compose (전체 시스템)
```bash
# 백그라운드에서 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### ☁️ 클라우드 배포

#### Render.com (무료)
1. [Render.com](https://render.com) 계정 생성
2. GitHub 저장소 연결
3. `render.yaml` 자동 감지
4. 배포 시작

#### Railway.app
1. [Railway.app](https://railway.app) 계정 생성
2. GitHub 저장소 연결
3. 자동 감지 및 배포

#### Google Cloud Run
```bash
# 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/PROJECT_ID/gmgn-crawler

# 배포
gcloud run deploy --image gcr.io/PROJECT_ID/gmgn-crawler --platform managed
```

### 🖥️ VPS/서버 배포

#### Ubuntu/Debian 서버
```bash
# 1. 저장소 클론
git clone https://github.com/ico1036/gmgnStraw.git
cd gmgnStraw

# 2. Python 가상환경 설정
python3 -m venv .venv
source .venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 서비스 파일 생성 (systemd)
sudo nano /etc/systemd/system/gmgn-crawler.service
```

#### systemd 서비스 파일
```ini
[Unit]
Description=GMGN Crawler Web App
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/gmgnStraw
Environment=PATH=/path/to/gmgnStraw/.venv/bin
ExecStart=/path/to/gmgnStraw/.venv/bin/python web_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 서비스 시작
```bash
sudo systemctl daemon-reload
sudo systemctl enable gmgn-crawler
sudo systemctl start gmgn-crawler
sudo systemctl status gmgn-crawler
```

## 환경 변수 설정

### 필요한 환경 변수
```bash
# .env 파일 생성
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
MONITOR_INTERVAL=600  # 10분 = 600초
```

### Docker에서 환경 변수 사용
```bash
docker run -d \
  --env-file .env \
  -p 5000:5000 \
  gmgn-crawler
```

## 모니터링 및 로그

### Docker 로그 확인
```bash
docker logs gmgn-crawler
docker-compose logs -f
```

### 서버 로그 확인
```bash
tail -f logs/web_app.log
tail -f logs/monitor.log
```

### 헬스체크
```bash
curl http://localhost:5000/
curl http://localhost:5000/api/tokens
```

## 백업 및 복원

### 데이터 백업
```bash
# Docker 볼륨 백업
docker run --rm -v gmgn_data:/data -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz /data

# 로컬 파일 백업
tar czf backup_$(date +%Y%m%d).tar.gz *.json logs/
```

### 복원
```bash
# Docker 볼륨 복원
docker run --rm -v gmgn_data:/data -v $(pwd):/backup ubuntu bash -c "cd /data && tar xzf /backup/backup.tar.gz --strip 1"
```

## 트러블슈팅

### 포트 충돌
- 자동 포트 탐지 기능 내장 (5000-5100 범위)
- 환경 변수 `PORT`로 수동 설정 가능

### 메모리 부족
```bash
# Docker 메모리 제한 설정
docker run -d --memory="512m" gmgn-crawler
```

### 네트워크 문제
```bash
# 네트워크 연결 확인
curl -I https://gmgn.ai
```

## 성능 최적화

### Gunicorn 사용 (프로덕션)
```bash
# requirements.txt에 추가
gunicorn==21.2.0

# 실행
gunicorn --bind 0.0.0.0:5000 --workers 4 web_app:app
```

### Nginx 리버스 프록시
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 보안 고려사항

1. **환경 변수로 민감한 정보 관리**
2. **HTTPS 인증서 설정**
3. **방화벽 설정**
4. **정기적인 보안 업데이트**

---

**📞 지원이 필요하시면 GitHub Issues를 통해 문의해주세요!**