# skills/sentiment_analysis_skill.py
from typing import Dict, Any
from core.skill_manager import BaseSkill
from core.logger import log
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalysisSkill(BaseSkill):
    name: str = "sentiment_analyzer"
    analyzer: SentimentIntensityAnalyzer = None

    def __init__(self):
        super().__init__()
        # Initialize the analyzer once when the skill is loaded
        if SentimentAnalysisSkill.analyzer is None:
            SentimentAnalysisSkill.analyzer = SentimentIntensityAnalyzer()
            log.info("SentimentIntensityAnalyzer initialized for SentimentAnalysisSkill.")

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        operation = kwargs.get("operation", "analyze_sentiment").lower()
        text_to_analyze = kwargs.get("text", prompt) # Allow 'text' kwarg or use prompt

        log.info(f"SentimentAnalysisSkill executing. Operation: '{operation}', Text (first 50 chars): '{text_to_analyze[:50]}...'")

        if not text_to_analyze or not text_to_analyze.strip():
            return self._build_response(success=False, error="Input Error", details="Text for sentiment analysis cannot be empty.")

        if operation == "analyze_sentiment":
            try:
                vs = self.analyzer.polarity_scores(text_to_analyze)
                # Determine overall sentiment based on compound score
                if vs['compound'] >= 0.05:
                    overall_sentiment = "positive"
                elif vs['compound'] <= -0.05:
                    overall_sentiment = "negative"
                else:
                    overall_sentiment = "neutral"
                
                response_data = {"text": text_to_analyze, "scores": vs, "overall_sentiment": overall_sentiment}
                return self._build_response(success=True, data=response_data)
            except Exception as e:
                log.error(f"SentimentAnalysisSkill error: {e}", exc_info=True)
                return self._build_response(success=False, error="Analysis Error", details=str(e))
        else:
            return self._build_response(success=False, error="Unsupported Operation", details=f"Operation '{operation}' is not supported.")

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "Analyzes the sentiment of a given text using VADER (Valence Aware Dictionary and sEntiment Reasoner).",
            "operations": {
                "analyze_sentiment": {
                    "description": "Calculates sentiment scores (positive, negative, neutral, compound) for the input text.",
                    "parameters_schema": {"text": {"type": "string", "description": "The text to analyze. Can also be passed via 'prompt'."}},
                    "example_request_payload": {"task_type": self.name, "operation": "analyze_sentiment", "text": "Praximous is a wonderfully useful tool!"}
                }
            }
        }