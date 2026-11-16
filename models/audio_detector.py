import torch
import numpy as np
import time
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
from typing import Dict, Any


class AudioDeepfakeDetector:
    """
    Detects AI-generated audio (voice cloning / TTS) using a
    Wav2Vec2-based audio classification model.

    Model: garystafford/wav2vec2-deepfake-voice-detector
    - Standard Wav2Vec2 sequence classification
    - Fully compatible with AutoModelForAudioClassification
    - Detects ElevenLabs, Amazon Polly, Kokoro, Hume AI, Speechify, Luvvoice
    """

    def __init__(self, model_name: str = "garystafford/wav2vec2-deepfake-voice-detector"):
        self.model_name = model_name
        self.model = AutoModelForAudioClassification.from_pretrained(model_name)
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(model_name)
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def analyze(self, audio_array: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """Analyze an audio waveform for deepfake indicators."""
        start_time = time.time()

        # Ensure mono
        if audio_array.ndim > 1:
            audio_array = audio_array.mean(axis=1)

        # Normalize
        if np.max(np.abs(audio_array)) > 0:
            audio_array = audio_array / np.max(np.abs(audio_array))

        # Pad or truncate to 4 seconds at 16 kHz (64,000 samples)
        max_length = 64000
        if len(audio_array) > max_length:
            audio_array = audio_array[:max_length]
        else:
            audio_array = np.pad(audio_array, (0, max(0, max_length - len(audio_array))))

        # Extract features
        inputs = self.feature_extractor(
            audio_array,
            sampling_rate=16000,
            return_tensors="pt",
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]

        inference_time = time.time() - start_time

        # Determine which class is "fake" based on the model's label mapping
        label2id = self.model.config.label2id
        id2label = self.model.config.id2label

        # Try to find the "fake" label dynamically
        fake_index = None
        real_index = None
        for idx, label in id2label.items():
            label_lower = label.lower()
            if "fake" in label_lower or "spoof" in label_lower or "synthetic" in label_lower:
                fake_index = int(idx)
            elif "real" in label_lower or "bonafide" in label_lower or "genuine" in label_lower:
                real_index = int(idx)

        # Fallback: assume index 1 is fake, index 0 is real
        if fake_index is None:
            fake_index = 1 if len(probabilities) > 1 else 0
        if real_index is None:
            real_index = 0 if len(probabilities) > 1 else 0

        prob_fake = float(probabilities[fake_index])
        prob_real = float(probabilities[real_index]) if real_index != fake_index else 1.0 - prob_fake

        is_fake = prob_fake > 0.5

        return {
            "is_fake": is_fake,
            "confidence": max(prob_real, prob_fake),
            "model_name": self.model_name.split("/")[-1],
            "inference_time": inference_time,
            "probabilities": {
                "real": prob_real,
                "fake": prob_fake
            }
        }