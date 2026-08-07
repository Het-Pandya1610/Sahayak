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
            # FIXED: Use ResNet18 with same architecture as training
            # ============================================================
            model = models.resnet18(weights=None)
            
            # Freeze all layers (matching training)
            for param in model.parameters():
                param.requires_grad = False
            
            # Same classifier as training (with dropout and batch norm)
            num_features = model.fc.in_features
            model.fc = nn.Sequential(
                nn.Dropout(0.6),
                nn.Linear(num_features, 64),
                nn.ReLU(),
                nn.BatchNorm1d(64),
                nn.Dropout(0.48),
                nn.Linear(64, 32),
                nn.ReLU(),
                nn.BatchNorm1d(32),
                nn.Dropout(0.36),
                nn.Linear(32, 2)
            )
            
            # Load weights
            model_path = os.path.join(os.path.dirname(__file__), 'model_weights.pth')
            if os.path.exists(model_path):
                checkpoint = torch.load(model_path, map_location=self.device)
                
                # Extract model state dict from checkpoint
                if 'model_state_dict' in checkpoint:
                    state_dict = checkpoint['model_state_dict']
                    val_acc = checkpoint.get('val_acc', 'unknown')
                    epoch = checkpoint.get('epoch', 'unknown')
                    logger.info(f"✅ Loading model from epoch {epoch} with val_acc: {val_acc}%")
                else:
                    state_dict = checkpoint
                
                # Load state dict
                model.load_state_dict(state_dict)
                model.to(self.device)
                model.eval()
                self.model = model
                logger.info(f"✅ Model loaded successfully on {self.device}")
            else:
                logger.warning(f"⚠️ No trained weights found at {model_path}")
                self.model = None
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            import traceback
            traceback.print_exc()
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
                logger.warning("Model not loaded, using fallback")
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
            
            # Simple heuristics
            brightness = np.mean(img_array)
            contrast = np.std(img_array)
            
            # Check for blue/dark areas (potential pothole)
            if img_array.shape[2] == 3:
                blue_channel = img_array[:, :, 2].mean()
                if blue_channel < 100 and brightness < 100:
                    return {
                        'class': 'pothole', 
                        'class_id': 1, 
                        'confidence': 0.5, 
                        'probabilities': {'garbage': 0.5, 'pothole': 0.5}
                    }
            
            # Check for texture/variation (potential garbage)
            if contrast > 80:
                return {
                    'class': 'garbage', 
                    'class_id': 0, 
                    'confidence': 0.5, 
                    'probabilities': {'garbage': 0.6, 'pothole': 0.4}
                }
            
            # Default
            return {
                'class': 'garbage', 
                'class_id': 0, 
                'confidence': 0.3, 
                'probabilities': {'garbage': 0.5, 'pothole': 0.5}
            }
                
        except Exception as e:
            logger.error(f"Fallback prediction error: {str(e)}")
            return {
                'class': 'garbage', 
                'class_id': 0, 
                'confidence': 0.3, 
                'probabilities': {'garbage': 0.5, 'pothole': 0.5}
            }
    
    def extract_features(self, image):
        """Extract features from image for detailed analysis"""
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
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            return float(edge_density)
        except:
            return 0.0
    
    def assess_severity(self, prediction_result, features):
        """Assess severity based on prediction and features"""
        severity_score = 0.0
        
        # Confidence contributes to severity
        severity_score += prediction_result.get('confidence', 0.5) * 0.4
        
        # Features contribute to severity
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