import requests

urls = ['https://omnigate-erp-os.web.app', 'https://omnigateos.com/']
sections = ['vision', 'comparison', 'simulator', 'replay-studio', 'roi-calculator', 'ledger', 'benchmarks', 'contact']

for url in urls:
    try:
        r = requests.get(url, timeout=10)
        print(f"=== URL: {url} ===")
        print(f"Status Code: {r.status_code}")
        print(f"Content Length: {len(r.text)} bytes")
        for s in sections:
            found = f'id="{s}"' in r.text
            print(f"  Section #{s}: {'FOUND' if found else 'MISSING'}")
        
        # Verify crucial assets and logic
        print(f"  styles.css linked: {'styles.css' in r.text}")
        print(f"  app.js linked: {'app.js' in r.text}")
        print(f"  Email info@omnigateos.com: {'info@omnigateos.com' in r.text}")
        print(f"  SAG Studio DAG Visualizer: {'SAG Studio' in r.text}")
        print(f"  ROI Slider present: {'input-revenue' in r.text or 'range-employees' in r.text or 'slider' in r.text.lower()}")
    except Exception as e:
        print(f"Error checking {url}: {e}")
