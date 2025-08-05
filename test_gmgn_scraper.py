#!/usr/bin/env python3
"""
GMGN 스크래퍼 테스트 코드 - 테스트 라스트 방식
"""
import pytest
import json
import os
from datetime import datetime
from unittest.mock import patch, mock_open
import gmgn_scraper


class TestGMGNScraper:
    """GMGN 스크래퍼 테스트 클래스"""

    def test_scrape_gmgn_returns_valid_data(self):
        """스크래퍼가 유효한 데이터를 반환하는지 테스트"""
        # Given: 스크래퍼 실행
        # When: 데이터 수집
        data = gmgn_scraper.scrape_gmgn()
        
        # Then: 유효한 데이터 반환
        assert isinstance(data, list)
        assert len(data) > 0
        
        # 각 토큰 데이터 검증
        for token in data:
            assert 'symbol' in token
            assert 'name' in token
            assert 'price' in token
            assert 'change_24h' in token
            assert 'market_cap' in token
            assert 'volume_24h' in token
            assert 'timestamp' in token
            
            # 데이터 타입 검증
            assert isinstance(token['symbol'], str)
            assert isinstance(token['price'], (int, float))
            assert isinstance(token['change_24h'], (int, float))
    
    def test_scrape_gmgn_has_required_fields(self):
        """스크래퍼가 필수 필드를 포함하는지 테스트"""
        # Given: 필수 필드 정의
        required_fields = ['symbol', 'name', 'price', 'change_24h', 'market_cap', 'volume_24h', 'timestamp']
        
        # When: 데이터 수집
        data = gmgn_scraper.scrape_gmgn()
        
        # Then: 모든 필수 필드 존재
        for token in data:
            for field in required_fields:
                assert field in token, f"Missing field: {field} in token: {token}"

    def test_save_data_creates_files(self):
        """save_data 함수가 파일을 생성하는지 테스트"""
        # Given: 테스트 데이터
        test_data = [
            {
                'symbol': 'TEST',
                'name': 'Test Token',
                'price': 0.001,
                'change_24h': 10.0,
                'market_cap': 1000000,
                'volume_24h': 100000,
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        # When: 데이터 저장
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('json.dump') as mock_json_dump:
                gmgn_scraper.save_data(test_data)
                
                # Then: 파일이 생성되고 JSON이 저장됨
                assert mock_file.called
                assert mock_json_dump.called

    def test_check_alerts_identifies_pumping_tokens(self):
        """급등 토큰 식별 테스트"""
        # Given: 급등/급락 토큰 데이터
        test_data = [
            {'symbol': 'PUMP', 'change_24h': 50.0},  # 급등
            {'symbol': 'STABLE', 'change_24h': 5.0},  # 보통
            {'symbol': 'DUMP', 'change_24h': -20.0}   # 급락
        ]
        
        # When: 알림 확인
        alerts = gmgn_scraper.check_alerts(test_data)
        
        # Then: 급등 토큰만 알림
        assert len(alerts) == 1
        assert 'PUMP' in alerts[0]
        assert '50.0%' in alerts[0]

    def test_check_alerts_handles_empty_data(self):
        """빈 데이터에 대한 알림 확인 테스트"""
        # Given: 빈 데이터
        empty_data = []
        
        # When: 알림 확인
        alerts = gmgn_scraper.check_alerts(empty_data)
        
        # Then: 빈 알림 리스트
        assert isinstance(alerts, list)
        assert len(alerts) == 0

    def test_mock_data_consistency(self):
        """Mock 데이터 일관성 테스트"""
        # Given: 여러 번 실행
        # When: 데이터 수집을 여러 번 실행
        data1 = gmgn_scraper.scrape_gmgn()
        data2 = gmgn_scraper.scrape_gmgn()
        
        # Then: 동일한 구조의 데이터
        assert len(data1) == len(data2)
        
        for i in range(len(data1)):
            assert data1[i]['symbol'] == data2[i]['symbol']
            assert data1[i]['name'] == data2[i]['name']
            # 가격은 변동 가능하므로 체크하지 않음

    def test_price_ranges_are_reasonable(self):
        """가격 범위가 합리적인지 테스트"""
        # Given: 데이터 수집
        data = gmgn_scraper.scrape_gmgn()
        
        # When & Then: 가격이 합리적 범위 내
        for token in data:
            assert token['price'] > 0, f"Price should be positive: {token['price']}"
            assert token['price'] < 1000, f"Price seems too high: {token['price']}"
            assert token['market_cap'] > 0, f"Market cap should be positive: {token['market_cap']}"
            assert token['volume_24h'] >= 0, f"Volume should be non-negative: {token['volume_24h']}"

    def test_change_percentage_format(self):
        """변동률 포맷 테스트"""
        # Given: 데이터 수집
        data = gmgn_scraper.scrape_gmgn()
        
        # When & Then: 변동률이 유효한 범위
        for token in data:
            change = token['change_24h']
            assert isinstance(change, (int, float))
            assert -100 <= change <= 1000, f"Change percentage out of range: {change}%"

    @pytest.mark.integration
    def test_main_function_runs_without_error(self):
        """메인 함수가 오류 없이 실행되는지 테스트"""
        # Given: 메인 함수
        # When: 실행
        try:
            with patch('builtins.print'):  # 출력 억제
                gmgn_scraper.main()
            success = True
        except Exception as e:
            success = False
            pytest.fail(f"Main function failed: {e}")
        
        # Then: 성공적 실행
        assert success


class TestDataValidation:
    """데이터 검증 테스트"""

    def test_timestamp_format(self):
        """타임스탬프 포맷 테스트"""
        # Given: 데이터 수집
        data = gmgn_scraper.scrape_gmgn()
        
        # When & Then: 타임스탬프가 유효한 ISO 포맷
        for token in data:
            timestamp_str = token['timestamp']
            try:
                datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                valid_format = True
            except ValueError:
                valid_format = False
            
            assert valid_format, f"Invalid timestamp format: {timestamp_str}"

    def test_symbol_format(self):
        """심볼 포맷 테스트"""
        # Given: 데이터 수집
        data = gmgn_scraper.scrape_gmgn()
        
        # When & Then: 심볼이 대문자이고 유효한 길이
        for token in data:
            symbol = token['symbol']
            assert isinstance(symbol, str)
            assert len(symbol) >= 2, f"Symbol too short: {symbol}"
            assert len(symbol) <= 10, f"Symbol too long: {symbol}"
            assert symbol.isupper(), f"Symbol should be uppercase: {symbol}"


if __name__ == "__main__":
    # 개별 테스트 실행을 위한 코드
    pytest.main([__file__, "-v"])