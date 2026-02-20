import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

class DualFAISSRetriever:
    def __init__(
        self,
        static_index_path,
        static_meta_path,
        dynamic_index_path,
        dynamic_meta_path,
        model_name="all-MiniLM-L6-v2"
    ):
        print("🔄 Loading embedding model...")
        self.model = SentenceTransformer(model_name)

        print("📚 Loading static index...")
        self.static_index = faiss.read_index(static_index_path)
        self.static_meta = pd.read_csv(static_meta_path)

        print("🔥 Loading dynamic index...")
        self.dynamic_index = faiss.read_index(dynamic_index_path)
        self.dynamic_meta = pd.read_csv(dynamic_meta_path)
        
        print(f"✅ Loaded: {len(self.static_meta)} static + {len(self.dynamic_meta)} dynamic records")

    def search(self, query, k_static=5, k_dynamic=5):
        """Search both indexes and merge results"""
        # Embed query
        query_vec = self.model.encode([query])

        # Search static
        D1, I1 = self.static_index.search(query_vec, k_static)
        static_results = [
            {
                "text": self.static_meta.iloc[i]["text"],
                "source": "static",
                "distance": float(D1[0][idx])
            }
            for idx, i in enumerate(I1[0]) if i < len(self.static_meta)
        ]

        # Search dynamic
        D2, I2 = self.dynamic_index.search(query_vec, k_dynamic)
        dynamic_results = [
            {
                "text": self.dynamic_meta.iloc[i]["text"],
                "source": "dynamic",
                "distance": float(D2[0][idx])
            }
            for idx, i in enumerate(I2[0]) if i < len(self.dynamic_meta)
        ]

        # Merge and sort by distance
        combined = static_results + dynamic_results
        combined.sort(key=lambda x: x["distance"])
        
        return combined
