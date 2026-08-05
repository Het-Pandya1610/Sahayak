import os
import cv2
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision import models
import torch.nn as nn
import requests
from io import BytesIO
import base64
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_model()
        
        # ============================================================
        # MATCH YOUR TRAINED MODEL: 2 classes (garbage, pothole)
        # ============================================================
        self.classes = {
            0: 'garbage',
            1: 'pothole'
        }
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self):
        """Load trained model - MATCHES YOUR TRAINING ARCHITECTURE"""
        try:
            # ============================================================
            # FIXED: Use ResNet18 with 2 classes (matches your training!)
            # ============================================================
            self.model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
            num_features = self.model.fc.in_features
            self.model.fc = nn.Linear(num_features, 2)  # 2 classes
            
            # Load custom weights
            model_path = os.path.join(os.path.dirname(__file__), 'model_weights.pth')
            if os.path.exists(model_path):
                state_dict = torch.load(model_path, map_location=self.device)
                self.model.load_state_dict(state_dict)
                logger.info("✅ Custom model weights loaded successfully")
                self.model.to(self.device)
                self.model.eval()
                logger.info(f"Model loaded on {self.device}")
            else:
                logger.warning(f"⚠️ No trained weights found at {model_path}")
                self.model = None
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self.model = None
    
    def preprocess_image(self, image):
        """Preprocess image for model input"""
        if isinstance(image, str):
            if image.startswith('data:image'):
                image_data = base64.b64decode(image.split(',')[1])
                image = Image.open(BytesIO(image_data))
            elif image.startswith('http'):
                response = requests.get(image)
                image = Image.open(BytesIO(response.content))
            else:
                image = Image.open(image)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_tensor = self.transform(image).unsqueeze(0)
        return image_tensor.to(self.device)
    
    def predict(self, image):
        """Predict if image is garbage or pothole"""
        try:
            if self.model is None:
                return self._fallback_prediction(image)
            
            image_tensor = self.preprocess_image(image)
            
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted_class].item()
            
            class_name = self.classes.get(predicted_class, 'other')
            
            return {
                'class': class_name,
                'class_id': predicted_class,
                'confidence': confidence,
                'probabilities': {
                    'garbage': probabilities[0][0].item(),
                    'pothole': probabilities[0][1].item()
                }
            }
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return self._fallback_prediction(image)
    
    def _fallback_prediction(self, image):
        """Fallback prediction using simple image analysis"""
        try:
            if isinstance(image, str):
                if image.startswith('data:image'):
                    image_data = base64.b64decode(image.split(',')[1])
                    img = Image.open(BytesIO(image_data))
                else:
                    img = Image.open(image)
            else:
                img = image
            
            img_array = np.array(img)
            avg_color = np.mean(img_array, axis=(0, 1))
            
            if avg_color[0] < 100 and avg_color[1] < 100 and avg_color[2] < 100:
                return {'class': 'pothole', 'class_id': 1, 'confidence': 0.6, 'probabilities': {}}
            elif np.std(img_array) > 50:
                return {'class': 'garbage', 'class_id': 0, 'confidence': 0.6, 'probabilities': {}}
            else:
                return {'class': 'garbage', 'class_id': 0, 'confidence': 0.5, 'probabilities': {}}
                
        except Exception as e:
            logger.error(f"Fallback prediction error: {str(e)}")
            return {'class': 'garbage', 'class_id': 0, 'confidence': 0.3, 'probabilities': {}}
    
    def extract_features(self, image):
        """Extract features from image for detailed analysis"""
        try:
            img_array = np.array(image if not isinstance(image, str) else Image.open(image))
            
            features = {
                'width': img_array.shape[1],
                'height': img_array.shape[0],
                'mean_color': np.mean(img_array, axis=(0, 1)).tolist(),
                'std_color': np.std(img_array, axis=(0, 1)).tolist(),
                'brightness': np.mean(img_array),
                'contrast': np.std(img_array),
                'edges': self._detect_edges(img_array)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction error: {str(e)}")
            return {}
    
    def _detect_edges(self, img_array):
        try:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            return edge_density
        except:
            return 0.0
    
    def assess_severity(self, prediction_result, features):
        """Assess severity based on prediction and features"""
        severity_score = 0.0
        severity_score += prediction_result.get('confidence', 0.5) * 0.4
        
        if features:
            edge_density = features.get('edges', 0)
            if edge_density > 0.3:
                severity_score += 0.3
            elif edge_density > 0.15:
                severity_score += 0.15
            
            brightness = features.get('brightness', 128)
            if brightness < 80:
                severity_score += 0.15
            contrast = features.get('contrast', 50)
            if contrast > 80:
                severity_score += 0.15
        
        return min(severity_score, 1.0)