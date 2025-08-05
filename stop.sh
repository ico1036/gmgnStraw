#!/bin/bash

# GMGN 크롤러 중지 스크립트

echo "🛑 GMGN 크롤러 중지..."

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

# Docker 컨테이너 중지
print_step "Docker 컨테이너 확인 및 중지..."
if command -v docker-compose &> /dev/null; then
    docker-compose down 2>/dev/null && print_success "Docker 컨테이너 중지됨"
fi

# 로컬 프로세스 중지
if [ -f .web_pid ]; then
    WEB_PID=$(cat .web_pid)
    if kill -0 $WEB_PID 2>/dev/null; then
        print_step "웹 서버 중지 중... (PID: $WEB_PID)"
        kill $WEB_PID
        print_success "웹 서버 중지됨"
    fi
    rm -f .web_pid
fi

if [ -f .monitor_pid ]; then
    MONITOR_PID=$(cat .monitor_pid)
    if kill -0 $MONITOR_PID 2>/dev/null; then
        print_step "모니터링 중지 중... (PID: $MONITOR_PID)"
        kill $MONITOR_PID
        print_success "모니터링 중지됨"
    fi
    rm -f .monitor_pid
fi

# 남은 프로세스 강제 종료
print_step "남은 프로세스 정리..."
pkill -f "web_app.py" 2>/dev/null
pkill -f "auto_monitor.py" 2>/dev/null

print_success "모든 프로세스가 중지되었습니다!"