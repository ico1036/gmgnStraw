#!/usr/bin/env python3
"""
간단한 웹 대시보드 - Flask 기반
"""
import json
import os
import socket
import subprocess
import signal
from datetime import datetime
from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

def cleanup_old_processes():
    """기존 웹앱 프로세스 정리"""
    try:
        # 기존 Flask/web_app 프로세스 찾기
        result = subprocess.run(['pgrep', '-f', 'web_app.py'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip() and pid != str(os.getpid()):
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"🔄 기존 프로세스 {pid} 종료됨")
                    except (ProcessLookupError, ValueError):
                        pass
    except Exception:
        pass  # 무시

def find_free_port(start_port=5000, end_port=5100):
    """사용 가능한 포트를 찾는 함수"""
    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"포트 {start_port}-{end_port} 범위에서 사용 가능한 포트를 찾을 수 없습니다.")

# HTML 템플릿
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GMGN 트래커 - 간단 버전</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .tokens-table {
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
        }
        td {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        .positive {
            color: #28a745;
            font-weight: bold;
        }
        .negative {
            color: #dc3545;
            font-weight: bold;
        }
        .refresh-btn {
            background: #28a745;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 0;
        }
        .refresh-btn:hover {
            background: #218838;
        }
        .alert-section {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 GMGN 트래커</h1>
            <p>실시간 암호화폐 모니터링 (간단 버전)</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{{ total_tokens }}</div>
                <div>총 토큰 수</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ pumping_count }}</div>
                <div>급등 토큰</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ last_update }}</div>
                <div>마지막 업데이트</div>
            </div>
        </div>

        {% if alerts %}
        <div class="alert-section">
            <h3>🚨 급등 알림</h3>
            {% for alert in alerts %}
            <div>{{ alert }}</div>
            {% endfor %}
        </div>
        {% endif %}

        <button class="refresh-btn" onclick="location.reload()">🔄 새로고침</button>
        <button class="refresh-btn" onclick="manualUpdate()" style="background: #007bff;">📥 수동 수집</button>

        <div class="tokens-table">
            <table>
                <thead>
                    <tr>
                        <th>토큰</th>
                        <th>가격 (USD)</th>
                        <th>24시간 변동</th>
                        <th>시가총액</th>
                        <th>거래량</th>
                    </tr>
                </thead>
                <tbody>
                    {% for token in tokens %}
                    <tr>
                        <td>
                            <strong>{{ token['symbol'] }}</strong><br>
                            <small style="color: #666;">{{ token['name'] }}</small>
                        </td>
                        <td>${{ "%.6f"|format(token['price'] or 0) }}</td>
                        <td class="{% if token['change_24h'] > 0 %}positive{% else %}negative{% endif %}">
                            {{ "{:+.1f}".format(token['change_24h'] or 0) }}%
                        </td>
                        <td>${{ "{:,.0f}".format(token['market_cap'] or 0) }}</td>
                        <td>${{ "{:,.0f}".format(token['volume_24h'] or 0) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function manualUpdate() {
            try {
                const response = await fetch('/api/update', { method: 'POST' });
                const result = await response.json();
                
                if (result.success) {
                    alert('데이터 업데이트 완료!');
                    location.reload();
                } else {
                    alert('업데이트 실패: ' + result.error);
                }
            } catch (error) {
                alert('업데이트 실패: ' + error.message);
            }
        }
        
        // 30초마다 자동 새로고침
        setInterval(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
"""

def load_latest_data():
    """최신 데이터 로드"""
    try:
        if os.path.exists('latest.json'):
            with open('latest.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"데이터 로드 실패: {e}")
    
    return []

def get_alerts(tokens):
    """급등 알림 생성"""
    alerts = []
    for token in tokens:
        if token['change_24h'] > 30:
            alerts.append(f"🚀 {token['symbol']}: +{token['change_24h']:.1f}%")
    return alerts

@app.route('/')
def dashboard():
    """메인 대시보드"""
    tokens = load_latest_data()
    alerts = get_alerts(tokens)
    pumping_count = len([t for t in tokens if t['change_24h'] > 20])
    
    last_update = "방금 전"
    if tokens:
        try:
            last_timestamp = datetime.fromisoformat(tokens[0]['timestamp'].replace('Z', '+00:00'))
            last_update = last_timestamp.strftime('%H:%M:%S')
        except:
            pass
    
    return render_template_string(DASHBOARD_TEMPLATE, 
                                  tokens=tokens,
                                  alerts=alerts,
                                  total_tokens=len(tokens),
                                  pumping_count=pumping_count,
                                  last_update=last_update)

@app.route('/api/tokens')
def api_tokens():
    """토큰 데이터 API"""
    tokens = load_latest_data()
    return jsonify({
        'success': True,
        'data': tokens,
        'count': len(tokens)
    })

@app.route('/api/update', methods=['POST'])
def api_update():
    """수동 업데이트 API"""
    try:
        import subprocess
        result = subprocess.run(['python', 'gmgn_scraper.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            return jsonify({'success': True, 'message': '업데이트 완료'})
        else:
            return jsonify({'success': False, 'error': result.stderr})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    try:
        print("🌐 웹 서버 시작...")
        
        # 기존 프로세스 정리
        cleanup_old_processes()
        
        # 사용 가능한 포트 찾기
        port = find_free_port()
        print(f"📍 주소: http://localhost:{port}")
        print(f"✅ 포트 {port}에서 서버가 시작됩니다.")
        print("🔄 브라우저가 자동으로 열리지 않으면 위 주소를 복사해서 접속하세요.")
        
        # Flask 서버 시작
        app.run(debug=True, host='0.0.0.0', port=port)
        
    except RuntimeError as e:
        print(f"❌ 오류: {e}")
        print("💡 시스템을 재시작하거나 다른 애플리케이션을 종료해보세요.")
    except KeyboardInterrupt:
        print("\n👋 웹 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")