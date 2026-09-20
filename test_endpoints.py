import time
time.sleep(2)
import urllib.request, http.cookiejar, urllib.parse, os

base = 'http://127.0.0.1:5000'
results = []

# Test 1: GET /login
try:
    r = urllib.request.urlopen(base + '/login')
    results.append('PASS  GET /login -> ' + str(r.status))
except Exception as e:
    results.append('FAIL  GET /login -> ' + str(e))

# Test 2: GET /it-update (phishing page)
try:
    r = urllib.request.urlopen(base + '/it-update')
    results.append('PASS  GET /it-update -> ' + str(r.status))
except Exception as e:
    results.append('FAIL  GET /it-update -> ' + str(e))

# Test 3: GET /awareness-education
try:
    r = urllib.request.urlopen(base + '/awareness-education')
    results.append('PASS  GET /awareness-education -> ' + str(r.status))
except Exception as e:
    results.append('FAIL  GET /awareness-education -> ' + str(e))

# Test 4: POST /api/login + cookie check + dashboard access
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
data = urllib.parse.urlencode({'username': 'budi', 'password': 'pass'}).encode()
try:
    resp = opener.open(urllib.request.Request(base + '/api/login', data=data))
    st = next((c for c in jar if c.name == 'session_token'), None)
    if st:
        httponly = st.has_nonstandard_attr('HttpOnly')
        secure = st.secure
        val = st.value
        results.append('PASS  POST /api/login -> cookie set')
        results.append('      session_token = ' + val)
        results.append('      HttpOnly flag  = ' + str(httponly) + '  (should be False)')
        results.append('      Secure flag    = ' + str(secure) + '  (should be False)')
        # Access dashboard with cookie
        r_dash = opener.open(base + '/dashboard/keuangan')
        results.append('PASS  GET /dashboard/keuangan (with cookie) -> ' + str(r_dash.status))
    else:
        results.append('FAIL  POST /api/login -> no session_token in cookie jar')
except Exception as e:
    results.append('FAIL  POST /api/login -> ' + str(e))

# Test 5: Dashboard WITHOUT cookie (should redirect to login)
try:
    r_nodash = urllib.request.urlopen(base + '/dashboard/keuangan')
    results.append('INFO  GET /dashboard (no cookie) -> ' + str(r_nodash.status) + ' (followed redirect to login)')
except Exception as e:
    results.append('PASS  GET /dashboard (no cookie) -> redirected (' + type(e).__name__ + ')')

# Test 6: Phishing submit redirect
try:
    jar2 = http.cookiejar.CookieJar()
    opener2 = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar2))
    form = urllib.parse.urlencode({'username': 'victim', 'password': 'pw123', 'new_password': 'np456'}).encode()
    req2 = urllib.request.Request(base + '/api/phishing-submit', data=form)
    resp2 = opener2.open(req2)
    results.append('PASS  POST /api/phishing-submit -> final URL: ' + resp2.url)
except Exception as e:
    results.append('FAIL  POST /api/phishing-submit -> ' + str(e))

# Test 7: Log file
if os.path.exists('web_access.log'):
    with open('web_access.log') as f:
        lines = f.readlines()
    results.append('PASS  web_access.log exists -> ' + str(len(lines)) + ' log entries')
    if lines:
        results.append('      Last entry: ' + lines[-1].strip())
else:
    results.append('FAIL  web_access.log not found')

print()
print('=' * 60)
print('  CYBERSECURITY LAB - ENDPOINT TEST RESULTS')
print('=' * 60)
for r in results:
    print(r)
print('=' * 60)

