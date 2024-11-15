import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from PIL import Image
import numpy as np

class ImageClassifier:
    def __init__(self, train_folder, test_folder, val_split=0.2, seed=42):
        self.seed = seed
        np.random.seed(self.seed)
        torch.manual_seed(self.seed)
        torch.cuda.manual_seed_all(self.seed)

        self.train_folder = train_folder
        self.test_folder = test_folder
        self.val_split = val_split
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Data Preparation
        self.data_transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
        ])

        # Model Definition
        self.model = models.resnet18(pretrained=True)
        num_ftrs = self.model.fc.in_features
        self.model.fc = nn.Linear(num_ftrs, 10)  # Two output units for cat and dog
        self.model = self.model.to(self.device)

        # Training Setup
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.SGD(self.model.parameters(), lr=0.001, momentum=0.9)

    def train(self, num_epochs=50):
        dataset = datasets.ImageFolder(self.train_folder, transform=self.data_transform)
        train_size = int((1 - self.val_split) * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
        train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=32, shuffle=True)

        for epoch in range(num_epochs):
            self.model.train()
            for inputs, labels in train_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                self.optimizer.zero_grad()
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()
            print(f"Epoch {epoch+1}/{num_epochs}, Loss: {loss.item()}")

            # Validation
            self.model.eval()
            val_loader = torch.utils.data.DataLoader(val_dataset, batch_size=32, shuffle=False)
            with torch.no_grad():
                val_loss = 0.0
                for inputs, labels in val_loader:
                    inputs, labels = inputs.to(self.device), labels.to(self.device)
                    outputs = self.model(inputs)
                    val_loss += self.criterion(outputs, labels).item()
                val_loss /= len(val_loader)
                print(f"Validation Loss: {val_loss}")

    def test(self):
        test_dataset = datasets.ImageFolder(self.test_folder, transform=self.data_transform)
        test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=32, shuffle=False)

        self.model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        accuracy = correct / total
        print(f"Accuracy on cat images: {accuracy}")

    def predict(self, image_path):
        image = Image.open(image_path)
        input_tensor = self.data_transform(image).unsqueeze(0).to(self.device)
        self.model.eval()
        with torch.no_grad():
            output = self.model(input_tensor)
        _, predicted_idx = torch.max(output, 1)
        labels = ['cat', 'dog']
        predicted_label = labels[predicted_idx.item()]
        return predicted_label

# Example usage
classifier = ImageClassifier('C:/Users/reese/OneDrive/Documents/Research/Mom project 1/Python Code/imagenette2/train',
                             'C:/Users/reese/OneDrive/Documents/Research/Mom project 1/Python Code/imagenette2/val')
classifier.train()
classifier.test()
#predicted_label = classifier.predict('path_to_image.jpg')
#print(f"The model predicts this is a: {predicted_label}")
