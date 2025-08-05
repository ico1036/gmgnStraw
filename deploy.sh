#!/bin/bash

# GMGN 크롤러 배포 스크립트

echo "🚀 GMGN 크롤러 배포 시작..."

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}📍 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 배포 방법 선택
echo "배포 방법을 선택하세요:"
echo "1) 🐳 Docker로 로컬 배포"
echo "2) ☁️  클라우드 배포 안내"
echo "3) 🖥️  로컬 서버 배포"
read -p "선택 (1-3): " choice

case $choice in
    1)
        print_step "Docker 배포 시작..."
        
        # Docker 설치 확인
        if ! command -v docker &> /dev/null; then
            print_error "Docker가 설치되지 않았습니다. Docker를 설치해주세요."
            exit 1
        fi
        
        # Docker Compose 설치 확인
        if ! command -v docker-compose &> /dev/null; then
            print_error "Docker Compose가 설치되지 않았습니다."
            exit 1
        fi
        
        # 기존 컨테이너 정리
        print_step "기존 컨테이너 정리 중..."
        docker-compose down 2>/dev/null || true
        
        # 이미지 빌드
        print_step "Docker 이미지 빌드 중..."
        docker-compose build
        
        # 컨테이너 실행
        print_step "컨테이너 실행 중..."
        docker-compose up -d
        
        print_success "배포 완료!"
        echo "📍 웹 대시보드: http://localhost:5000"
        echo "📊 컨테이너 상태 확인: docker-compose ps"
        echo "📝 로그 확인: docker-compose logs -f"
        ;;
        
    2)
        print_step "클라우드 배포 옵션들:"
        echo ""
        echo "🌟 무료 옵션:"
        echo "1. Render.com - render.yaml 파일 사용"
        echo "   • GitHub 저장소 연결"
        echo "   • 자동 배포 설정"
        echo ""
        echo "2. Railway.app"
        echo "   • GitHub 연결"
        echo "   • 쉬운 설정"
        echo ""
        echo "3. Google Cloud Run"
        echo "   • Docker 이미지 업로드"
        echo "   • 서버리스 실행"
        echo ""
        echo "📖 상세 가이드는 README.md를 참조하세요."
        ;;
        
    3)
        print_step "로컬 서버 배포 시작..."
        
        # 가상환경 활성화 확인
        if [[ "$VIRTUAL_ENV" == "" ]]; then
            print_step "가상환경 활성화 중..."
            source .venv/bin/activate 2>/dev/null || {
                print_error "가상환경을 찾을 수 없습니다. 'python -m venv .venv'로 생성하세요."
                exit 1
            }
        fi
        
        # 의존성 설치
        print_step "의존성 설치 중..."
        pip install -r requirements.txt
        
        # 데이터 디렉토리 생성
        mkdir -p data logs
        
        # 백그라운드에서 실행
        print_step "백그라운드에서 웹 서버 시작..."
        nohup python web_app.py > logs/web_app.log 2>&1 &
        WEB_PID=$!
        
        print_step "백그라운드에서 모니터링 시작..."
        nohup python auto_monitor.py > logs/monitor.log 2>&1 &
        MONITOR_PID=$!
        
        # PID 저장
        echo $WEB_PID > .web_pid
        echo $MONITOR_PID > .monitor_pid
        
        print_success "로컬 서버 배포 완료!"
        echo "📍 웹 대시보드: http://localhost:5000+"
        echo "🔍 웹 로그: tail -f logs/web_app.log"
        echo "🔍 모니터 로그: tail -f logs/monitor.log"
        echo "⏹️  중지하려면: ./stop.sh"
        ;;
        
    *)
        print_error "잘못된 선택입니다."
        exit 1
        ;;
esac