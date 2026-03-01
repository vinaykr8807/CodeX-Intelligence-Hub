"""Test StackOverflow snippet extraction"""
import requests
from bs4 import BeautifulSoup

def test_stackoverflow_search(query="merge sort", tag="python", pagesize=5):
    """Test StackOverflow API with query+tag"""
    base = 'https://api.stackexchange.com/2.3'
    snippets = []
    
    try:
        params = {
            'order': 'desc',
            'sort': 'relevance',
            'site': 'stackoverflow',
            'pagesize': min(pagesize * 2, 30),
            'filter': 'withbody',
            'q': query,
            'tagged': tag
        }
        
        print(f"🔍 Searching: query='{query}', tag='{tag}'")
        r = requests.get(f"{base}/search/advanced", params=params, timeout=10)
        
        if r.status_code != 200:
            print(f"❌ API Error: {r.status_code}")
            return snippets
        
        items = r.json().get('items', [])
        print(f"✅ Found {len(items)} questions")
        
        for i, q in enumerate(items, 1):
            if len(snippets) >= pagesize:
                break
            
            print(f"\n📝 Question {i}: {q.get('title')}")
            print(f"   Link: {q.get('link')}")
            
            ar = requests.get(
                f"{base}/questions/{q['question_id']}/answers",
                params={'order':'desc','sort':'votes','site':'stackoverflow','filter':'withbody'},
                timeout=10
            )
            
            if ar.status_code == 200:
                answers = ar.json().get('items', [])
                print(f"   Answers: {len(answers)}")
                
                for a in answers[:2]:
                    soup = BeautifulSoup(a.get('body', ''), 'html.parser')
                    code_blocks = soup.find_all('code')
                    
                    for cb in code_blocks:
                        code_text = cb.get_text().strip()
                        if len(code_text) > 30:
                            snippets.append({
                                'title': q.get('title'),
                                'link': q.get('link'),
                                'content': code_text
                            })
                            print(f"   ✅ Extracted {len(code_text)} chars")
                            break
                    if len(snippets) >= pagesize:
                        break
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return snippets

if __name__ == "__main__":
    # Test 1: merge sort
    print("=" * 60)
    print("TEST 1: Merge Sort in Python")
    print("=" * 60)
    results = test_stackoverflow_search("merge sort", "python", 3)
    print(f"\n📊 Total snippets: {len(results)}")
    
    if results:
        print("\n" + "=" * 60)
        print("SAMPLE CODE:")
        print("=" * 60)
        print(results[0]['content'][:500])
    
    # Test 2: binary search
    print("\n\n" + "=" * 60)
    print("TEST 2: Binary Search in Python")
    print("=" * 60)
    results2 = test_stackoverflow_search("binary search", "python", 3)
    print(f"\n📊 Total snippets: {len(results2)}")
