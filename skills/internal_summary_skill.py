# skills/internal_summary_skill.py
from typing import Dict, Any
from core.skill_manager import BaseSkill
from core.logger import log
import re

class InternalSummarySkill(BaseSkill):
    name: str = "internal_summary" # This must match the task_type in API requests

    async def execute(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        log.info(f"InternalSummarySkill executing with prompt (first 50 chars): '{prompt[:50]}...' and args: {kwargs}")

        if not prompt or not prompt.strip():
            return self._build_response(success=False, error="Input Error", details="Prompt text cannot be empty for summarization.")

        original_text = prompt
        summary_type = kwargs.get("summary_type", "first_sentences").lower()
        max_sentences = kwargs.get("max_sentences", 2)
        max_words = kwargs.get("max_words", 50)

        summary_text = ""

        if summary_type == "first_sentences":
            # Simple sentence splitting, might need refinement for complex cases
            sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', original_text)
            summary_text = " ".join(sentences[:max_sentences])
        elif summary_type == "first_words":
            words = original_text.split()
            summary_text = " ".join(words[:max_words])
            if len(words) > max_words:
                summary_text += "..."
        else:
            return self._build_response(
                success=False,
                data={"original_text_length": len(original_text)},
                error=f"Unsupported summary_type: {summary_type}",
                details="Supported summary_types are: first_sentences, first_words."
            )

        response_data = {
            "original_text_length": len(original_text),
            "summary_type_used": summary_type,
            "summary": summary_text,
            "message": "Summary generated successfully."
        }
        return self._build_response(success=True, data=response_data)

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "skill_name": self.name,
            "description": "Generates a simple summary of the provided text using basic heuristics.",
            "operations": {
                "generate_summary": {
                    "description": "Creates a summary by extracting first sentences or words.",
                    "parameters_schema": {
                        "prompt": {"type": "string", "description": "The text to be summarized."},
                        "summary_type": {"type": "string", "enum": ["first_sentences", "first_words"], "default": "first_sentences", "description": "Method for summarization."},
                        "max_sentences": {"type": "integer", "default": 2, "description": "Number of sentences for 'first_sentences' summary."},
                        "max_words": {"type": "integer", "default": 50, "description": "Number of words for 'first_words' summary."}
                    },
                    "example_request_payload": {
                        "task_type": self.name,
                        "prompt": "This is a long piece of text that needs to be summarized. It has multiple sentences. We want to see only the beginning.",
                        "summary_type": "first_sentences",
                        "max_sentences": 1
                    }
                }
            }
        }