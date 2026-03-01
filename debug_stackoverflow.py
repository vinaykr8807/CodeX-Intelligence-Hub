import requests
from bs4 import BeautifulSoup
import html as _html

def debug_stackoverflow(query, tag):
    base = 'https://api.stackexchange.com/2.3'
    
    params = {
        'order': 'desc',
        'sort': 'relevance',
        'site': 'stackoverflow',
        'pagesize': 5,
        'filter': 'withbody',
        'q': query,
        'tagged': tag
    }
    
    print(f"Searching: query='{query}', tag='{tag}'")
    print(f"URL: {base}/search/advanced")
    print(f"Params: {params}\n")
    
    r = requests.get(f"{base}/search/advanced", params=params, timeout=10)
    print(f"Status: {r.status_code}")
    
    if r.status_code != 200:
        print(f"Failed: {r.text[:200]}")
        return
    
    items = r.json().get('items', [])
    print(f"Found {len(items)} questions\n")
    
    for i, q in enumerate(items[:3], 1):
        print(f"{'='*60}")
        print(f"Question {i}: {q.get('title')}")
        print(f"   Link: {q.get('link')}")
        
        # Get answers
        ar = requests.get(f"{base}/questions/{q['question_id']}/answers",
                         params={'order':'desc','sort':'votes','site':'stackoverflow','filter':'withbody'},
                         timeout=10)
        
        if ar.status_code != 200:
            print(f"   No answers")
            continue
            
        answers = ar.json().get('items', [])
        print(f"   Answers: {len(answers)}")
        
        for j, a in enumerate(answers[:2], 1):
            print(f"\n   --- Answer {j} ---")
            body = a.get('body', '')
            print(f"   Raw HTML length: {len(body)}")
            
            soup = BeautifulSoup(body, 'html.parser')
            
            # Try different extraction methods
            print(f"\n   Method 1: Find all <pre>")
            pres = soup.find_all('pre')
            print(f"   Found {len(pres)} <pre> tags")
            
            for k, pre in enumerate(pres[:2], 1):
                code_block = pre.find('code')
                if code_block:
                    raw_text = code_block.get_text()
                    decoded = _html.unescape(raw_text)
                    print(f"   <pre> {k}:")
                    print(f"     Raw length: {len(raw_text)}")
                    print(f"     Decoded length: {len(decoded)}")
                    print(f"     Lines: {decoded.count(chr(10))}")
                    print(f"     Preview: {decoded[:100]}")
            
            print(f"\n   Method 2: Find all <code>")
            codes = soup.find_all('code')
            print(f"   Found {len(codes)} <code> tags")
            
            for k, code in enumerate(codes[:3], 1):
                raw_text = code.get_text()
                decoded = _html.unescape(raw_text)
                print(f"   <code> {k}: len={len(decoded)}, lines={decoded.count(chr(10))}")
                if len(decoded) > 30:
                    print(f"     Preview: {decoded[:80]}")

if __name__ == "__main__":
    debug_stackoverflow("merge sort", "python")
