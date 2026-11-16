from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import torch
import time
from typing import Dict, Any


class ImageDeepfakeDetector:
    def __init__(self, model_name: str = "buildborderless/CommunityForensics-DeepfakeDet-ViT"):
        self.model_name = model_name
        self.model = ViTForImageClassification.from_pretrained(model_name)
        self.processor = ViTImageProcessor.from_pretrained(model_name)
        self.model.eval()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)

    def analyze(self, image: Image.Image) -> Dict[str, Any]:
        start_time = time.time()

        # This model requires 384x384 input
        inputs = self.processor(
            images=image,
            return_tensors="pt",
            size={"height": 384, "width": 384}
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits

            # This model outputs a SINGLE logit (binary classifier).
            # Apply sigmoid to get probability of "fake".
            if logits.shape[-1] == 1:
                prob_fake = torch.sigmoid(logits)[0][0].item()
                prob_real = 1.0 - prob_fake
                predicted_class = 1 if prob_fake > 0.5 else 0
            else:
                # Fallback for two-class models
                probabilities = torch.nn.functional.softmax(logits, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                if probabilities.shape[-1] > 1:
                    prob_real = probabilities[0][0].item()
                    prob_fake = probabilities[0][1].item()
                else:
                    prob_fake = probabilities[0][0].item()
                    prob_real = 1.0 - prob_fake

        inference_time = time.time() - start_time
        is_fake = predicted_class == 1
        confidence = max(prob_fake, prob_real)

        return {
            "is_fake": is_fake,
            "confidence": confidence,
            "model_name": self.model_name.split("/")[-1],
            "input_size": f"{inputs['pixel_values'].shape[2]}x{inputs['pixel_values'].shape[3]}",
            "inference_time": inference_time,
            "probabilities": {
                "authentic": prob_real,
                "fake": prob_fake
            }
        }