from retriever import DualFAISSRetriever
from generator import FixSuggestionGenerator
from severity import SeverityPredictor

class BugIntelligenceController:
    """Central controller orchestrating all agents"""
    
    def __init__(
        self,
        static_index,
        static_meta,
        dynamic_index,
        dynamic_meta,
        api_key
    ):
        print("🧠 Initializing Bug Intelligence System...")
        
        # Agent 2: Retriever
        print("📚 Loading Retriever Agent...")
        self.retriever = DualFAISSRetriever(
            static_index,
            static_meta,
            dynamic_index,
            dynamic_meta
        )
        
        # Agent 3: Generator
        print("🤖 Loading Generator Agent...")
        self.generator = FixSuggestionGenerator(api_key)
        
        # Agent 4: Severity Predictor
        print("⚡ Loading Severity Agent...")
        self.severity_model = SeverityPredictor()
        
        print("✅ System Ready!\n")
    
    def analyze_bug(self, query, k_static=4, k_dynamic=4):
        """
        Complete bug analysis pipeline
        
        Returns:
            dict: {
                "query": str,
                "severity": str,
                "severity_color": str,
                "fix_suggestion": str,
                "supporting_contexts": list,
                "num_contexts": int
            }
        """
        
        # Step 1: Retrieve similar bugs
        contexts = self.retriever.search(query, k_static=k_static, k_dynamic=k_dynamic)
        
        # Step 2: Predict severity (using query + context)
        severity = self.severity_model.predict(query, use_context=True, contexts=contexts)
        severity_color = self.severity_model.get_severity_color(severity)
        
        # Step 3: Generate fix suggestions
        fix_response = self.generator.generate_fix(query, contexts)
        
        # Step 4: Build structured output
        result = {
            "query": query,
            "severity": severity,
            "severity_color": severity_color,
            "fix_suggestion": fix_response,
            "supporting_contexts": contexts[:5],
            "num_contexts": len(contexts)
        }
        
        return result
    
    def batch_analyze(self, queries):
        """Analyze multiple bugs at once"""
        results = []
        for query in queries:
            result = self.analyze_bug(query)
            results.append(result)
        return results
