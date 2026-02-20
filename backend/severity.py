class SeverityPredictor:
    """Rule-based severity classification using keyword signals"""
    
    def __init__(self):
        self.critical_keywords = [
            "crash", "data loss", "security", "vulnerability", "exploit",
            "memory leak", "corruption", "production down", "system failure",
            "deadlock", "sql injection", "xss", "authentication bypass"
        ]
        
        self.high_keywords = [
            "exception", "timeout", "performance issue", "failed test",
            "regression", "hang", "high cpu", "memory overflow", "null pointer",
            "segmentation fault", "stack overflow", "infinite loop"
        ]
        
        self.medium_keywords = [
            "incorrect output", "unexpected behavior", "warning",
            "slow response", "minor performance", "edge case", "validation error"
        ]
        
        self.low_keywords = [
            "ui issue", "typo", "documentation", "minor bug", "cosmetic",
            "formatting", "style", "comment", "whitespace"
        ]
    
    def predict(self, text, use_context=False, contexts=None):
        """Predict severity level from text"""
        # Combine query with retrieved contexts for better accuracy
        if use_context and contexts:
            context_texts = [ctx["text"] if isinstance(ctx, dict) else ctx for ctx in contexts[:3]]
            text = text + " " + " ".join(context_texts)
        
        t = text.lower()
        
        # Check in priority order
        for word in self.critical_keywords:
            if word in t:
                return "Critical"
        
        for word in self.high_keywords:
            if word in t:
                return "High"
        
        for word in self.medium_keywords:
            if word in t:
                return "Medium"
        
        for word in self.low_keywords:
            if word in t:
                return "Low"
        
        # Default to Medium if no keywords match
        return "Medium"
    
    def get_severity_color(self, severity):
        """Get color code for severity level"""
        colors = {
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🟢"
        }
        return colors.get(severity, "⚪")
