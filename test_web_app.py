#!/usr/bin/env python3
"""
웹 앱 테스트 코드 - 테스트 라스트 방식
"""
import pytest
import json
import os
from unittest.mock import patch, mock_open
from web_app import app


class TestWebApp:
    """웹 앱 테스트 클래스"""

    @pytest.fixture
    def client(self):
        """Flask 테스트 클라이언트"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client

    @pytest.fixture
    def sample_data(self):
        """테스트용 샘플 데이터"""
        return [
            {
                'symbol': 'TEST1',
                'name': 'Test Token 1',
                'price': 0.001,
                'change_24h': 45.0,
                'market_cap': 1000000,
                'volume_24h': 500000,
                'timestamp': '2024-01-01T12:00:00'
            },
            {
                'symbol': 'TEST2',
                'name': 'Test Token 2',
                'price': 0.002,
                'change_24h': -15.0,
                'market_cap': 2000000,
                'volume_24h': 750000,
                'timestamp': '2024-01-01T12:00:00'
            }
        ]

    def test_dashboard_loads_successfully(self, client):
        """대시보드 페이지가 성공적으로 로드되는지 테스트"""
        # Given: 웹 클라이언트
        # When: 메인 페이지 요청
        response = client.get('/')
        
        # Then: 성공적 응답
        assert response.status_code == 200
        assert b'GMGN' in response.data
        # 한글 '트래커'가 포함되어 있는지 확인
        html_text = response.data.decode('utf-8')
        assert '트래커' in html_text or 'tracker' in html_text.lower()

    def test_api_tokens_endpoint(self, client, sample_data):
        """토큰 API 엔드포인트 테스트"""
        # Given: 샘플 데이터가 있는 상황
        with patch('web_app.load_latest_data', return_value=sample_data):
            # When: API 호출
            response = client.get('/api/tokens')
            
            # Then: 올바른 JSON 응답
            assert response.status_code == 200
            assert response.is_json
            
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert len(data['data']) == 2

    def test_api_update_endpoint(self, client):
        """수동 업데이트 API 테스트"""
        # Given: 업데이트 엔드포인트
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            mock_subprocess.return_value.stderr = ""
            
            # When: POST 요청
            response = client.post('/api/update')
            
            # Then: 성공 응답
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True

    def test_load_latest_data_with_existing_file(self, sample_data):
        """기존 파일이 있을 때 데이터 로드 테스트"""
        # Given: latest.json 파일이 존재
        mock_file_content = json.dumps(sample_data)
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=mock_file_content)):
                from web_app import load_latest_data
                
                # When: 데이터 로드
                result = load_latest_data()
                
                # Then: 올바른 데이터 반환
                assert len(result) == 2
                assert result[0]['symbol'] == 'TEST1'

    def test_load_latest_data_with_no_file(self):
        """파일이 없을 때 데이터 로드 테스트"""
        # Given: latest.json 파일이 없음
        with patch('os.path.exists', return_value=False):
            from web_app import load_latest_data
            
            # When: 데이터 로드
            result = load_latest_data()
            
            # Then: 빈 리스트 반환
            assert result == []

    def test_get_alerts_identifies_pumping_tokens(self, sample_data):
        """급등 토큰 식별 테스트"""
        # Given: 급등 토큰이 포함된 데이터
        from web_app import get_alerts
        
        # When: 알림 확인
        alerts = get_alerts(sample_data)
        
        # Then: 급등 토큰 알림 생성
        assert len(alerts) == 1  # TEST1만 30% 이상 상승
        assert 'TEST1' in alerts[0]
        assert '45.0%' in alerts[0]

    def test_dashboard_displays_token_count(self, client, sample_data):
        """대시보드에 토큰 수가 표시되는지 테스트"""
        # Given: 샘플 데이터
        with patch('web_app.load_latest_data', return_value=sample_data):
            # When: 대시보드 요청
            response = client.get('/')
            
            # Then: 토큰 수 표시
            assert response.status_code == 200
            assert b'2' in response.data  # 토큰 수

    def test_dashboard_handles_empty_data(self, client):
        """빈 데이터에 대한 대시보드 처리 테스트"""
        # Given: 빈 데이터
        with patch('web_app.load_latest_data', return_value=[]):
            # When: 대시보드 요청
            response = client.get('/')
            
            # Then: 오류 없이 표시
            assert response.status_code == 200

    def test_api_tokens_handles_empty_data(self, client):
        """빈 데이터에 대한 API 처리 테스트"""
        # Given: 빈 데이터
        with patch('web_app.load_latest_data', return_value=[]):
            # When: API 호출
            response = client.get('/api/tokens')
            
            # Then: 올바른 응답
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert data['count'] == 0

    def test_api_update_handles_failure(self, client):
        """업데이트 실패 처리 테스트"""
        # Given: 실패하는 서브프로세스
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.returncode = 1
            mock_subprocess.return_value.stderr = "Error message"
            
            # When: 업데이트 요청
            response = client.post('/api/update')
            
            # Then: 실패 응답
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is False
            assert 'error' in data

    def test_price_formatting_in_response(self, client, sample_data):
        """API 응답에서 가격 포맷 테스트"""
        # Given: 샘플 데이터
        with patch('web_app.load_latest_data', return_value=sample_data):
            # When: API 호출
            response = client.get('/api/tokens')
            
            # Then: 가격이 숫자 형태로 반환
            data = response.get_json()
            for token in data['data']:
                assert isinstance(token['price'], (int, float))
                assert token['price'] > 0

    def test_change_percentage_in_response(self, client, sample_data):
        """변동률 응답 테스트"""
        # Given: 샘플 데이터
        with patch('web_app.load_latest_data', return_value=sample_data):
            # When: API 호출
            response = client.get('/api/tokens')
            
            # Then: 변동률이 올바른 형태
            data = response.get_json()
            for token in data['data']:
                assert isinstance(token['change_24h'], (int, float))

    @pytest.mark.integration
    def test_full_dashboard_workflow(self, client):
        """전체 대시보드 워크플로우 테스트"""
        # Given: 전체 시스템
        # When: 대시보드 접속 → API 호출 → 업데이트
        
        # 1. 대시보드 접속
        response1 = client.get('/')
        assert response1.status_code == 200
        
        # 2. API 호출
        response2 = client.get('/api/tokens')
        assert response2.status_code == 200
        
        # 3. 업데이트 시도 (실제 실행은 mock)
        with patch('subprocess.run') as mock_subprocess:
            mock_subprocess.return_value.returncode = 0
            response3 = client.post('/api/update')
            assert response3.status_code == 200


if __name__ == "__main__":
    # 개별 테스트 실행
    pytest.main([__file__, "-v"])