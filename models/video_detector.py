import torch
import numpy as np
import cv2
from PIL import Image
import time
import os
from typing import Dict, Any, List


class VideoDeepfakeDetector:
    """
    Detects AI-generated video using VideoMAE.

    Model: Vansh180/VideoMae-ffc23-deepfake-detector
    - VideoMAE base, fine-tuned on FaceForensics++ (C23)
    - Expects exactly 16 frames per video
    - Standard VideoMAEForVideoClassification architecture
    """

    def __init__(self, model_name: str = "Vansh180/VideoMae-ffc23-deepfake-detector"):
        self.model_name = model_name
        self.available = False
        self.model = None
        self.processor = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.num_frames = 16  # Fixed at 16 for this model

        try:
            from transformers import VideoMAEForVideoClassification, VideoMAEImageProcessor

            self.model = VideoMAEForVideoClassification.from_pretrained(model_name)
            self.processor = VideoMAEImageProcessor.from_pretrained(model_name)
            self.model.eval()
            self.model.to(self.device)
            self.available = True
            print(f"[video_detector] Model loaded: {model_name}")
        except Exception as e:
            print(f"[video_detector] Model loading failed: {e}")
            self.available = False

    def extract_frames(self, video_path: str, num_frames: int = 16) -> List[np.ndarray]:
        """Extract exactly num_frames uniformly-spaced frames as RGB numpy arrays."""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return []

            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                cap.release()
                return []

            # Always extract exactly num_frames
            indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            frames = []

            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
                ret, frame = cap.read()
                if ret and frame is not None:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)

            cap.release()

            # If we got fewer frames than needed, pad by repeating the last one
            while len(frames) < num_frames and len(frames) > 0:
                frames.append(frames[-1])

            return frames[:num_frames]
        except Exception as e:
            print(f"[video_detector] Frame extraction failed: {e}")
            return []

    def analyze(self, video_path: str, num_frames: int = 16) -> Dict[str, Any]:
        """Analyze a video for deepfake indicators."""
        start_time = time.time()

        if not os.path.exists(video_path):
            return {
                "is_fake": None,
                "confidence": 0.0,
                "error": "Video file does not exist.",
                "model_name": self.model_name
            }

        if not self.available:
            return {
                "is_fake": None,
                "confidence": 0.0,
                "error": "Video model not available.",
                "model_name": self.model_name
            }

        try:
            # Extract exactly 16 frames as numpy arrays
            frames = self.extract_frames(video_path, self.num_frames)

            if len(frames) == 0:
                return {
                    "is_fake": None,
                    "confidence": 0.0,
                    "error": "No frames could be extracted from the video.",
                    "model_name": self.model_name
                }

            # Process frames. The VideoMAEImageProcessor expects a list of frames
            # (a single video) and returns pixel_values with shape
            # (1, num_frames, num_channels, height, width).
            inputs = self.processor(frames, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=-1)[0]

            inference_time = time.time() - start_time

            # The model outputs 2 classes: 0 = real, 1 = fake
            prob_real = float(probabilities[0])
            prob_fake = float(probabilities[1])
            is_fake = prob_fake > 0.5
            confidence = max(prob_real, prob_fake)

            return {
                "is_fake": is_fake,
                "confidence": confidence,
                "model_name": self.model_name.split("/")[-1],
                "inference_time": inference_time,
                "avg_fake_probability": prob_fake,
                "frames_analyzed": len(frames),
                "frame_results": [
                    {"frame": 1, "fake_probability": prob_fake, "is_fake": is_fake}
                ],
                "error": None
            }

        except Exception as e:
            return {
                "is_fake": None,
                "confidence": 0.0,
                "error": f"Video analysis failed: {str(e)}",
                "model_name": self.model_name
            }