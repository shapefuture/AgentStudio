import os
import openai

class OpenRouterAnalysisTool:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://api.openrouter.ai/v1"
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
    def analyze_text(self, text, model="gpt-3.5-turbo", temperature=0.7):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": text}],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error analyzing text: {str(e)}")
            return None

    def batch_analyze(self, texts, model="gpt-3.5-turbo", temperature=0.7):
        results = []
        for text in texts:
            analysis = self.analyze_text(text, model, temperature)
            results.append(analysis)
        return results
