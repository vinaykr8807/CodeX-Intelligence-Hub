import requests
import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import time
from datetime import datetime
import os

class RealTimeBugFetcher:
    """Fetches bugs in real-time and updates FAISS indexes"""
    
    def __init__(self, model_dir, groq_key=None, stack_key=None):
        self.model_dir = model_dir
        self.stack_key = stack_key
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load existing indexes
        self.dynamic_index_path = os.path.join(model_dir, "dynamic_faiss.index")
        self.dynamic_meta_path = os.path.join(model_dir, "dynamic_metadata.csv")
        
        self.index = faiss.read_index(self.dynamic_index_path)
        self.metadata = pd.read_csv(self.dynamic_meta_path)
        
        print(f"✅ Loaded: {len(self.metadata)} existing records")
    
    def fetch_github_bugs(self, languages, max_per_lang=50):
        """Fetch recent bugs from GitHub"""
        records = []
        
        for lang in languages:
            query = f"language:{lang} label:bug state:closed"
            url = "https://api.github.com/search/issues"
            params = {"q": query, "per_page": max_per_lang, "sort": "updated"}
            
            try:
                res = requests.get(url, params=params, timeout=10)
                if res.status_code == 200:
                    items = res.json().get("items", [])
                    for item in items:
                        records.append({
                            "text": f"ISSUE: {item.get('title')} DESCRIPTION: {item.get('body', '')}",
                            "source": "github_realtime",
                            "language": lang,
                            "url": item.get("html_url"),
                            "created_at": item.get("created_at")
                        })
                time.sleep(2)
            except:
                continue
        
        return records
    
    def fetch_stackoverflow_bugs(self, tags, max_per_tag=50):
        """Fetch recent bugs from StackOverflow"""
        records = []
        
        for tag in tags:
            url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                "pagesize": max_per_tag,
                "order": "desc",
                "sort": "creation",
                "tagged": tag,
                "site": "stackoverflow",
                "filter": "withbody",
                "q": "error OR bug",
                "key": self.stack_key
            }
            
            try:
                res = requests.get(url, params=params, timeout=10)
                data = res.json()
                
                if "items" in data:
                    for q in data["items"]:
                        records.append({
                            "text": f"BUG: {q.get('title')} CONTEXT: {q.get('body', '')}",
                            "source": "stackoverflow_realtime",
                            "language": tag,
                            "url": q.get("link"),
                            "created_at": datetime.fromtimestamp(q.get("creation_date")).strftime("%Y-%m-%d")
                        })
                time.sleep(2)
            except:
                continue
        
        return records
    
    def update_index(self, new_records):
        """Add new records to FAISS index"""
        if not new_records:
            return 0
        
        # Create embeddings
        texts = [r["text"] for r in new_records]
        embeddings = self.model.encode(texts)
        
        # Add to FAISS
        self.index.add(embeddings.astype('float32'))
        
        # Update metadata
        new_df = pd.DataFrame(new_records)
        self.metadata = pd.concat([self.metadata, new_df], ignore_index=True)
        
        # Save
        faiss.write_index(self.index, self.dynamic_index_path)
        self.metadata.to_csv(self.dynamic_meta_path, index=False)
        
        return len(new_records)
    
    def run_continuous(self, languages, tags, interval_minutes=60):
        """Run continuous fetching loop"""
        print(f"🔄 Starting real-time fetcher (interval: {interval_minutes} min)")
        
        while True:
            print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Fetch from GitHub
            print("📥 Fetching from GitHub...")
            gh_bugs = self.fetch_github_bugs(languages)
            print(f"   Found {len(gh_bugs)} new GitHub bugs")
            
            # Fetch from StackOverflow
            print("📥 Fetching from StackOverflow...")
            so_bugs = self.fetch_stackoverflow_bugs(tags)
            print(f"   Found {len(so_bugs)} new SO bugs")
            
            # Update index
            all_bugs = gh_bugs + so_bugs
            added = self.update_index(all_bugs)
            print(f"✅ Added {added} records to index")
            print(f"📊 Total records: {len(self.metadata)}")
            
            # Wait
            print(f"⏳ Sleeping for {interval_minutes} minutes...")
            time.sleep(interval_minutes * 60)
    
    def run_once(self, languages, tags):
        """Run single fetch cycle"""
        print(f"🔄 Running single fetch cycle...")
        
        gh_bugs = self.fetch_github_bugs(languages, max_per_lang=100)
        so_bugs = self.fetch_stackoverflow_bugs(tags, max_per_tag=100)
        
        all_bugs = gh_bugs + so_bugs
        added = self.update_index(all_bugs)
        
        print(f"✅ Added {added} records")
        print(f"📊 Total: {len(self.metadata)} records")
        
        return added
