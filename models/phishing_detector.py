from transformers import pipeline
import re
from typing import Dict, Any, List

class PhishingDetector:
    def __init__(self, model_name: str = "eduardocastellon/roberta-phishing-email-detector"):
        self.model_name = model_name
        self.classifier = pipeline(
            "text-classification",
            model=model_name,
            tokenizer=model_name,
            device=-1
        )
        self.urgency_keywords = [
            "urgent", "immediate", "act now", "expires", 
            "suspended", "verify", "confirm", "click here",
            "limited time", "account locked", "unusual activity"
        ]
        self.credential_keywords = [
            "password", "login", "username", "ssn",
            "social security", "credit card", "bank account",
            "verify your identity", "confirm your account"
        ]
    
    def analyze(self, email_text: str) -> Dict[str, Any]:
        result = self.classifier(email_text, truncation=True, max_length=512)[0]
        label = result['label']
        confidence = result['score']
        is_phishing = label == "LABEL_1"
        indicators = self._detect_indicators(email_text)
        return {
            "is_phishing": is_phishing,
            "confidence": confidence if is_phishing else 1 - confidence,
            "indicators": indicators,
            "scores": {
                "phishing_score": confidence if is_phishing else 1 - confidence,
                "legitimate_score": 1 - confidence if is_phishing else confidence,
                "raw_label": label
            }
        }
    
    def _detect_indicators(self, text: str) -> List[str]:
        indicators = []
        text_lower = text.lower()
        found_urgency = [kw for kw in self.urgency_keywords if kw in text_lower]
        if found_urgency:
            indicators.append(f"Urgency language: {', '.join(found_urgency[:3])}")
        found_credentials = [kw for kw in self.credential_keywords if kw in text_lower]
        if found_credentials:
            indicators.append(f"Credential request: {', '.join(found_credentials[:3])}")
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, text)
        suspicious = [u for u in urls if self._is_suspicious_url(u)]
        if suspicious:
            indicators.append(f"Suspicious URLs found: {len(suspicious)}")
        generic_greetings = ["dear customer", "dear user", "dear member", "dear account holder"]
        if any(g in text_lower for g in generic_greetings):
            indicators.append("Generic greeting used")
        if not indicators:
            indicators.append("No additional risk indicators found")
        return indicators
    
    def _is_suspicious_url(self, url: str) -> bool:
        patterns = [
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            r'bit\.ly|tinyurl|goo\.gl',
            r'[а-яА-Я]',
            r'\.(tk|ml|ga|cf|gq)$',
        ]
        return any(re.search(p, url) for p in patterns)