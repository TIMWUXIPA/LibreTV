"""Run: python3 scripts/check-deployment.py [base URL]. Secrets stay local."""
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

base = (sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:18787').rstrip('/')
secrets = dict(line.split('=', 1) for line in (Path(__file__).resolve().parents[1] / '.dev.vars').read_text().splitlines() if '=' in line)
cookie = ''

def request(path, data=None, authenticated=False):
    headers = {'Content-Type': 'application/json', 'X-Forwarded-Proto': 'https'}
    if authenticated:
        headers['Cookie'] = cookie
    req = urllib.request.Request(base + path, data=None if data is None else json.dumps(data).encode(), headers=headers)
    try:
        response = urllib.request.urlopen(req, timeout=40)
    except urllib.error.HTTPError as error:
        response = error
    return response.status, response.headers, response.read()

status, _, body = request('/api/status')
assert status == 200 and json.loads(body)['passwordRequired'] is True, (status, body[:300])
print('PASS status and password required')
status, _, _ = request('/api/search', {'wd': 'test', 'sources': []})
assert status == 401, status
print('PASS unauthenticated search denied')
status, _, _ = request('/api/auth', {'password': 'invalid-smoke-test-password'})
assert status == 401, status
print('PASS wrong password denied')
status, headers, body = request('/api/auth', {'password': secrets['PASSWORD']})
assert status == 200 and json.loads(body)['success'], (status, body[:300])
cookie = headers['Set-Cookie'].split(';', 1)[0]
assert 'httponly' in headers['Set-Cookie'].lower() and 'secure' in headers['Set-Cookie'].lower()
print('PASS login and secure HttpOnly cookie')
status, _, body = request('/api/auth', authenticated=True)
assert status == 200 and json.loads(body)['verified'] is True, (status, body[:300])
print('PASS authenticated session')
status, _, body = request('/api/proxy?url=' + urllib.parse.quote('http://127.0.0.1/', safe=''), authenticated=True)
assert status in (400, 403), (status, body[:300])
print('PASS private IP blocked')
status, _, body = request('/api/search', {'wd': 'test', 'sources': [{'key': 'blocked', 'name': 'blocked', 'url': 'http://127.0.0.1/'}]}, True)
assert status == 200 and json.loads(body)['failures'], (status, body[:300])
print('PASS search backend and private source blocked')
sample = 'https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8'
status, _, body = request('/api/proxy?url=' + urllib.parse.quote(sample, safe=''), authenticated=True)
assert status == 200 and body.startswith(b'#EXTM3U') and b'/api/proxy' in body, (status, body[:300])
print('PASS public HLS playlist fetch and proxy rewrite')
status, _, body = request('/')
assert status == 200 and b'LibreTV' in body, (status, body[:200])
print('PASS homepage')
