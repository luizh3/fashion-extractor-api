import torch
import clip
from PIL import Image
import numpy as np
from typing import List, Dict, Tuple

class CLIPClassifier:
    """Classe para classificação de roupas usando modelo CLIP"""
    
    def __init__(self, model_name: str = "ViT-B/32"):
        """
        Inicializa o classificador CLIP
        
        Args:
            model_name: Nome do modelo CLIP a ser usado
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.model = None
        self.preprocess = None
        
        # Categorias padronizadas: (category_id, name_pt, prompt_en)
        self.categories = [
            (0, "Camiseta", "t-shirt"),
            (1, "Calça", "pants"),
            (2, "Shorts", "shorts"),
            (3, "Jaqueta", "jacket"),
            (4, "Blusa", "blouse"),
            (5, "Saia", "skirt"),
            (6, "Suéter", "sweater"),
            (7, "Moletom", "hoodie"),
            (8, "Casaco", "coat"),
            (9, "Terno", "suit"),
            (10, "Maiô", "swimsuit"),
            (11, "Roupa Íntima", "underwear"),
            (12, "Meias", "socks"),
            (13, "Sapatos", "shoes"),
            (14, "Botas", "boots"),
            (15, "Sandálias", "sandals"),
            (16, "Chapéu", "hat"),
            (17, "Boné", "cap"),
            (18, "Cachecol", "scarf"),
            (19, "Luvas", "gloves"),
            (20, "Cinto", "belt"),
            (21, "Bolsa", "bag"),
            (22, "Mochila", "backpack")
        ]
        
        # Extrai apenas os prompts em inglês para o modelo CLIP
        self.classes = [category[2] for category in self.categories]
        
    def load_model(self):
        """Carrega o modelo CLIP"""
        if self.model is None:
            print(f"🔄 Carregando modelo CLIP ({self.model_name})...")
            self.model, self.preprocess = clip.load(self.model_name, device=self.device)
            print("✅ Modelo CLIP carregado com sucesso!")
    
    def _ensure_rgb_image(self, image: Image.Image) -> Image.Image:
        """
        Garante que a imagem seja RGB
        
        Args:
            image: Imagem PIL
            
        Returns:
            Imagem PIL em formato RGB
        """
        if image.mode == 'RGBA':
            # Converte RGBA para RGB
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            rgb_image.paste(image, mask=image.split()[-1])  # Usa o canal alpha como máscara
            return rgb_image
        elif image.mode != 'RGB':
            # Converte outros formatos para RGB
            return image.convert('RGB')
        else:
            return image
    
    def classify_image(self, image: Image.Image) -> List[Dict[str, any]]:
        """
        Classifica uma imagem de roupa
        
        Args:
            image: Imagem PIL para classificar
            
        Returns:
            Lista de classificações ordenadas por probabilidade
        """
        if self.model is None:
            raise RuntimeError("Modelo não foi carregado. Chame load_model() primeiro.")
        
        # Garante que a imagem seja RGB
        image_rgb = self._ensure_rgb_image(image)
        
        # Pré-processamento da imagem
        processed_image = self.preprocess(image_rgb).unsqueeze(0).to(self.device)
        text = clip.tokenize(self.classes).to(self.device)
        
        # Inferência
        with torch.no_grad():
            image_features = self.model.encode_image(processed_image)
            text_features = self.model.encode_text(text)
            logits_per_image, _ = self.model(processed_image, text)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
        
        # Preparar resultado com categorias padronizadas
        classifications = []
        for i, (category_id, name_pt, _) in enumerate(self.categories):
            prob = probs[i]
            classifications.append({
                "category": category_id,
                "name": name_pt,
                "probability": float(prob),
                "percentage": f"{prob:.2%}"
            })
        
        # Ordenar por probabilidade (maior para menor)
        classifications.sort(key=lambda x: x["probability"], reverse=True)
        
        return classifications
    
    def get_top_prediction(self, classifications: List[Dict]) -> Dict[str, any]:
        """
        Obtém a predição com maior probabilidade
        
        Args:
            classifications: Lista de classificações
            
        Returns:
            Dicionário com a predição principal
        """
        if not classifications:
            raise ValueError("Lista de classificações está vazia")
        
        return {
            "category": classifications[0]["category"],
            "name": classifications[0]["name"],
            "probability": classifications[0]["probability"],
            "percentage": classifications[0]["percentage"]
        }
    
    def get_device_info(self) -> str:
        """Retorna informações sobre o dispositivo usado"""
        return self.device

# Instância global do classificador
classifier = CLIPClassifier()

def load_classifier():
    """Função para carregar o classificador global"""
    classifier.load_model()

def classify_clothing_image(image: Image.Image) -> Tuple[List[Dict], Dict]:
    """
    Função utilitária para classificar uma imagem de roupa
    
    Args:
        image: Imagem PIL para classificar
        
    Returns:
        Tupla com (classificações, predição_principal)
    """
    classifications = classifier.classify_image(image)
    top_prediction = classifier.get_top_prediction(classifications)
    return classifications, top_prediction

def get_device_info() -> str:
    """Retorna informações sobre o dispositivo usado"""
    return classifier.get_device_info() 