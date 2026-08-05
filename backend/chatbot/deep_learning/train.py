"""
Train a 2-class model (Pothole vs Garbage) with enhanced dataset
Run: python -m chatbot.deep_learning.train
"""

import os
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import numpy as np
from pathlib import Path
import time
import gc
import random

# ============================================================
# CONFIGURATION - UPDATED WITH MORE EPOCHS
# ============================================================
EPOCHS = 30  # Increased from 15 to 30 for better accuracy
BATCH_SIZE = 32
LEARNING_RATE = 0.001
IMG_SIZE = 224
EARLY_STOPPING_PATIENCE = 8  # Increased patience

# Get the directory of this file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_DIR = BASE_DIR / 'datasets' / 'municipal_issues'

print(f"📂 Dataset path: {DATASET_DIR}")
print(f"📂 Base path: {BASE_DIR}")

# Check if dataset exists
if not DATASET_DIR.exists():
    print(f"❌ Dataset not found at {DATASET_DIR}")
    sys.exit(1)

# Device configuration
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"🚀 Using device: {device}")

if device.type == 'cuda':
    print(f"   GPU: {torch.cuda.get_device_name(0)}")
    print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")


# ============================================================
# DATASET CLASS - FIXED FOR YOUR ACTUAL STRUCTURE
# ============================================================
class PotholeGarbageDataset(Dataset):
    """Dataset for Pothole vs Garbage classification"""
    
    def __init__(self, root_dir, transform=None, max_samples=None, split='train'):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.split = split
        self.samples = []
        self.classes = ['garbage', 'pothole']
        self.class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        
        print(f"📂 Loading dataset from: {root_dir} (split: {split})")
        
        # YOUR ACTUAL STRUCTURE: root_dir/class_name/split/images/
        # Where split is either 'train' or 'valid'
        for class_name in self.classes:
            class_dir = self.root_dir / class_name / split / 'images'
            if class_dir.exists():
                images = list(class_dir.glob('*.*'))
                images = [img for img in images if img.suffix.lower() in ['.jpg', '.jpeg', '.png']]
                
                if max_samples and len(images) > max_samples:
                    images = random.sample(images, max_samples)
                
                for img_path in images:
                    self.samples.append({
                        'path': str(img_path),
                        'label': self.class_to_idx[class_name]
                    })
                print(f"  ✅ Loaded {len(images)} {class_name} images from {class_dir}")
            else:
                print(f"  ⚠️ Directory not found: {class_dir}")
        
        print(f"  📊 Total samples: {len(self.samples)}")
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        try:
            image = Image.open(sample['path']).convert('RGB')
            label = sample['label']
            
            if self.transform:
                image = self.transform(image)
            
            return image, label
        except Exception as e:
            print(f"⚠️ Error loading image {sample['path']}: {e}")
            random_idx = np.random.randint(0, len(self.samples))
            return self.__getitem__(random_idx)


# ============================================================
# DATA TRANSFORMS
# ============================================================
train_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(degrees=15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

val_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


# ============================================================
# TRAINING FUNCTION - FIXED
# ============================================================
def train_model():
    """Main training function"""
    print("\n" + "="*60)
    print("🚀 TRAINING POTHOLES vs GARBAGE CLASSIFIER")
    print("="*60)
    
    # Check dataset structure
    garbage_train = DATASET_DIR / 'garbage' / 'train' / 'images'
    pothole_train = DATASET_DIR / 'pothole' / 'train' / 'images'
    garbage_valid = DATASET_DIR / 'garbage' / 'valid' / 'images'
    pothole_valid = DATASET_DIR / 'pothole' / 'valid' / 'images'
    
    print("\n📊 Checking dataset structure...")
    print(f"  Garbage Train: {garbage_train.exists()} ({len(list(garbage_train.glob('*.*'))) if garbage_train.exists() else 0} images)")
    print(f"  Pothole Train: {pothole_train.exists()} ({len(list(pothole_train.glob('*.*'))) if pothole_train.exists() else 0} images)")
    print(f"  Garbage Valid: {garbage_valid.exists()} ({len(list(garbage_valid.glob('*.*'))) if garbage_valid.exists() else 0} images)")
    print(f"  Pothole Valid: {pothole_valid.exists()} ({len(list(pothole_valid.glob('*.*'))) if pothole_valid.exists() else 0} images)")
    
    # FIXED: Load datasets with split parameter
    train_dataset = PotholeGarbageDataset(DATASET_DIR, transform=train_transform, split='train')
    val_dataset = PotholeGarbageDataset(DATASET_DIR, transform=val_transform, split='valid')
    
    if len(train_dataset) == 0 or len(val_dataset) == 0:
        print("❌ No images found in dataset!")
        print("\n📁 Your dataset structure should be:")
        print("   datasets/municipal_issues/garbage/train/images/")
        print("   datasets/municipal_issues/pothole/train/images/")
        print("   datasets/municipal_issues/garbage/valid/images/")
        print("   datasets/municipal_issues/pothole/valid/images/")
        return
    
    print(f"\n📊 Dataset Summary:")
    print(f"  Training: {len(train_dataset)} images")
    print(f"  Validation: {len(val_dataset)} images")
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset, 
        batch_size=BATCH_SIZE, 
        shuffle=True,
        num_workers=4,
        pin_memory=True,
        persistent_workers=True,
        prefetch_factor=2
    )
    val_loader = DataLoader(
        val_dataset, 
        batch_size=BATCH_SIZE * 2,
        shuffle=False,
        num_workers=4,
        pin_memory=True,
        persistent_workers=True,
        prefetch_factor=2
    )
    
    # Load pre-trained model
    print("\n🧠 Loading pre-trained ResNet18...")
    model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)
    model = model.to(device)
    
    # Loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3, factor=0.5)
    
    # Training loop
    print(f"\n📈 Starting training for {EPOCHS} epochs...")
    print("="*60)
    
    best_val_acc = 0.0
    model_path = os.path.join(os.path.dirname(__file__), 'model_weights.pth')
    epochs_without_improvement = 0
    
    for epoch in range(1, EPOCHS + 1):
        epoch_start = time.time()
        
        # Training phase
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images, labels = images.to(device), labels.to(device)
            
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = outputs.max(1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
            
            if batch_idx % 50 == 0 and device.type == 'cuda':
                torch.cuda.empty_cache()
        
        train_acc = 100 * train_correct / train_total
        train_loss_avg = train_loss / len(train_loader)
        
        # Validation phase
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_acc = 100 * val_correct / val_total
        val_loss_avg = val_loss / len(val_loader)
        
        scheduler.step(val_loss_avg)
        epoch_time = time.time() - epoch_start
        
        print(f"\n📊 Epoch {epoch}/{EPOCHS} ({epoch_time:.1f}s)")
        print(f"  Train Loss: {train_loss_avg:.4f} | Train Acc: {train_acc:.2f}%")
        print(f"  Val Loss: {val_loss_avg:.4f} | Val Acc: {val_acc:.2f}%")
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            torch.save(model.state_dict(), model_path)
            epochs_without_improvement = 0
            print(f"  ✅ Best model saved! (Acc: {val_acc:.2f}%)")
        else:
            epochs_without_improvement += 1
            print(f"  ⏳ No improvement for {epochs_without_improvement} epochs")
        
        if epochs_without_improvement >= EARLY_STOPPING_PATIENCE:
            print(f"\n⚠️ Early stopping triggered after {epoch} epochs!")
            break
        
        if device.type == 'cuda':
            torch.cuda.empty_cache()
        gc.collect()
    
    print("\n" + "="*60)
    print("🎉 TRAINING COMPLETE!")
    print("="*60)
    print(f"🏆 Best Validation Accuracy: {best_val_acc:.2f}%")
    print(f"📁 Model saved at: {model_path}")
    
    # Load best model for testing
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # Test on sample images
    print("\n🔍 Testing on sample validation images...")
    test_model(model, val_dataset)
    
    return model


# ============================================================
# TEST FUNCTION
# ============================================================
def test_model(model, dataset, num_samples=5):
    """Test the model on random samples"""
    model.eval()
    
    class_names = ['Garbage', 'Pothole']
    
    num_samples = min(num_samples, len(dataset))
    if num_samples == 0:
        print("  No validation samples available")
        return
    
    indices = np.random.choice(len(dataset), num_samples, replace=False)
    correct = 0
    
    with torch.no_grad():
        for idx in indices:
            image, label = dataset[idx]
            if isinstance(image, torch.Tensor):
                image_tensor = image.unsqueeze(0).to(device)
            else:
                continue
            
            outputs = model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            predicted = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted].item()
            
            is_correct = (predicted == label)
            if is_correct:
                correct += 1
            
            print(f"\n  🖼️ Image {idx+1}:")
            print(f"     True: {class_names[label]}")
            print(f"     Predicted: {class_names[predicted]} ({confidence*100:.1f}%)")
            print(f"     {'✅ Correct' if is_correct else '❌ Wrong'}")
    
    print(f"\n  📊 Test Accuracy: {correct/num_samples*100:.1f}% ({correct}/{num_samples})")


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    start_time = time.time()
    train_model()
    total_time = time.time() - start_time
    print(f"\n⏱️ Total training time: {total_time/60:.1f} minutes")