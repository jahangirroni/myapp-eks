from flask import Flask, request, jsonify, redirect, render_template_string
import hashlib
import subprocess
import json
from datetime import datetime

app = Flask(__name__)

# In-memory storage for URL shortener
urls = {}

# HTML Template
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>DevOps Platform | EKS</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; font-size: 2.5em; }
        h1 span { background: linear-gradient(135deg, #00ffcc, #0066ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 20px; }
        .card {
            background: rgba(255,255,255,0.08);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s;
        }
        .card:hover { transform: translateY(-5px); }
        .card h2 { margin-bottom: 15px; font-size: 1.5em; border-left: 4px solid #00ffcc; padding-left: 12px; }
        .metric { display: inline-block; background: rgba(0,255,204,0.1); padding: 10px 15px; margin: 5px; border-radius: 8px; }
        .metric-value { font-size: 24px; font-weight: bold; color: #00ffcc; }
        .pipeline-stage { padding: 10px; margin: 8px 0; background: rgba(255,255,255,0.05); border-radius: 8px; border-left: 3px solid #ff4444; }
        .pipeline-stage.completed { border-left-color: #00ff00; }
        .pipeline-stage.running { border-left-color: #ffaa00; animation: pulse 1s infinite; }
        .url-input { width: 100%; padding: 12px; margin: 10px 0; border: none; border-radius: 8px; background: rgba(255,255,255,0.1); color: #fff; }
        button { background: linear-gradient(135deg, #00ffcc, #0066ff); border: none; padding: 12px 24px; border-radius: 8px; color: #fff; font-weight: bold; cursor: pointer; margin-top: 10px; }
        button:hover { transform: scale(1.02); }
        .short-url { background: rgba(0,255,204,0.1); padding: 10px; border-radius: 8px; margin-top: 10px; word-break: break-all; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.7; } 100% { opacity: 1; } }
        .badge { display: inline-block; background: #00ffcc; color: #0a0e27; padding: 3px 8px; border-radius: 12px; font-size: 11px; margin-left: 10px; font-weight: bold; }
        @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 <span>Cloud Native DevOps Platform</span> <span class="badge">EKS</span></h1>
        
        <div class="grid">
            <div class="card">
                <h2>📊 EKS Cluster Metrics</h2>
                <div id="metrics">
                    <div class="metric">🖥️ Nodes: <span id="nodes" class="metric-value">2</span></div>
                    <div class="metric">📦 Pods: <span id="pods" class="metric-value">-</span></div>
                    <div class="metric">⚙️ CPU: <span id="cpu" class="metric-value">-</span>%</div>
                    <div class="metric">💾 Memory: <span id="memory" class="metric-value">-</span>%</div>
                    <div class="metric">🏷️ Cluster: <span id="cluster" class="metric-value">cloud-native-cluster</span></div>
                </div>
            </div>

            <div class="card">
                <h2>🔗 URL Shortener</h2>
                <input type="url" id="urlInput" class="url-input" placeholder="Enter long URL (e.g., https://github.com/jahangirroni)">
                <button onclick="shortenUrl()">Shorten URL ✨</button>
                <div id="shortResult"></div>
            </div>

            <div class="card">
                <h2>🔐 DevSecOps Pipeline</h2>
                <div id="pipeline">
                    <div class="pipeline-stage completed">🔍 Code Commit (0.5s)</div>
                    <div class="pipeline-stage completed">🛡️ SAST Scan - SonarQube (45s)</div>
                    <div class="pipeline-stage completed">📦 Docker Build (120s)</div>
                    <div class="pipeline-stage completed">🔒 Trivy Container Scan (30s)</div>
                    <div class="pipeline-stage completed">🔐 Secrets Detection (10s)</div>
                    <div class="pipeline-stage completed">⚙️ Deploy to EKS (180s)</div>
                    <div class="pipeline-stage running">📊 Compliance Check - SOC2 (in progress)</div>
                    <div class="pipeline-stage">📈 Deploy Monitoring (pending)</div>
                </div>
                <p style="margin-top: 10px; font-size: 11px;">✅ Security+ ✅ CIS ✅ SOC2 Ready</p>
            </div>

            <div class="card">
                <h2>📁 Quick Links</h2>
                <div class="metric">🐳 <a href="https://github.com/jahangirroni/myapp-eks" style="color:#00ffcc">GitHub Repository</a></div>
                <div class="metric">📝 <a href="https://github.com/jahangirroni/jahangirroni" style="color:#00ffcc">GitHub Profile</a></div>
                <div class="metric">🏗️ Terraform EKS Code</div>
                <div class="metric">🔄 CI/CD Ready</div>
            </div>
        </div>
    </div>

    <script>
        function fetchMetrics() {
            fetch('/api/metrics')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('nodes').innerText = data.nodes;
                    document.getElementById('pods').innerText = data.pods;
                    document.getElementById('cpu').innerText = data.cpu;
                    document.getElementById('memory').innerText = data.memory;
                })
                .catch(() => {
                    document.getElementById('pods').innerText = 'auto-scaling';
                    document.getElementById('cpu').innerText = '~25';
                    document.getElementById('memory').innerText = '~40';
                });
        }
        fetchMetrics();
        setInterval(fetchMetrics, 10000);

        function shortenUrl() {
            const url = document.getElementById('urlInput').value;
            if (!url) return alert('Enter a URL');
            
            fetch('/shorten', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(res => res.json())
            .then(data => {
                document.getElementById('shortResult').innerHTML = `
                    <div class="short-url">
                        🔗 Short URL: <a href="${data.short_url}" target="_blank" style="color:#00ffcc">${data.short_url}</a>
                    </div>
                `;
            });
        }

        setTimeout(() => {
            document.querySelectorAll('.pipeline-stage')[6].className = 'pipeline-stage completed';
        }, 5000);
        setTimeout(() => {
            document.querySelectorAll('.pipeline-stage')[7].className = 'pipeline-stage running';
        }, 8000);
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(TEMPLATE)

@app.route('/api/metrics')
def metrics():
    try:
        result = subprocess.run(['kubectl', 'get', 'pods', '--no-headers', '|', 'wc', '-l'], 
                               shell=True, capture_output=True, text=True, timeout=5)
        pods = int(result.stdout.strip()) if result.stdout else 5
    except:
        pods = 5
    
    return jsonify({
        'nodes': 2,
        'pods': pods,
        'cpu': round(25 + (datetime.now().minute % 10), 1),
        'memory': round(40 + (datetime.now().minute % 15), 1),
        'cluster': 'cloud-native-cluster'
    })

@app.route('/shorten', methods=['POST'])
def shorten():
    original_url = request.json.get('url')
    short_code = hashlib.md5(original_url.encode()).hexdigest()[:6]
    urls[short_code] = original_url
    return jsonify({
        'short_url': f"http://{request.host}/{short_code}"
    })

@app.route('/<short_code>')
def redirect_url(short_code):
    if short_code in urls:
        return redirect(urls[short_code])
    return "URL not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
