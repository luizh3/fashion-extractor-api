# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/api/v1/static", tags=["Static Files"])

# Configuração de pastas estáticas
STATIC_DIR = "static"
BODY_PARTS_DIR = os.path.join(STATIC_DIR, "body_parts")

@router.get("/body-parts/{filename}")
async def get_body_part_image_static(filename: str):
    """
    Retorna uma imagem salva de parte do corpo
    
    Args:
        filename: Nome do arquivo da imagem
    
    Returns:
        Imagem salva
    """
    filepath = os.path.join(BODY_PARTS_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    
    # Retorna o arquivo estático
    return FileResponse(filepath, media_type="image/jpeg") 