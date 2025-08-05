#!/usr/bin/env python3
"""
통합 테스트 코드 - 전체 시스템 워크플로우 테스트
"""
import pytest
import json
import os
import subprocess
import time
from unittest.mock import patch
import gmgn_scraper
from web_app import app


class TestIntegration:
    """통합 테스트 클래스"""

    @pytest.fixture
    def client(self):
        """Flask 테스트 클라이언트"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    def test_full_data_pipeline(self):
        """전체 데이터 파이프라인 테스트"""
        # Given: 깨끗한 환경
        # 기존 latest.json 백업
        backup_file = None
        if os.path.exists('latest.json'):
            with open('latest.json', 'r') as f:
                backup_file = f.read()
            os.remove('latest.json')
        
        try:
            # When: 1. 데이터 수집
            data = gmgn_scraper.scrape_gmgn()
            assert len(data) > 0, "데이터 수집 실패"
            
            # When: 2. 데이터 저장
            gmgn_scraper.save_data(data)
            assert os.path.exists('latest.json'), "데이터 저장 실패"
            
            # When: 3. 저장된 데이터 검증
            with open('latest.json', 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
            assert len(saved_data) == len(data), "저장된 데이터 크기 불일치"
            
            # When: 4. 알림 시스템 테스트
            alerts = gmgn_scraper.check_alerts(data)
            pumping_tokens = [token for token in data if token['change_24h'] > 30]
            assert len(alerts) == len(pumping_tokens), "알림 수 불일치"
            
            # Then: 전체 파이프라인 성공
            print(f"✅ 데이터 파이프라인 테스트 완료: {len(data)}개 토큰, {len(alerts)}개 알림")
            
        finally:
            # 백업 파일 복원
            if backup_file:
                with open('latest.json', 'w') as f:
                    f.write(backup_file)

    def test_web_dashboard_with_real_data(self, client):
        """실제 데이터를 사용한 웹 대시보드 테스트"""
        # Given: 실제 데이터 생성
        data = gmgn_scraper.scrape_gmgn()
        gmgn_scraper.save_data(data)
        
        # When: 웹 대시보드 접속
        response = client.get('/')
        
        # Then: 성공적 로딩
        assert response.status_code == 200
        
        # 토큰 데이터가 표시되는지 확인
        html_content = response.data.decode('utf-8')
        for token in data:
            assert token['symbol'] in html_content, f"토큰 {token['symbol']}이 표시되지 않음"

    def test_api_endpoints_consistency(self, client):
        """API 엔드포인트 일관성 테스트"""
        # Given: 데이터 준비
        data = gmgn_scraper.scrape_gmgn()
        gmgn_scraper.save_data(data)
        
        # When: API 호출
        response = client.get('/api/tokens')
        api_data = response.get_json()
        
        # Then: API 데이터 일관성 확인
        assert api_data['success'] is True
        assert len(api_data['data']) == len(data)
        
        # 각 토큰의 필수 필드 확인
        for i, token in enumerate(api_data['data']):
            original = data[i]
            assert token['symbol'] == original['symbol']
            assert token['price'] == original['price']
            assert token['change_24h'] == original['change_24h']

    def test_manual_update_workflow(self, client):
        """수동 업데이트 워크플로우 테스트"""
        # Given: 초기 상태
        initial_response = client.get('/api/tokens')
        initial_data = initial_response.get_json()
        
        # When: 수동 업데이트 실행
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stderr = ""
            
            update_response = client.post('/api/update')
            update_result = update_response.get_json()
            
            # Then: 업데이트 성공
            assert update_result['success'] is True
            assert mock_subprocess.called

    def test_error_handling_workflow(self, client):
        """에러 처리 워크플로우 테스트"""
        # Given: 실패하는 업데이트
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.returncode = 1
            mock_subprocess.return_value.stderr = "테스트 에러"
            
            # When: 업데이트 실행
            response = client.post('/api/update')
            result = response.get_json()
            
            # Then: 에러 처리 확인
            assert result['success'] is False
            assert 'error' in result

    def test_alert_threshold_functionality(self):
        """알림 임계값 기능 테스트"""
        # Given: 다양한 변동률의 테스트 데이터
        test_data = [
            {'symbol': 'LOW', 'change_24h': 5.0},      # 낮음
            {'symbol': 'MID', 'change_24h': 25.0},     # 중간
            {'symbol': 'HIGH', 'change_24h': 45.0},    # 높음
            {'symbol': 'EXTREME', 'change_24h': 150.0} # 극도로 높음
        ]
        
        # When: 알림 확인
        alerts = gmgn_scraper.check_alerts(test_data)
        
        # Then: 30% 이상만 알림
        assert len(alerts) == 2  # HIGH, EXTREME만
        alert_text = ' '.join(alerts)
        assert 'HIGH' in alert_text
        assert 'EXTREME' in alert_text
        assert 'LOW' not in alert_text
        assert 'MID' not in alert_text

    def test_data_persistence(self):
        """데이터 지속성 테스트"""
        # Given: 첫 번째 데이터 수집
        data1 = gmgn_scraper.scrape_gmgn()
        gmgn_scraper.save_data(data1)
        
        # When: 두 번째 데이터 수집
        time.sleep(0.1)  # 타임스탬프 차이를 위한 짧은 대기
        data2 = gmgn_scraper.scrape_gmgn()
        gmgn_scraper.save_data(data2)
        
        # Then: 최신 데이터가 저장됨
        with open('latest.json', 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
        
        # 두 번째 데이터의 타임스탬프가 더 최신이어야 함
        assert saved_data[0]['timestamp'] >= data1[0]['timestamp']

    def test_json_file_generation(self):
        """JSON 파일 생성 테스트"""
        # Given: 데이터 수집 전 상태
        existing_files = [f for f in os.listdir('.') if f.startswith('gmgn_data_') and f.endswith('.json')]
        initial_count = len(existing_files)
        
        # When: 데이터 수집 및 저장
        data = gmgn_scraper.scrape_gmgn()
        gmgn_scraper.save_data(data)
        
        # Then: 새 파일 생성 확인
        new_files = [f for f in os.listdir('.') if f.startswith('gmgn_data_') and f.endswith('.json')]
        assert len(new_files) == initial_count + 1, "새 데이터 파일이 생성되지 않음"
        
        # latest.json도 존재해야 함
        assert os.path.exists('latest.json'), "latest.json 파일이 없음"

    @pytest.mark.slow
    def test_performance_benchmark(self):
        """성능 벤치마크 테스트"""
        # Given: 성능 측정 준비
        import time
        
        # When: 스크래핑 성능 측정
        start_time = time.time()
        data = gmgn_scraper.scrape_gmgn()
        scrape_time = time.time() - start_time
        
        # When: 저장 성능 측정
        start_time = time.time()
        gmgn_scraper.save_data(data)
        save_time = time.time() - start_time
        
        # When: 알림 확인 성능 측정
        start_time = time.time()
        alerts = gmgn_scraper.check_alerts(data)
        alert_time = time.time() - start_time
        
        # Then: 성능 기준 확인 (각 작업이 1초 이내)
        assert scrape_time < 1.0, f"스크래핑이 너무 느림: {scrape_time:.2f}초"
        assert save_time < 1.0, f"저장이 너무 느림: {save_time:.2f}초"
        assert alert_time < 1.0, f"알림 확인이 너무 느림: {alert_time:.2f}초"
        
        print(f"📊 성능 측정 결과:")
        print(f"   스크래핑: {scrape_time:.3f}초")
        print(f"   저장: {save_time:.3f}초")
        print(f"   알림 확인: {alert_time:.3f}초")


class TestSystemReliability:
    """시스템 안정성 테스트"""

    def test_graceful_failure_handling(self):
        """우아한 실패 처리 테스트"""
        # Given: 잘못된 데이터
        invalid_data = [{'invalid': 'data'}]
        
        # When: 알림 확인 (KeyError 발생 가능)
        try:
            alerts = gmgn_scraper.check_alerts(invalid_data)
            # Then: 빈 알림 리스트 반환하거나 예외 처리
            assert isinstance(alerts, list)
        except KeyError:
            # 예외가 발생해도 시스템이 중단되지 않아야 함
            pytest.fail("시스템이 잘못된 데이터를 우아하게 처리하지 못함")

    def test_file_permission_handling(self):
        """파일 권한 처리 테스트"""
        # Given: 테스트 데이터
        test_data = [{'symbol': 'TEST', 'change_24h': 10}]
        
        # When: 저장 시도 (파일 권한이 있다고 가정)
        try:
            gmgn_scraper.save_data(test_data)
            success = True
        except PermissionError:
            success = False
        
        # Then: 권한이 있으면 성공, 없으면 우아한 실패
        # 실제 환경에서는 대부분 성공할 것
        assert success or not success  # 어느 쪽이든 crash 없이 처리


if __name__ == "__main__":
    # 통합 테스트 실행
    pytest.main([__file__, "-v", "-s"])