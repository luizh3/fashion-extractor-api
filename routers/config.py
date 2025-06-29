# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException
from typing import Dict

from utils.body_parts_detector import set_margin_percentage, get_margin_percentage

router = APIRouter(prefix="/api/v1/config", tags=["Configuration"])

@router.get("/margin")
async def get_margin_config():
    """
    Retorna a configuração atual da margem de tolerância
    
    Returns:
        JSON com a configuração da margem
    """
    margin = get_margin_percentage()
    return {
        "margin_percentage": margin,
        "description": "Margem de tolerância aplicada aos bounding boxes das partes do corpo"
    }

@router.put("/margin")
async def update_margin_config(margin_config: Dict[str, float]):
    """
    Atualiza a configuração da margem de tolerância
    
    Args:
        margin_config: {"margin_percentage": 0.30} (30% de margem)
    
    Returns:
        JSON com confirmação da configuração
    """
    if "margin_percentage" not in margin_config:
        raise HTTPException(
            status_code=400, 
            detail="Campo 'margin_percentage' é obrigatório"
        )
    
    margin = margin_config["margin_percentage"]
    
    # Validar valor da margem
    if not (0.0 <= margin <= 1.0):
        raise HTTPException(
            status_code=400, 
            detail="Margem deve estar entre 0.0 e 1.0 (0% a 100%)"
        )
    
    # Aplicar nova configuração
    set_margin_percentage(margin)
    
    return {
        "success": True,
        "margin_percentage": margin,
        "message": f"Margem configurada para {margin * 100}%"
    } 