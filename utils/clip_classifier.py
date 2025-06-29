import torch
import clip
from PIL import Image
import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity

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
        
        # Cores disponíveis para roupas
        self.colors = [
            "red", "blue", "green", "yellow", "black", "white", "gray", "brown", 
            "pink", "purple", "orange", "navy", "beige", "cream", "maroon", "olive"
        ]
        
        # Categorias padronizadas: (category_id, name_pt, prompt_en, body_region)
        self.categories = [
            (0, "Camiseta", "t-shirt", "torso"),
            (1, "Calça", "pants", "legs"),
            (2, "Shorts", "shorts", "legs"),
            (3, "Jaqueta", "jacket", "torso"),
            (4, "Blusa", "blouse", "torso"),
            (5, "Saia", "skirt", "legs"),
            (6, "Suéter", "sweater", "torso"),
            (7, "Moletom", "hoodie", "torso"),
            (8, "Casaco", "coat", "torso"),
            (9, "Terno", "suit", "torso"),
            (10, "Maiô", "swimsuit", "full_body"),
            (11, "Roupa Íntima", "underwear", "underwear"),
            (12, "Meias", "socks", "feet"),
            (13, "Sapatos", "shoes", "feet"),
            (14, "Botas", "boots", "feet"),
            (15, "Sandálias", "sandals", "feet"),
            (16, "Chapéu", "hat", "head"),
            (17, "Boné", "cap", "head"),
            (18, "Cachecol", "scarf", "neck"),
            (19, "Luvas", "gloves", "hands"),
            (20, "Cinto", "belt", "waist"),
            (21, "Bolsa", "bag", "accessory"),
            (22, "Mochila", "backpack", "accessory")
        ]
        
        # Extrai apenas os prompts em inglês para o modelo CLIP
        self.classes = [category[2] for category in self.categories]
        
        # Mapeamento de regiões do corpo
        self.body_regions = {
            "torso": ["t-shirt", "jacket", "blouse", "sweater", "hoodie", "coat", "suit"],
            "legs": ["pants", "shorts", "skirt"],
            "feet": ["socks", "shoes", "boots", "sandals"],
            "head": ["hat", "cap"],
            "neck": ["scarf"],
            "hands": ["gloves"],
            "waist": ["belt"],
            "accessory": ["bag", "backpack"],
            "underwear": ["underwear"],
            "full_body": ["swimsuit"]
        }
        
        # Cache para embeddings de texto
        self.text_embeddings = None
        self.color_embeddings = None
        
    def load_model(self):
        """Carrega o modelo CLIP"""
        if self.model is None:
            print(f"🔄 Carregando modelo CLIP ({self.model_name})...")
            self.model, self.preprocess = clip.load(self.model_name, device=self.device)
            print("✅ Modelo CLIP carregado com sucesso!")
            
            # Pré-computar embeddings de texto para compatibilidade
            self._compute_text_embeddings()
            self._compute_color_embeddings()
    
    def _compute_text_embeddings(self):
        """Pré-computa embeddings de texto para todas as categorias"""
        if self.model is None:
            return
            
        print("🔄 Computando embeddings de texto...")
        text = clip.tokenize(self.classes).to(self.device)
        
        with torch.no_grad():
            self.text_embeddings = self.model.encode_text(text).cpu().numpy()
        
        print("✅ Embeddings de texto computados!")
    
    def _compute_color_embeddings(self):
        """Pré-computa embeddings para cores"""
        if self.model is None:
            return
            
        print("🔄 Computando embeddings de cores...")
        color_prompts = [f"{color} color" for color in self.colors]
        text = clip.tokenize(color_prompts).to(self.device)
        
        with torch.no_grad():
            self.color_embeddings = self.model.encode_text(text).cpu().numpy()
        
        print("✅ Embeddings de cores computados!")
    
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
        for i, (category_id, name_pt, prompt_en, body_region) in enumerate(self.categories):
            prob = probs[i]
            classifications.append({
                "category": category_id,
                "name": name_pt,
                "prompt": prompt_en,
                "body_region": body_region,
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
            "prompt": classifications[0]["prompt"],
            "body_region": classifications[0]["body_region"],
            "probability": classifications[0]["probability"],
            "percentage": classifications[0]["percentage"]
        }
    
    def get_compatible_items(self, selected_item: Dict, target_regions: List[str] = None, 
                           top_k: int = 5) -> Dict[str, List[Dict]]:
        """
        Encontra itens compatíveis com base na peça selecionada
        
        Args:
            selected_item: Item selecionado (deve ter 'prompt', 'body_region' e opcionalmente 'color')
            target_regions: Regiões do corpo para buscar (ex: ['torso', 'feet'])
            top_k: Número de sugestões por região
            
        Returns:
            Dicionário com sugestões por região
        """
        if self.text_embeddings is None:
            raise RuntimeError("Embeddings de texto não foram computados. Chame load_model() primeiro.")
        
        # Encontrar índice do item selecionado
        selected_idx = None
        for i, (_, _, prompt_en, _) in enumerate(self.categories):
            if prompt_en == selected_item["prompt"]:
                selected_idx = i
                break
        
        if selected_idx is None:
            raise ValueError(f"Item '{selected_item['prompt']}' não encontrado nas categorias")
        
        # Embedding do item selecionado
        selected_embedding = self.text_embeddings[selected_idx].reshape(1, -1)
        
        # Se uma cor foi especificada no selected_item, combinar com o embedding da cor
        color = selected_item.get("color")
        if color and color.lower() in self.colors:
            color_idx = self.colors.index(color.lower())
            color_embedding = self.color_embeddings[color_idx].reshape(1, -1)
            
            # Combinar embeddings (média ponderada: 70% item + 30% cor)
            combined_embedding = 0.7 * selected_embedding + 0.3 * color_embedding
        else:
            combined_embedding = selected_embedding
        
        # Calcular similaridade com todos os outros itens
        similarities = cosine_similarity(combined_embedding, self.text_embeddings)[0]
        
        # Se há uma cor selecionada, também calcular compatibilidade de cores
        compatible_colors = []
        if color and color.lower() in self.colors:
            # Calcular similaridade entre a cor selecionada e outras cores
            color_similarities = cosine_similarity(color_embedding, self.color_embeddings)[0]
            
            # Encontrar cores mais compatíveis (excluindo a própria cor)
            color_indices = [(i, sim) for i, sim in enumerate(color_similarities) if i != color_idx]
            color_indices.sort(key=lambda x: x[1], reverse=True)
            
            # Pegar as top 5 cores mais compatíveis
            compatible_colors = [
                {
                    "color": self.colors[idx],
                    "similarity": float(sim)
                }
                for idx, sim in color_indices[:5]
            ]
        
        # Filtrar por regiões do corpo se especificado
        if target_regions:
            filtered_items = []
            for i, (category_id, name_pt, prompt_en, body_region) in enumerate(self.categories):
                if body_region in target_regions and i != selected_idx:
                    item_data = {
                        "category": category_id,
                        "name": name_pt,
                        "prompt": prompt_en,
                        "body_region": body_region,
                        "similarity": float(similarities[i])
                    }
                    
                    # Se há cores compatíveis, adicionar sugestões de cores para este item
                    if compatible_colors:
                        item_data["compatible_colors"] = compatible_colors
                    
                    filtered_items.append(item_data)
        else:
            # Incluir todos os itens exceto o selecionado
            filtered_items = []
            for i, (category_id, name_pt, prompt_en, body_region) in enumerate(self.categories):
                if i != selected_idx:
                    item_data = {
                        "category": category_id,
                        "name": name_pt,
                        "prompt": prompt_en,
                        "body_region": body_region,
                        "similarity": float(similarities[i])
                    }
                    
                    # Se há cores compatíveis, adicionar sugestões de cores para este item
                    if compatible_colors:
                        item_data["compatible_colors"] = compatible_colors
                    
                    filtered_items.append(item_data)
        
        # Ordenar por similaridade
        filtered_items.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Agrupar por região do corpo
        suggestions = {}
        for item in filtered_items:
            region = item["body_region"]
            if region not in suggestions:
                suggestions[region] = []
            if len(suggestions[region]) < top_k:
                suggestions[region].append(item)
        
        return suggestions
    
    def get_color_compatibility(self, color: str, target_regions: List[str] = None, top_k: int = 5) -> Dict[str, List[Dict]]:
        """
        Encontra itens que combinam com uma cor específica
        
        Args:
            color: Cor para buscar compatibilidade (ex: 'red', 'blue')
            target_regions: Regiões do corpo para buscar
            top_k: Número de sugestões por região
            
        Returns:
            Dicionário com sugestões por região
        """
        if self.color_embeddings is None:
            raise RuntimeError("Embeddings de cores não foram computados. Chame load_model() primeiro.")
        
        if color.lower() not in self.colors:
            raise ValueError(f"Cor '{color}' não está disponível. Cores disponíveis: {self.colors}")
        
        color_idx = self.colors.index(color.lower())
        color_embedding = self.color_embeddings[color_idx].reshape(1, -1)
        
        # Calcular similaridade com todos os itens
        similarities = cosine_similarity(color_embedding, self.text_embeddings)[0]
        
        # Filtrar por regiões do corpo se especificado
        if target_regions:
            filtered_items = []
            for i, (category_id, name_pt, prompt_en, body_region) in enumerate(self.categories):
                if body_region in target_regions:
                    filtered_items.append({
                        "category": category_id,
                        "name": name_pt,
                        "prompt": prompt_en,
                        "body_region": body_region,
                        "similarity": float(similarities[i])
                    })
        else:
            # Incluir todos os itens
            filtered_items = []
            for i, (category_id, name_pt, prompt_en, body_region) in enumerate(self.categories):
                filtered_items.append({
                    "category": category_id,
                    "name": name_pt,
                    "prompt": prompt_en,
                    "body_region": body_region,
                    "similarity": float(similarities[i])
                })
        
        # Ordenar por similaridade
        filtered_items.sort(key=lambda x: x["similarity"], reverse=True)
        
        # Agrupar por região do corpo
        suggestions = {}
        for item in filtered_items:
            region = item["body_region"]
            if region not in suggestions:
                suggestions[region] = []
            if len(suggestions[region]) < top_k:
                suggestions[region].append(item)
        
        return suggestions
    
    def get_outfit_suggestions(self, selected_items: List[Dict], top_k: int = 3) -> Dict[str, List[Dict]]:
        """
        Sugere um outfit completo baseado nos itens selecionados
        
        Args:
            selected_items: Lista de itens já selecionados
            top_k: Número de sugestões por região
            
        Returns:
            Dicionário com sugestões para completar o outfit
        """
        # Definir regiões principais para um outfit
        main_regions = ["torso", "legs", "feet"]
        
        # Encontrar regiões que ainda precisam ser preenchidas
        selected_regions = {item["body_region"] for item in selected_items}
        missing_regions = [region for region in main_regions if region not in selected_regions]
        
        if not missing_regions:
            return {"message": "Outfit já está completo!"}
        
        # Usar o item com maior similaridade como referência
        best_item = max(selected_items, key=lambda x: x.get("probability", 0))
        
        # Buscar itens compatíveis para as regiões faltantes
        suggestions = self.get_compatible_items(best_item, missing_regions, top_k)
        
        return {
            "selected_items": selected_items,
            "missing_regions": missing_regions,
            "suggestions": suggestions
        }
    
    def get_device_info(self) -> str:
        """Retorna informações sobre o dispositivo usado"""
        return self.device
    
    def analyze_outfit_compatibility(self, classified_parts: Dict) -> Dict:
        """
        Analisa a compatibilidade entre as peças detectadas em um outfit
        
        Args:
            classified_parts: Dicionário com classificações por parte do corpo
                {
                    "torso": {"top_prediction": {...}},
                    "legs": {"top_prediction": {...}},
                    "feet": {"top_prediction": {...}}
                }
            
        Returns:
            Dicionário com análise de compatibilidade
        """
        if not classified_parts:
            return {"error": "Nenhuma peça classificada"}
        
        # Mapear regiões principais para análise
        main_regions = ["torso", "legs", "feet"]
        detected_parts = {}
        
        # Extrair informações das peças detectadas
        for region in main_regions:
            if region in classified_parts and "top_prediction" in classified_parts[region]:
                detected_parts[region] = classified_parts[region]["top_prediction"]
        
        if len(detected_parts) < 2:
            return {
                "compatibility_score": 0.0,
                "message": "Poucas peças detectadas para análise de compatibilidade",
                "detected_parts": detected_parts
            }
        
        # Calcular compatibilidade entre as peças
        compatibility_scores = {}
        total_score = 0.0
        comparisons = 0
        
        # Comparar cada par de peças
        regions = list(detected_parts.keys())
        for i in range(len(regions)):
            for j in range(i + 1, len(regions)):
                region1, region2 = regions[i], regions[j]
                part1, part2 = detected_parts[region1], detected_parts[region2]
                
                # Calcular similaridade entre as duas peças
                similarity = self._calculate_part_compatibility(part1, part2)
                
                comparison_key = f"{region1}_vs_{region2}"
                compatibility_scores[comparison_key] = {
                    "part1": {
                        "region": region1,
                        "name": part1["name"],
                        "prompt": part1["prompt"]
                    },
                    "part2": {
                        "region": region2,
                        "name": part2["name"],
                        "prompt": part2["prompt"]
                    },
                    "similarity": similarity,
                    "compatibility_level": self._get_compatibility_level(similarity)
                }
                
                total_score += similarity
                comparisons += 1
        
        # Calcular score médio de compatibilidade
        avg_compatibility = total_score / comparisons if comparisons > 0 else 0.0
        
        # Determinar se o outfit combina
        outfit_rating = self._get_outfit_rating(avg_compatibility)
        
        # Sugestões de melhoria
        suggestions = self._generate_outfit_suggestions(detected_parts, compatibility_scores)
        
        return {
            "compatibility_score": round(avg_compatibility, 3),
            "outfit_rating": outfit_rating,
            "detected_parts": detected_parts,
            "pairwise_compatibility": compatibility_scores,
            "suggestions": suggestions,
            "total_comparisons": comparisons
        }
    
    def _calculate_part_compatibility(self, part1: Dict, part2: Dict) -> float:
        """
        Calcula a compatibilidade entre duas peças de roupa
        
        Args:
            part1, part2: Dicionários com informações das peças
            
        Returns:
            Score de compatibilidade entre 0 e 1
        """
        if self.text_embeddings is None:
            return 0.5  # Valor neutro se embeddings não estiverem disponíveis
        
        # Encontrar índices das peças
        idx1 = None
        idx2 = None
        
        for i, (_, _, prompt_en, _) in enumerate(self.categories):
            if prompt_en == part1["prompt"]:
                idx1 = i
            if prompt_en == part2["prompt"]:
                idx2 = i
        
        if idx1 is None or idx2 is None:
            return 0.5
        
        # Calcular similaridade entre os embeddings
        embedding1 = self.text_embeddings[idx1].reshape(1, -1)
        embedding2 = self.text_embeddings[idx2].reshape(1, -1)
        
        similarity = cosine_similarity(embedding1, embedding2)[0][0]
        return float(similarity)
    
    def _get_compatibility_level(self, similarity: float) -> str:
        """Converte score de similaridade em nível de compatibilidade"""
        if similarity >= 0.8:
            return "Excelente"
        elif similarity >= 0.6:
            return "Boa"
        elif similarity >= 0.4:
            return "Regular"
        else:
            return "Baixa"
    
    def _get_outfit_rating(self, avg_compatibility: float) -> Dict:
        """Determina a avaliação geral do outfit"""
        if avg_compatibility >= 0.8:
            return {
                "level": "Excelente",
                "emoji": "🌟",
                "description": "Outfit muito bem combinado! As peças harmonizam perfeitamente."
            }
        elif avg_compatibility >= 0.6:
            return {
                "level": "Bom",
                "emoji": "👍",
                "description": "Outfit bem combinado. As peças funcionam bem juntas."
            }
        elif avg_compatibility >= 0.4:
            return {
                "level": "Regular",
                "emoji": "🤔",
                "description": "Outfit com compatibilidade média. Algumas peças podem ser melhoradas."
            }
        else:
            return {
                "level": "Baixo",
                "emoji": "⚠️",
                "description": "Outfit com baixa compatibilidade. Considere trocar algumas peças."
            }
    
    def _generate_outfit_suggestions(self, detected_parts: Dict, compatibility_scores: Dict) -> List[str]:
        """Gera sugestões para melhorar o outfit usando CLIP"""
        suggestions = []
        
        # Analisar pares com baixa compatibilidade
        low_compatibility_pairs = [
            (key, data) for key, data in compatibility_scores.items()
            if data["similarity"] < 0.4
        ]
        
        for pair_key, pair_data in low_compatibility_pairs:
            part1_name = pair_data["part1"]["name"]
            part2_name = pair_data["part2"]["name"]
            
            suggestions.append(
                f"Considere trocar o {part1_name} ou {part2_name} por uma peça mais compatível"
            )
        
        # Gerar sugestões contextuais usando CLIP
        contextual_suggestions = self._generate_contextual_suggestions(detected_parts)
        suggestions.extend(contextual_suggestions)
        
        return suggestions[:3]  # Limitar a 3 sugestões
    
    def _generate_contextual_suggestions(self, detected_parts: Dict) -> List[str]:
        """Gera sugestões contextuais baseadas nas peças detectadas usando CLIP"""
        if self.text_embeddings is None:
            return []
        
        suggestions = []
        detected_regions = list(detected_parts.keys())
        detected_items = [part["prompt"] for part in detected_parts.values()]
        
        # Definir prompts para diferentes cenários
        suggestion_prompts = []
        
        # Se tem apenas 2 peças, sugerir terceira peça
        if len(detected_parts) == 2:
            missing_regions = [r for r in ["torso", "legs", "feet"] if r not in detected_regions]
            if missing_regions:
                for region in missing_regions:
                    if region == "torso":
                        suggestion_prompts.append("blouse")
                        suggestion_prompts.append("sweater")
                    elif region == "legs":
                        suggestion_prompts.append("pants")
                        suggestion_prompts.append("skirt")
                    elif region == "feet":
                        suggestion_prompts.append("shoes")
                        suggestion_prompts.append("boots")
        
        # Se tem 3+ peças, sugerir acessórios
        elif len(detected_parts) >= 3:
            # Verificar se é um outfit mais formal
            formal_items = ["suit", "coat", "shoes"]
            is_formal = any(item in detected_items for item in formal_items)
            
            if is_formal:
                suggestion_prompts.extend(["belt", "hat", "scarf"])
            else:
                suggestion_prompts.extend(["bag", "cap", "backpack"])
        
        # Calcular compatibilidade com as peças existentes
        if suggestion_prompts and detected_items:
            # Encontrar embeddings das peças detectadas
            detected_indices = []
            for item in detected_items:
                for i, (_, _, prompt_en, _) in enumerate(self.categories):
                    if prompt_en == item:
                        detected_indices.append(i)
                        break
            
            if detected_indices:
                # Calcular embedding médio das peças detectadas
                detected_embeddings = self.text_embeddings[detected_indices]
                avg_detected_embedding = detected_embeddings.mean(axis=0).reshape(1, -1)
                
                # Encontrar embeddings das sugestões
                suggestion_indices = []
                for prompt in suggestion_prompts:
                    for i, (_, _, prompt_en, _) in enumerate(self.categories):
                        if prompt_en == prompt:
                            suggestion_indices.append(i)
                            break
                
                if suggestion_indices:
                    # Calcular similaridade entre peças detectadas e sugestões
                    suggestion_embeddings = self.text_embeddings[suggestion_indices]
                    similarities = cosine_similarity(avg_detected_embedding, suggestion_embeddings)[0]
                    
                    # Pegar as 3 sugestões mais compatíveis
                    best_suggestions = []
                    for i, similarity in enumerate(similarities):
                        if similarity > 0.5:  # Threshold mínimo de compatibilidade
                            suggestion_idx = suggestion_indices[i]
                            category_name = self.categories[suggestion_idx][1]  # Nome em português
                            best_suggestions.append((category_name, similarity))
                    
                    # Ordenar por similaridade e adicionar sugestões
                    best_suggestions.sort(key=lambda x: x[1], reverse=True)
                    for item_name, similarity in best_suggestions[:2]:
                        if len(detected_parts) == 2:
                            suggestions.append(f"Adicionar um {item_name} pode completar o look")
                        else:
                            suggestions.append(f"Um {item_name} pode complementar o outfit")
        
        # Se não conseguiu gerar sugestões contextuais, usar sugestões baseadas em regras
        if not suggestions:
            if len(detected_parts) == 2:
                suggestions.append("Adicionar uma terceira peça pode melhorar o conjunto")
            elif len(detected_parts) >= 3:
                suggestions.append("O outfit está completo! Considere acessórios para complementar")
        
        return suggestions

    def analyze_complete_outfit_image(self, full_image: Image.Image, classified_parts: Dict) -> Dict:
        """
        Analisa o outfit completo usando a imagem inteira com CLIP
        
        Args:
            full_image: Imagem completa da pessoa
            classified_parts: Classificações das partes individuais
            
        Returns:
            Dicionário com análise completa do outfit
        """
        if self.model is None:
            return {"error": "Modelo CLIP não carregado"}
        
        # Garantir que a imagem seja RGB
        full_image = self._ensure_rgb_image(full_image)
        
        # Pré-processar a imagem para o CLIP
        processed_image = self.preprocess(full_image).unsqueeze(0).to(self.device)
        
        # Prompts mais simples e diretos para avaliação de outfit
        style_prompts = [
            "formal clothing",
            "casual clothing", 
            "elegant clothing",
            "trendy clothing",
            "classic clothing",
            "modern clothing"
        ]
        
        coordination_prompts = [
            "well coordinated",
            "color coordinated",
            "matching clothes",
            "harmonious outfit",
            "balanced outfit",
            "stylish outfit"
        ]
        
        # Analisar estilo
        style_scores = self._analyze_style_with_clip(processed_image, style_prompts)
        
        # Analisar coordenação
        coordination_scores = self._analyze_coordination_with_clip(processed_image, coordination_prompts)
        
        # Determinar estilo dominante
        dominant_style = max(style_scores.items(), key=lambda x: x[1])
        
        # Calcular score geral de coordenação (usar o maior valor)
        max_coordination = max(coordination_scores.values())
        
        # Determinar avaliação geral
        overall_rating = self._get_overall_outfit_rating(max_coordination, dominant_style)
        
        # Gerar insights específicos
        insights = self._generate_outfit_insights(style_scores, coordination_scores)
        
        return {
            "full_image_analysis": {
                "overall_rating": overall_rating,
                "style_analysis": {
                    "dominant_style": dominant_style[0],
                    "style_confidence": dominant_style[1],
                    "all_style_scores": style_scores
                },
                "coordination_analysis": {
                    "coordination_score": round(max_coordination, 3),
                    "all_coordination_scores": coordination_scores
                },
                "insights": insights
            },
            "individual_parts_analysis": self.analyze_outfit_compatibility(classified_parts)
        }
    
    def _analyze_style_with_clip(self, processed_image, style_prompts):
        """Analisa o estilo usando CLIP com prompts específicos"""
        text = clip.tokenize(style_prompts).to(self.device)
        
        with torch.no_grad():
            image_features = self.model.encode_image(processed_image)
            text_features = self.model.encode_text(text)
            logits_per_image, _ = self.model(processed_image, text)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
        
        # Normalizar e mapear scores
        style_scores = {}
        for i, (prompt, prob) in enumerate(zip(style_prompts, probs)):
            # Normalizar para 0-1 e aplicar boost para scores mais altos
            normalized_score = min(prob * 2.0, 1.0)  # Boost scores baixos
            style_scores[prompt.replace(" clothing", "")] = float(normalized_score)
        
        return style_scores
    
    def _analyze_coordination_with_clip(self, processed_image, coordination_prompts):
        """Analisa a coordenação usando CLIP com prompts específicos"""
        text = clip.tokenize(coordination_prompts).to(self.device)
        
        with torch.no_grad():
            image_features = self.model.encode_image(processed_image)
            text_features = self.model.encode_text(text)
            logits_per_image, _ = self.model(processed_image, text)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
        
        # Normalizar e mapear scores
        coordination_scores = {}
        for i, (prompt, prob) in enumerate(zip(coordination_prompts, probs)):
            # Normalizar para 0-1 e aplicar boost para scores mais altos
            normalized_score = min(prob * 2.0, 1.0)  # Boost scores baixos
            
            # Mapear para nomes mais amigáveis
            if "well coordinated" in prompt:
                key = "well_coordinated"
            elif "color coordinated" in prompt:
                key = "color_coordinated"
            elif "matching clothes" in prompt:
                key = "matching"
            elif "harmonious outfit" in prompt:
                key = "harmonious"
            elif "balanced outfit" in prompt:
                key = "balanced"
            elif "stylish outfit" in prompt:
                key = "stylish"
            else:
                key = prompt.replace(" ", "_")
            
            coordination_scores[key] = float(normalized_score)
        
        return coordination_scores
    
    def _get_overall_outfit_rating(self, coordination_score: float, dominant_style: tuple) -> Dict:
        """Determina a avaliação geral do outfit baseada na imagem completa"""
        style_name, style_confidence = dominant_style
        
        if coordination_score >= 0.8:
            level = "Excelente"
            emoji = "🌟"
            description = f"Outfit {style_name} muito bem coordenado! Todas as peças harmonizam perfeitamente."
        elif coordination_score >= 0.6:
            level = "Bom"
            emoji = "👍"
            description = f"Outfit {style_name} bem coordenado. As peças funcionam bem juntas."
        elif coordination_score >= 0.4:
            level = "Regular"
            emoji = "🤔"
            description = f"Outfit {style_name} com coordenação média. Algumas peças podem ser melhoradas."
        else:
            level = "Baixo"
            emoji = "⚠️"
            description = f"Outfit {style_name} com baixa coordenação. Considere trocar algumas peças."
        
        return {
            "level": level,
            "emoji": emoji,
            "description": description,
            "coordination_score": round(coordination_score, 3),
            "dominant_style": style_name,
            "style_confidence": round(style_confidence, 3)
        }
    
    def _generate_outfit_insights(self, style_scores: Dict, coordination_scores: Dict) -> List[str]:
        """Gera insights específicos sobre o outfit"""
        insights = []
        
        # Insights sobre estilo
        if style_scores["formal"] > 0.6:
            insights.append("Look adequado para ocasiões formais")
        elif style_scores["casual"] > 0.6:
            insights.append("Look perfeito para o dia a dia")
        
        if style_scores["elegant"] > 0.7:
            insights.append("Outfit com toque elegante")
        
        if style_scores["trendy"] > 0.6:
            insights.append("Look atual e na moda")
        
        # Insights sobre coordenação
        if coordination_scores["well_coordinated"] > 0.7:
            insights.append("As peças estão muito bem coordenadas")
        elif coordination_scores["well_coordinated"] < 0.3:
            insights.append("As peças precisam de melhor coordenação")
        
        if coordination_scores["color_coordinated"] > 0.7:
            insights.append("As cores estão harmoniosas")
        elif coordination_scores["color_coordinated"] < 0.3:
            insights.append("Considere melhorar a combinação de cores")
        
        return insights[:3]  # Limitar a 3 insights

    def detect_clothing_color(self, image: Image.Image) -> Dict:
        """
        Detecta a cor predominante de uma peça de roupa
        
        Args:
            image: Imagem da peça de roupa
            
        Returns:
            Dicionário com informações da cor detectada
        """
        if self.model is None:
            return {"error": "Modelo CLIP não carregado"}
        
        # Garantir que a imagem seja RGB
        image = self._ensure_rgb_image(image)
        
        # 1. Análise de cores usando processamento de imagem
        color_analysis = self._analyze_image_colors(image)
        
        # 2. Análise usando CLIP com prompts de cores
        clip_color_analysis = self._analyze_colors_with_clip(image)
        
        # 3. Combinar resultados
        combined_result = self._combine_color_analyses(color_analysis, clip_color_analysis)
        
        return combined_result
    
    def _analyze_image_colors(self, image: Image.Image) -> Dict:
        """Analisa cores usando processamento de imagem tradicional"""
        import numpy as np
        from collections import Counter
        
        # Converter para array numpy
        img_array = np.array(image)
        
        # Reshape para lista de pixels
        pixels = img_array.reshape(-1, 3)
        
        # Definir cores de referência
        reference_colors = {
            'red': [255, 0, 0],
            'blue': [0, 0, 255],
            'green': [0, 255, 0],
            'yellow': [255, 255, 0],
            'black': [0, 0, 0],
            'white': [255, 255, 255],
            'gray': [128, 128, 128],
            'brown': [139, 69, 19],
            'pink': [255, 192, 203],
            'purple': [128, 0, 128],
            'orange': [255, 165, 0],
            'navy': [0, 0, 128],
            'beige': [245, 245, 220],
            'cream': [255, 253, 208],
            'maroon': [128, 0, 0],
            'olive': [128, 128, 0]
        }
        
        # Calcular distância para cada cor de referência
        color_counts = {}
        for color_name, ref_color in reference_colors.items():
            distances = np.sqrt(np.sum((pixels - ref_color) ** 2, axis=1))
            # Contar pixels próximos desta cor (threshold de 100)
            close_pixels = np.sum(distances < 100)
            color_counts[color_name] = close_pixels
        
        # Encontrar a cor predominante
        if color_counts:
            dominant_color = max(color_counts.items(), key=lambda x: x[1])
            total_pixels = len(pixels)
            percentage = (dominant_color[1] / total_pixels) * 100
            
            return {
                "dominant_color": dominant_color[0],
                "confidence": min(percentage / 50, 1.0),  # Normalizar para 0-1
                "all_colors": color_counts
            }
        
        return {"dominant_color": "unknown", "confidence": 0.0, "all_colors": {}}
    
    def _analyze_colors_with_clip(self, image: Image.Image) -> Dict:
        """Analisa cores usando CLIP"""
        # Pré-processar a imagem
        processed_image = self.preprocess(image).unsqueeze(0).to(self.device)
        
        # Prompts de cores
        color_prompts = [
            f"{color} colored clothing" for color in self.colors
        ]
        
        # Tokenizar e inferir
        text = clip.tokenize(color_prompts).to(self.device)
        
        with torch.no_grad():
            image_features = self.model.encode_image(processed_image)
            text_features = self.model.encode_text(text)
            logits_per_image, _ = self.model(processed_image, text)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
        
        # Encontrar a cor com maior probabilidade
        color_scores = {}
        for i, (prompt, prob) in enumerate(zip(color_prompts, probs)):
            color_name = self.colors[i]
            color_scores[color_name] = float(prob)
        
        if color_scores:
            dominant_color = max(color_scores.items(), key=lambda x: x[1])
            return {
                "dominant_color": dominant_color[0],
                "confidence": dominant_color[1],
                "all_colors": color_scores
            }
        
        return {"dominant_color": "unknown", "confidence": 0.0, "all_colors": {}}
    
    def _combine_color_analyses(self, image_analysis: Dict, clip_analysis: Dict) -> Dict:
        """Combina análises de cores de imagem e CLIP"""
        # Peso para cada método (CLIP tem mais peso por ser mais inteligente)
        clip_weight = 0.7
        image_weight = 0.3
        
        # Se ambos detectaram a mesma cor, aumentar confiança
        if (image_analysis["dominant_color"] == clip_analysis["dominant_color"] and 
            image_analysis["dominant_color"] != "unknown"):
            
            combined_confidence = (
                clip_analysis["confidence"] * clip_weight + 
                image_analysis["confidence"] * image_weight
            )
            
            return {
                "dominant_color": clip_analysis["dominant_color"],
                "confidence": min(combined_confidence * 1.2, 1.0),  # Boost se concordam
                "detection_method": "combined",
                "clip_confidence": clip_analysis["confidence"],
                "image_confidence": image_analysis["confidence"],
                "all_colors": clip_analysis["all_colors"]
            }
        
        # Se discordam, usar o CLIP (mais confiável)
        return {
            "dominant_color": clip_analysis["dominant_color"],
            "confidence": clip_analysis["confidence"],
            "detection_method": "clip_only",
            "clip_confidence": clip_analysis["confidence"],
            "image_confidence": image_analysis["confidence"],
            "all_colors": clip_analysis["all_colors"]
        }

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

def get_compatible_items(selected_item: Dict, target_regions: List[str] = None, 
                        top_k: int = 5) -> Dict[str, List[Dict]]:
    """
    Função utilitária para encontrar itens compatíveis
    
    Args:
        selected_item: Item selecionado
        target_regions: Regiões do corpo para buscar
        top_k: Número de sugestões por região
        
    Returns:
        Dicionário com sugestões por região
    """
    return classifier.get_compatible_items(selected_item, target_regions, top_k)

def get_color_compatibility(color: str, target_regions: List[str] = None, top_k: int = 5) -> Dict[str, List[Dict]]:
    """
    Função utilitária para encontrar itens que combinam com uma cor
    
    Args:
        color: Cor para buscar compatibilidade
        target_regions: Regiões do corpo para buscar
        top_k: Número de sugestões por região
        
    Returns:
        Dicionário com sugestões por região
    """
    return classifier.get_color_compatibility(color, target_regions, top_k)

def get_outfit_suggestions(selected_items: List[Dict], top_k: int = 3) -> Dict[str, List[Dict]]:
    """
    Função utilitária para sugerir outfit completo
    
    Args:
        selected_items: Lista de itens selecionados
        top_k: Número de sugestões por região
        
    Returns:
        Dicionário com sugestões para completar o outfit
    """
    return classifier.get_outfit_suggestions(selected_items, top_k)

def get_device_info() -> str:
    """Retorna informações sobre o dispositivo usado"""
    return classifier.get_device_info()

def analyze_outfit_compatibility(classified_parts: Dict) -> Dict:
    """
    Função utilitária para analisar compatibilidade de outfit
    
    Args:
        classified_parts: Dicionário com classificações por parte do corpo
        
    Returns:
        Dicionário com análise de compatibilidade
    """
    return classifier.analyze_outfit_compatibility(classified_parts)

def analyze_complete_outfit_image(full_image: Image.Image, classified_parts: Dict) -> Dict:
    """
    Analisa o outfit completo usando a imagem inteira com CLIP
    
    Args:
        full_image: Imagem completa da pessoa
        classified_parts: Classificações das partes individuais
        
    Returns:
        Dicionário com análise completa do outfit
    """
    return classifier.analyze_complete_outfit_image(full_image, classified_parts)

def detect_clothing_color(image: Image.Image) -> Dict:
    """
    Detecta a cor predominante de uma peça de roupa
    
    Args:
        image: Imagem da peça de roupa
        
    Returns:
        Dicionário com informações da cor detectada
    """
    return classifier.detect_clothing_color(image) 