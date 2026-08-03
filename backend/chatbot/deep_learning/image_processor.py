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
        
        # Class labels for classification
        self.classes = {
            0: 'garbage',
            1: 'pothole', 
            2: 'water_logging',
            3: 'other'
        }
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def load_model(self):
        """Load pre-trained model (ResNet50 or any other)"""
        try:
            # Use a pre-trained ResNet50 and modify for our 4 classes
            self.model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
            
            # Replace the final layer for our 4 classes
            num_features = self.model.fc.in_features
            self.model.fc = nn.Linear(num_features, 4)  # 4 classes
            
            # Load custom weights if available
            model_path = os.path.join(os.path.dirname(__file__), 'model_weights.pth')
            if os.path.exists(model_path):
                self.model.load_state_dict(torch.load(model_path, map_location=self.device))
                logger.info("Custom model weights loaded successfully")
            else:
                logger.warning("No custom weights found. Using base model for feature extraction.")
                # Use the model as feature extractor and add a classifier
                # We'll use a simpler approach for demo
                self.model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
                self.model.fc = nn.Linear(self.model.fc.in_features, 4)
            
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Model loaded on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            # Fallback to a simple classifier using pre-trained features
            self.model = None
    
    def preprocess_image(self, image):
        """Preprocess image for model input"""
        if isinstance(image, str):
            # Handle base64 or URL
            if image.startswith('data:image'):
                # Base64 image
                image_data = base64.b64decode(image.split(',')[1])
                image = Image.open(BytesIO(image_data))
            elif image.startswith('http'):
                # URL
                response = requests.get(image)
                image = Image.open(BytesIO(response.content))
            else:
                # File path
                image = Image.open(image)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transformations
        image_tensor = self.transform(image).unsqueeze(0)
        return image_tensor.to(self.device)
    
    def predict(self, image):
        """Predict the class of the image"""
        try:
            if self.model is None:
                # Fallback to feature-based classification
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
                    self.classes[i]: probabilities[0][i].item() 
                    for i in range(4)
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
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Simple color-based classification
            # Calculate average color
            avg_color = np.mean(img_array, axis=(0, 1))
            
            # Garbage: usually darker, mixed colors
            # Pothole: dark gray/black
            # Water: blue/green
            # Default: other
            
            # Simple heuristic
            if avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1]:
                # Blueish - could be water
                return {'class': 'water_logging', 'class_id': 2, 'confidence': 0.7, 'probabilities': {}}
            elif avg_color[0] < 100 and avg_color[1] < 100 and avg_color[2] < 100:
                # Dark - could be pothole
                return {'class': 'pothole', 'class_id': 1, 'confidence': 0.6, 'probabilities': {}}
            elif np.std(img_array) > 50:
                # High variance - could be garbage
                return {'class': 'garbage', 'class_id': 0, 'confidence': 0.6, 'probabilities': {}}
            else:
                return {'class': 'other', 'class_id': 3, 'confidence': 0.3, 'probabilities': {}}
                
        except Exception as e:
            logger.error(f"Fallback prediction error: {str(e)}")
            return {'class': 'other', 'class_id': 3, 'confidence': 0.0, 'probabilities': {}}
    
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
        """Detect edges in image for severity assessment"""
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
        
        # Base severity from confidence
        severity_score += prediction_result.get('confidence', 0.5) * 0.4
        
        # Adjust based on features
        if features:
            # Edge density indicates damage severity
            edge_density = features.get('edges', 0)
            if edge_density > 0.3:
                severity_score += 0.3
            elif edge_density > 0.15:
                severity_score += 0.15
            
            # Brightness and contrast
            brightness = features.get('brightness', 128)
            contrast = features.get('contrast', 50)
            
            if brightness < 80:  # Dark = more severe
                severity_score += 0.15
            if contrast > 80:  # High contrast = more visible issue
                severity_score += 0.15
        
        return min(severity_score, 1.0)