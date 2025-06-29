# -*- coding: utf-8 -*-
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
import base64
from typing import Dict, List

from utils.clip_classifier import (
    classify_clothing_image, 
    get_device_info, 
    get_compatible_items, 
    get_outfit_suggestions,
    get_color_compatibility
)
from utils.image_utils import ensure_rgb_image

router = APIRouter(prefix="/api/v1/clothing", tags=["Clothing Classification"])

@router.post("/classify")
async def classify_clothing(file: UploadFile = File(...)):
    """
    Classifica uma imagem de roupa e retorna as probabilidades
    
    Args:
        file: Arquivo de imagem (JPG, PNG, etc.)
    
    Returns:
        JSON com as classificações e probabilidades
    """
    # Validar tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    try:
        # Ler e processar a imagem
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Garantir que a imagem seja RGB
        image = ensure_rgb_image(image)
        
        # Classificar a imagem
        classifications, top_prediction = classify_clothing_image(image)
        
        # Resultado final
        result = {
            "filename": file.filename,
            "file_size": len(image_data),
            "content_type": file.content_type,
            "device_used": get_device_info(),
            "predictions": classifications,
            "top_prediction": top_prediction
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@router.post("/classify/base64")
async def classify_clothing_base64(image_data: Dict[str, str]):
    """
    Classifica uma imagem enviada em formato base64
    
    Args:
        image_data: {"image": "base64_string"}
    
    Returns:
        JSON com as classificações e probabilidades
    """
    if "image" not in image_data:
        raise HTTPException(status_code=400, detail="Campo 'image' com base64 é obrigatório")
    
    try:
        # Decodificar base64
        image_bytes = base64.b64decode(image_data["image"])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Garantir que a imagem seja RGB
        image = ensure_rgb_image(image)
        
        # Classificar a imagem
        classifications, top_prediction = classify_clothing_image(image)
        
        # Resultado final
        result = {
            "predictions": classifications,
            "top_prediction": top_prediction,
            "device_used": get_device_info()
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@router.post("/compatible-items")
async def find_compatible_items(request_data: Dict):
    """
    Encontra itens compatíveis com base em uma peça selecionada
    
    Args:
        request_data: {
            "selected_item": {
                "prompt": "t-shirt",
                "body_region": "torso",
                "name": "Camiseta",
                "color": "red"  # opcional - cor do item
            },
            "target_regions": ["legs", "feet"],  # opcional
            "top_k": 5  # opcional
        }
    
    Returns:
        JSON com sugestões de itens compatíveis por região
    """
    try:
        selected_item = request_data.get("selected_item")
        target_regions = request_data.get("target_regions")
        top_k = request_data.get("top_k", 5)
        
        if not selected_item:
            raise HTTPException(status_code=400, detail="Campo 'selected_item' é obrigatório")
        
        if "prompt" not in selected_item:
            raise HTTPException(status_code=400, detail="Campo 'prompt' é obrigatório no selected_item")
        
        # Buscar itens compatíveis
        suggestions = get_compatible_items(selected_item, target_regions, top_k)
        
        result = {
            "selected_item": selected_item,
            "target_regions": target_regions,
            "top_k": top_k,
            "suggestions": suggestions,
            "device_used": get_device_info()
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar itens compatíveis: {str(e)}")

@router.post("/color-compatibility")
async def find_color_compatibility(request_data: Dict):
    """
    Encontra itens que combinam com uma cor específica
    
    Args:
        request_data: {
            "color": "red",
            "target_regions": ["torso", "legs"],  # opcional
            "top_k": 5  # opcional
        }
    
    Returns:
        JSON com sugestões de itens que combinam com a cor
    """
    try:
        color = request_data.get("color")
        target_regions = request_data.get("target_regions")
        top_k = request_data.get("top_k", 5)
        
        if not color:
            raise HTTPException(status_code=400, detail="Campo 'color' é obrigatório")
        
        # Buscar itens compatíveis com a cor
        suggestions = get_color_compatibility(color, target_regions, top_k)
        
        result = {
            "color": color,
            "target_regions": target_regions,
            "top_k": top_k,
            "suggestions": suggestions,
            "device_used": get_device_info()
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar compatibilidade de cor: {str(e)}")

@router.post("/outfit-suggestions")
async def get_outfit_suggestions_endpoint(request_data: Dict):
    """
    Sugere um outfit completo baseado nos itens selecionados
    
    Args:
        request_data: {
            "selected_items": [
                {
                    "prompt": "t-shirt",
                    "body_region": "torso",
                    "name": "Camiseta",
                    "probability": 0.95
                }
            ],
            "top_k": 3  # opcional
        }
    
    Returns:
        JSON com sugestões para completar o outfit
    """
    try:
        selected_items = request_data.get("selected_items", [])
        top_k = request_data.get("top_k", 3)
        
        if not selected_items:
            raise HTTPException(status_code=400, detail="Campo 'selected_items' é obrigatório")
        
        # Validar estrutura dos itens
        for item in selected_items:
            if "prompt" not in item or "body_region" not in item:
                raise HTTPException(
                    status_code=400, 
                    detail="Cada item deve ter 'prompt' e 'body_region'"
                )
        
        # Buscar sugestões de outfit
        suggestions = get_outfit_suggestions(selected_items, top_k)
        
        result = {
            "selected_items": selected_items,
            "top_k": top_k,
            "suggestions": suggestions,
            "device_used": get_device_info()
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar sugestões de outfit: {str(e)}")

@router.get("/body-regions")
async def get_body_regions():
    """
    Retorna as regiões do corpo disponíveis para classificação
    
    Returns:
        JSON com as regiões do corpo e suas categorias
    """
    body_regions = {
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
    
    return JSONResponse(content={
        "body_regions": body_regions,
        "main_outfit_regions": ["torso", "legs", "feet"]
    })

@router.get("/colors")
async def get_available_colors():
    """
    Retorna as cores disponíveis para compatibilidade
    
    Returns:
        JSON com as cores disponíveis
    """
    colors = [
        "red", "blue", "green", "yellow", "black", "white", "gray", "brown", 
        "pink", "purple", "orange", "navy", "beige", "cream", "maroon", "olive"
    ]
    
    return JSONResponse(content={
        "colors": colors,
        "total_colors": len(colors)
    }) 