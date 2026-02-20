from groq import Groq

class FixSuggestionGenerator:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)

    def generate_fix(self, query, retrieved_contexts):
        """Generate fix suggestions using RAG"""
        # Extract text from context objects
        context_texts = [ctx["text"] if isinstance(ctx, dict) else ctx for ctx in retrieved_contexts[:8]]
        context_text = "\n\n---\n\n".join(context_texts)

        prompt = f"""
You are a senior software debugging expert.

User Bug:
{query}

Relevant Past Bugs & Solutions:
{context_text}

Tasks:
1) Explain the likely cause of the bug.
2) Suggest the most probable fixes.
3) Give step-by-step debugging advice.
4) Mention severity level (Low/Medium/High/Critical).

Answer clearly and technically.
"""

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert software debugger with deep knowledge of common bugs and fixes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content
