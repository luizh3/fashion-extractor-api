# -*- coding: utf-8 -*-
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
import base64
from typing import Dict

from utils.clip_classifier import classify_clothing_image, get_device_info
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