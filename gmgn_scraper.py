#!/usr/bin/env python3
"""
GMGN 간단 스크래퍼 - MVP 버전
"""
import requests
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup

def scrape_gmgn():
    """GMGN trending 페이지에서 데이터 수집"""
    print("🚀 GMGN 데이터 수집 시작...")
    
    url = "https://gmgn.ai/?chain=sol&tab=home"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # 실제 요청은 일단 주석처리하고 Mock 데이터 사용
        # response = requests.get(url, headers=headers, timeout=10)
        # response.raise_for_status()
        
        # Mock 데이터로 시작 (실제 파싱은 나중에)
        mock_data = [
            {
                'symbol': 'PEPE',
                'name': 'Pepe Token',
                'price': 0.000012,
                'change_24h': 45.2,
                'market_cap': 5000000,
                'volume_24h': 2500000,
                'timestamp': datetime.now().isoformat()
            },
            {
                'symbol': 'DOGE',
                'name': 'Dogecoin Style', 
                'price': 0.0025,
                'change_24h': -12.5,
                'market_cap': 10000000,
                'volume_24h': 3000000,
                'timestamp': datetime.now().isoformat()
            },
            {
                'symbol': 'MOON',
                'name': 'Moon Token',
                'price': 0.15,
                'change_24h': 125.8,
                'market_cap': 25000000,
                'volume_24h': 8000000,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        print(f"✅ {len(mock_data)}개 토큰 데이터 수집 완료")
        return mock_data
        
    except Exception as e:
        print(f"❌ 스크래핑 실패: {e}")
        return []

def save_data(data):
    """데이터를 JSON 파일에 저장"""
    # 마이크로초 단위까지 포함하여 파일명 유니크하게 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]  # 밀리초까지
    filename = f"gmgn_data_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 데이터 저장 완료: {filename}")
        
        # 최신 데이터를 latest.json으로도 저장
        with open('latest.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"❌ 저장 실패: {e}")

def check_alerts(data):
    """급등 토큰 알림 확인"""
    print("\n🚨 급등 토큰 확인 중...")
    
    alerts = []
    for token in data:
        try:
            # 필수 필드가 있는지 확인 후 처리
            if 'change_24h' in token and 'symbol' in token:
                if token['change_24h'] > 30:  # 30% 이상 상승
                    alert_msg = f"🚀 급등 알림: {token['symbol']} (+{token['change_24h']:.1f}%)"
                    print(alert_msg)
                    alerts.append(alert_msg)
        except (KeyError, TypeError, ValueError) as e:
            # 잘못된 데이터는 무시하고 계속 진행
            print(f"   ⚠️ 토큰 데이터 오류 무시: {e}")
            continue
    
    if not alerts:
        print("   현재 급등하는 토큰이 없습니다.")
    
    return alerts

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("🎯 GMGN 트래커 - 간단 버전")
    print("=" * 50)
    
    # 1. 데이터 수집
    data = scrape_gmgn()
    
    if data:
        # 2. 데이터 저장
        save_data(data)
        
        # 3. 알림 확인
        alerts = check_alerts(data)
        
        # 4. 결과 출력
        print(f"\n📊 수집된 토큰: {len(data)}개")
        print(f"🚨 급등 알림: {len(alerts)}개")
        
    print("\n✅ 완료!")

if __name__ == "__main__":
    main()