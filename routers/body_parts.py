# -*- coding: utf-8 -*-
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
import base64
import os
import uuid
from datetime import datetime
from typing import Dict

from utils.body_parts_detector import detect_body_parts_from_image, get_body_part_image
from utils.image_utils import ensure_rgb_image

router = APIRouter(prefix="/api/v1/body-parts", tags=["Body Parts Detection"])

# Configuração de pastas estáticas
STATIC_DIR = "static"
BODY_PARTS_DIR = os.path.join(STATIC_DIR, "body_parts")
os.makedirs(BODY_PARTS_DIR, exist_ok=True)

@router.post("/detect")
async def detect_body_parts(file: UploadFile = File(...)):
    """
    Detecta partes do corpo na imagem
    
    Args:
        file: Arquivo de imagem (JPG, PNG, etc.)
    
    Returns:
        JSON com as partes do corpo detectadas
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
        
        # Detectar partes do corpo
        detection_result = detect_body_parts_from_image(image)
        
        # Adicionar informações do arquivo
        detection_result["filename"] = file.filename
        detection_result["file_size"] = len(image_data)
        detection_result["content_type"] = file.content_type
        
        return JSONResponse(content=detection_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@router.post("/detect/base64")
async def detect_body_parts_base64(image_data: Dict[str, str]):
    """
    Detecta partes do corpo em uma imagem enviada em formato base64
    
    Args:
        image_data: {"image": "base64_string"}
    
    Returns:
        JSON com as partes do corpo detectadas
    """
    if "image" not in image_data:
        raise HTTPException(status_code=400, detail="Campo 'image' com base64 é obrigatório")
    
    try:
        # Decodificar base64
        image_bytes = base64.b64decode(image_data["image"])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Garantir que a imagem seja RGB
        image = ensure_rgb_image(image)
        
        # Detectar partes do corpo
        detection_result = detect_body_parts_from_image(image)
        
        return JSONResponse(content=detection_result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@router.post("/extract")
async def extract_body_parts(file: UploadFile = File(...)):
    """
    Detecta partes do corpo na imagem e salva como arquivos estáticos
    
    Args:
        file: Arquivo de imagem (JPG, PNG, etc.)
    
    Returns:
        JSON com URLs para acessar as imagens salvas
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
        
        # Detectar partes do corpo
        detection_result = detect_body_parts_from_image(image)
        
        if not detection_result["success"]:
            return JSONResponse(content=detection_result)
        
        # Gerar session ID único
        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Salvar partes do corpo
        saved_parts = {}
        total_parts_saved = 0
        
        for part_name, part_data in detection_result["body_parts"].items():
            try:
                # Extrair parte do corpo
                part_image = get_body_part_image(image, part_name)
                
                if part_image is not None:
                    # Gerar nome do arquivo
                    filename = f"{part_name}_{session_id}_{timestamp}.jpg"
                    filepath = os.path.join(BODY_PARTS_DIR, filename)
                    
                    # Salvar imagem
                    part_image.save(filepath, "JPEG", quality=95)
                    
                    # Informações do arquivo salvo
                    saved_parts[part_name] = {
                        "filename": filename,
                        "url": f"/api/v1/static/body-parts/{filename}",
                        "dimensions": {
                            "width": part_image.width,
                            "height": part_image.height
                        },
                        "area": part_data["area"]
                    }
                    
                    total_parts_saved += 1
                    
            except Exception as e:
                print(f"Erro ao salvar parte {part_name}: {e}")
                continue
        
        # Resultado final
        result = {
            "success": True,
            "session_id": session_id,
            "timestamp": timestamp,
            "filename": file.filename,
            "file_size": len(image_data),
            "content_type": file.content_type,
            "total_parts_saved": total_parts_saved,
            "body_parts": {
                part_name: part_info["url"] 
                for part_name, part_info in saved_parts.items()
            },
            "saved_parts": saved_parts
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@router.get("/{part_name}")
async def extract_specific_body_part(
    file: UploadFile = File(...),
    part_name: str = "torso"
):
    """
    Extrai uma parte específica do corpo da imagem
    
    Args:
        file: Arquivo de imagem (JPG, PNG, etc.)
        part_name: Nome da parte (torso, legs, feet)
    
    Returns:
        JSON com a imagem da parte em base64
    """
    # Validar parte do corpo
    valid_parts = ["torso", "legs", "feet"]
    if part_name not in valid_parts:
        raise HTTPException(
            status_code=400, 
            detail=f"Parte inválida. Use uma das: {valid_parts}"
        )
    
    # Validar tipo de arquivo
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    try:
        # Ler e processar a imagem
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Garantir que a imagem seja RGB
        image = ensure_rgb_image(image)
        
        # Extrair parte do corpo
        part_image = get_body_part_image(image, part_name)
        
        if part_image is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Parte '{part_name}' não foi detectada na imagem"
            )
        
        # Converter para base64
        buffer = io.BytesIO()
        part_image.save(buffer, format="JPEG", quality=95)
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # Resultado final
        result = {
            "part_name": part_name,
            "part_dimensions": {
                "width": part_image.width,
                "height": part_image.height
            },
            "part_image_base64": img_base64,
            "filename": file.filename,
            "file_size": len(image_data),
            "content_type": file.content_type
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}") 