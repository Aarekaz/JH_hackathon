"""
Advanced sentiment analysis service using transformer models.
Replaces simple keyword matching with real NLP.
"""
from typing import Dict, List, Optional
from functools import lru_cache
import logging
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Advanced sentiment analysis using transformer models.
    Uses cardiffnlp/twitter-roberta-base-sentiment for better accuracy.
    """

    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        """
        Initialize sentiment analyzer with transformer model.

        Args:
            model_name: HuggingFace model identifier
        """
        self.model_name = model_name
        self._classifier = None
        self._initialized = False

    def _lazy_init(self):
        """Lazy initialization of the model to avoid loading at import time."""
        if self._initialized:
            return

        try:
            logger.info(f"Loading sentiment analysis model: {self.model_name}")

            # Use CPU for inference (can be changed to 'cuda' if GPU available)
            device = 0 if torch.cuda.is_available() else -1

            self._classifier = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                device=device,
                truncation=True,
                max_length=512
            )

            self._initialized = True
            logger.info("Sentiment analysis model loaded successfully")

        except Exception as e:
            logger.error(f"Failed to load sentiment model: {e}")
            self._classifier = None
            self._initialized = False

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text using transformer model.

        Args:
            text: Text to analyze

        Returns:
            Dict with sentiment scores: {'positive': 0.8, 'negative': 0.1, 'neutral': 0.1}
        """
        self._lazy_init()

        if not self._classifier:
            # Fallback to simple heuristic if model fails to load
            return self._simple_sentiment_fallback(text)

        try:
            # Get sentiment prediction
            result = self._classifier(text[:512])[0]  # Truncate to max length

            label = result['label'].lower()
            score = result['score']

            # Convert to standard format
            sentiment_scores = {
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 0.0
            }

            sentiment_scores[label] = score

            return sentiment_scores

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return self._simple_sentiment_fallback(text)

    def _simple_sentiment_fallback(self, text: str) -> Dict[str, float]:
        """Simple keyword-based fallback when model is unavailable."""
        positive_keywords = [
            'support', 'agree', 'benefit', 'positive', 'good', 'excellent',
            'innovation', 'growth', 'improvement', 'advantage', 'opportunity'
        ]
        negative_keywords = [
            'oppose', 'disagree', 'concern', 'risk', 'danger', 'harmful',
            'problem', 'issue', 'threat', 'negative', 'bad'
        ]

        text_lower = text.lower()
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)

        total = positive_count + negative_count
        if total == 0:
            return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}

        return {
            'positive': positive_count / total,
            'negative': negative_count / total,
            'neutral': 0.0
        }

    def analyze_aspects(
        self,
        text: str,
        aspects: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """
        Analyze sentiment for specific aspects mentioned in text.

        Args:
            text: Text to analyze
            aspects: List of aspects to look for (e.g., ['privacy', 'innovation'])

        Returns:
            Dict mapping aspects to sentiment scores
        """
        results = {}

        # Split text into sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        for aspect in aspects:
            # Find sentences mentioning this aspect
            relevant_sentences = [
                s for s in sentences
                if aspect.lower() in s.lower()
            ]

            if not relevant_sentences:
                results[aspect] = {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
                continue

            # Analyze sentiment of relevant sentences
            combined_text = '. '.join(relevant_sentences)
            results[aspect] = self.analyze_sentiment(combined_text)

        return results

    def get_overall_stance(
        self,
        text: str,
        role_aspects: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate overall stance based on role-specific aspect weights.

        Args:
            text: Text to analyze
            role_aspects: Dict of aspects and their weights for a role

        Returns:
            Dict with overall score and confidence
        """
        # Analyze aspects
        aspect_sentiments = self.analyze_aspects(text, list(role_aspects.keys()))

        # Calculate weighted score
        total_score = 0.0
        total_weight = 0.0

        for aspect, weight in role_aspects.items():
            if aspect in aspect_sentiments:
                sentiment = aspect_sentiments[aspect]
                aspect_score = sentiment.get('positive', 0) - sentiment.get('negative', 0)
                total_score += aspect_score * abs(weight)
                total_weight += abs(weight)

        # Normalize
        if total_weight > 0:
            normalized_score = total_score / total_weight
        else:
            normalized_score = 0.0

        # Calculate confidence based on clarity of sentiment
        confidence = min(abs(normalized_score) * 1.5, 1.0)

        return {
            'score': normalized_score,
            'confidence': confidence
        }


# Singleton instance
@lru_cache(maxsize=1)
def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get or create singleton sentiment analyzer."""
    return SentimentAnalyzer()
