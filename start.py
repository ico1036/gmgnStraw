#!/usr/bin/env python3
"""
GMGN 트래커 간단 시작 스크립트
"""
import os
import sys
import time
import subprocess

def show_menu():
    """메뉴 표시"""
    print("=" * 50)
    print("🚀 GMGN 트래커 - 간단 버전")
    print("=" * 50)
    print("1. 📥 한번만 데이터 수집")
    print("2. 🌐 웹 대시보드 시작")
    print("3. 🤖 자동 모니터링 시작 (10분마다)")
    print("4. 📄 파일 목록 보기")
    print("5. ❌ 종료")
    print("=" * 50)

def run_scraper():
    """스크래퍼 실행"""
    print("📥 데이터 수집 중...")
    subprocess.run([sys.executable, 'gmgn_scraper.py'])

def start_web():
    """웹 서버 시작"""
    print("🌐 웹 서버 시작...")
    print("📍 사용 가능한 포트를 자동으로 찾는 중...")
    subprocess.run([sys.executable, 'web_app.py'])

def start_monitor():
    """자동 모니터링 시작"""
    print("🤖 자동 모니터링 시작...")
    subprocess.run([sys.executable, 'auto_monitor.py'])

def show_files():
    """파일 목록 표시"""
    print("\n📄 생성된 파일들:")
    files = [f for f in os.listdir('.') if f.endswith('.json')]
    for file in files:
        size = os.path.getsize(file)
        print(f"  📄 {file} ({size} bytes)")
    
    if not files:
        print("  아직 데이터 파일이 없습니다.")
        print("  먼저 '1. 데이터 수집'을 실행해보세요.")
    print()

def main():
    """메인 함수"""
    while True:
        show_menu()
        
        try:
            choice = input("선택하세요 (1-5): ").strip()
            
            if choice == '1':
                run_scraper()
            elif choice == '2':
                start_web()
            elif choice == '3':
                start_monitor()
            elif choice == '4':
                show_files()
            elif choice == '5':
                print("👋 프로그램을 종료합니다.")
                break
            else:
                print("❌ 잘못된 선택입니다. 1-5 사이의 숫자를 입력하세요.")
                
        except KeyboardInterrupt:
            print("\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
        
        input("\n⏸️  계속하려면 Enter를 누르세요...")

if __name__ == "__main__":
    main()