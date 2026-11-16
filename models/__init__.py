"""
Models package for the AI Threat Detector.

Imports are wrapped in try/except so that a single broken model
(e.g., video) does not prevent the other detectors from loading.
"""

try:
    from .phishing_detector import PhishingDetector
except Exception as e:
    print(f"[models] Could not import PhishingDetector: {e}")
    PhishingDetector = None

try:
    from .image_detector import ImageDeepfakeDetector
except Exception as e:
    print(f"[models] Could not import ImageDeepfakeDetector: {e}")
    ImageDeepfakeDetector = None

try:
    from .audio_detector import AudioDeepfakeDetector
except Exception as e:
    print(f"[models] Could not import AudioDeepfakeDetector: {e}")
    AudioDeepfakeDetector = None

try:
    from .video_detector import VideoDeepfakeDetector
except Exception as e:
    print(f"[models] Could not import VideoDeepfakeDetector: {e}")
    VideoDeepfakeDetector = None