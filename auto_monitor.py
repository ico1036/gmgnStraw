#!/usr/bin/env python3
"""
자동 모니터링 스크립트 - 주기적으로 실행
"""
import time
import schedule
import subprocess
import sys
from datetime import datetime

def run_scraper():
    """스크래퍼 실행"""
    print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 자동 수집 시작")
    
    try:
        result = subprocess.run([sys.executable, 'gmgn_scraper.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 자동 수집 완료")
        else:
            print(f"❌ 수집 실패: {result.stderr}")
            
    except Exception as e:
        print(f"❌ 실행 오류: {e}")

def main():
    """메인 실행 함수"""
    print("🤖 GMGN 자동 모니터링 시작")
    print("📅 스케줄: 10분마다 실행")
    print("⚠️  종료하려면 Ctrl+C를 누르세요")
    print("=" * 50)
    
    # 10분마다 실행 스케줄 설정
    schedule.every(10).minutes.do(run_scraper)
    
    # 시작시 한 번 실행
    run_scraper()
    
    # 스케줄 실행
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 모니터링 종료")

if __name__ == "__main__":
    main()