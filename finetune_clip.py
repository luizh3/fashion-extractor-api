import open_clip
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import pandas as pd
from tqdm import tqdm
import os

# Configurações
csv_path = 'dataset/fashion_clip_part.csv'
batch_size = 8
num_epochs = 1
lr = 1e-5
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_name = 'ViT-B-32'
pretrained = 'openai'
output_path = 'clip_finetuned_fashion.pth'

# Dataset
class FashionDataset(Dataset):
    def __init__(self, csv_file, transform, tokenizer):
        self.data = pd.read_csv(csv_file)
        self.transform = transform
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path = self.data.iloc[idx, 0]
        text = self.data.iloc[idx, 1]
        img = Image.open(img_path).convert('RGB')
        return self.transform(img), self.tokenizer([text])[0]

# Carregar modelo e preprocessamento
model, _, preprocess = open_clip.create_model_and_transforms(model_name, pretrained=pretrained)
tokenizer = open_clip.get_tokenizer(model_name)
model = model.to(device)

# DataLoader
dataset = FashionDataset(csv_path, preprocess, tokenizer)
loader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)

# Otimizador
optimizer = torch.optim.AdamW(model.parameters(), lr=lr)

# Treinamento
model.train()
for epoch in range(num_epochs):
    total_loss = 0
    for images, texts in tqdm(loader, desc=f"Epoch {epoch+1}/{num_epochs}"):
        images, texts = images.to(device), texts.to(device)
        image_features = model.encode_image(images)
        text_features = model.encode_text(texts)
        logits_per_image = image_features @ text_features.t()
        logits_per_text = text_features @ image_features.t()
        labels = torch.arange(len(images)).to(device)
        loss = (torch.nn.functional.cross_entropy(logits_per_image, labels) +
                torch.nn.functional.cross_entropy(logits_per_text, labels)) / 2
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1} Loss: {total_loss/len(loader):.4f}")

# Salvar modelo
torch.save(model.state_dict(), output_path)
print(f"Modelo salvo como {output_path}") 