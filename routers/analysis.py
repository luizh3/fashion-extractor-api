# -*- coding: utf-8 -*-
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image
import io
import base64
import os
import uuid
import logging
from datetime import datetime
from typing import Dict

from utils.clip_classifier import classify_clothing_image, get_device_info, analyze_outfit_compatibility, analyze_complete_outfit_image, detect_clothing_color
from utils.body_parts_detector import detect_body_parts_from_image, get_body_part_image
from utils.image_utils import ensure_rgb_image

# Configurar logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analysis", tags=["Analysis"])

# Configuração de pastas estáticas
STATIC_DIR = "static"
BODY_PARTS_DIR = os.path.join(STATIC_DIR, "body_parts")
os.makedirs(BODY_PARTS_DIR, exist_ok=True)

@router.post("/complete")
async def analyze_complete(file: UploadFile = File(...)):
    """
    Realiza análise completa: extrai todas as partes do corpo e classifica cada uma
    """
    logger.info("Iniciando análise completa")
    try:
        if not file.content_type.startswith('image/'):
            logger.error(f"Tipo de arquivo inválido: {file.content_type}")
            raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
        image_data = await file.read()
        if len(image_data) == 0:
            logger.error("Arquivo vazio!")
            raise HTTPException(status_code=400, detail="Arquivo está vazio")
        image = Image.open(io.BytesIO(image_data))
        image = ensure_rgb_image(image)
        body_detection = detect_body_parts_from_image(image)
        if not body_detection["success"]:
            logger.error(f"Falha na detecção: {body_detection['error']}")
            return JSONResponse(content={
                "success": False,
                "error": body_detection["error"],
                "filename": file.filename,
                "file_size": len(image_data),
                "content_type": file.content_type
            })
        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_parts = {}
        classified_parts = {}
        total_parts_saved = 0
        for part_name, part_data in body_detection["body_parts"].items():
            try:
                part_image = get_body_part_image(image, part_name)
                if part_image is not None:
                    filename = f"{part_name}_{session_id}_{timestamp}.jpg"
                    filepath = os.path.join(BODY_PARTS_DIR, filename)
                    part_image.save(filepath, "JPEG", quality=95)
                    classifications, top_prediction = classify_clothing_image(part_image, part_name)
                    color_analysis = detect_clothing_color(part_image)
                    saved_parts[part_name] = {
                        "filename": filename,
                        "url": f"/api/v1/static/body-parts/{filename}",
                        "dimensions": {
                            "width": part_image.width,
                            "height": part_image.height
                        },
                        "area": part_data["area"]
                    }
                    classified_parts[part_name] = {
                        "predictions": classifications,
                        "top_prediction": top_prediction,
                        "color_analysis": color_analysis,
                        "url": f"/api/v1/static/body-parts/{filename}"
                    }
                    total_parts_saved += 1
            except Exception as e:
                logger.error(f"Erro ao processar parte {part_name}: {e}")
                continue
        logger.info(f"Análise completa finalizada. {total_parts_saved} partes salvas.")
        compatibility_analysis = analyze_outfit_compatibility(classified_parts)
        complete_outfit_analysis = analyze_complete_outfit_image(image, classified_parts)
        vis_filename = f"bodyparts_{session_id}_{timestamp}.jpg"
        vis_filepath = os.path.join(BODY_PARTS_DIR, vis_filename)
        try:
            from utils.body_parts_detector import detector
            detector.save_body_parts_visualization(image, body_detection, vis_filepath)
            vis_url = f"/api/v1/static/body-parts/{vis_filename}"
        except Exception as e:
            logger.error(f"Erro ao salvar visualização das partes do corpo: {e}")
            vis_url = None
        result = {
            "success": True,
            "session_id": session_id,
            "timestamp": timestamp,
            "filename": file.filename,
            "file_size": len(image_data),
            "content_type": file.content_type,
            "device_used": get_device_info(),
            "total_parts_saved": total_parts_saved,
            "body_parts": {
                part_name: part_info["url"] 
                for part_name, part_info in saved_parts.items()
            },
            "saved_parts": saved_parts,
            "classifications": classified_parts,
            "outfit_compatibility": compatibility_analysis,
            "complete_outfit_analysis": complete_outfit_analysis,
            "body_parts_visualization_url": vis_url,
            "summary": {
                "total_parts_detected": len(body_detection["body_parts"]),
                "total_parts_classified": len(classified_parts),
                "people_detected": len(body_detection.get("people", [])),
                "compatibility_score": compatibility_analysis.get("compatibility_score", 0),
                "overall_coordination_score": complete_outfit_analysis.get("full_image_analysis", {}).get("coordination_analysis", {}).get("coordination_score", 0)
            }
        }
        logger.info("Análise completa concluída com sucesso")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Erro geral na análise: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@router.post("/complete/base64")
async def analyze_complete_base64(request_data: Dict):
    """
    Realiza análise completa usando imagem em base64
    
    Args:
        request_data: {"image_base64": "data:image/jpeg;base64,/9j/4AAQ..."}
    
    Returns:
        JSON com resultados de classificação para cada parte extraída
    """
    logger.info("Iniciando análise completa via base64")
    
    try:
        # Validar dados da requisição
        if "image_base64" not in request_data:
            logger.error("Campo 'image_base64' não encontrado")
            raise HTTPException(status_code=400, detail="Campo 'image_base64' é obrigatório")
        
        image_base64 = request_data["image_base64"]
        logger.info(f"Tamanho do base64: {len(image_base64)} caracteres")
        
        # Remover prefixo data:image/...;base64, se presente
        if image_base64.startswith('data:image/'):
            image_base64 = image_base64.split(',')[1]
            logger.info("Prefixo data: removido")
        
        # Decodificar base64
        logger.info("Decodificando base64...")
        image_data = base64.b64decode(image_base64)
        logger.info(f"Tamanho decodificado: {len(image_data)} bytes")
        
        # Abrir imagem
        logger.info("Abrindo imagem...")
        image = Image.open(io.BytesIO(image_data))
        logger.info(f"Dimensões: {image.size}")
        logger.info(f"Modo: {image.mode}")
        
        # Garantir que a imagem seja RGB
        logger.info("Convertendo para RGB...")
        image = ensure_rgb_image(image)
        
        # Detectar partes do corpo
        logger.info("Detectando partes do corpo...")
        body_detection = detect_body_parts_from_image(image)
        
        if not body_detection["success"]:
            logger.error(f"Falha na detecção: {body_detection['error']}")
            return JSONResponse(content={
                "success": False,
                "error": body_detection["error"],
                "image_size": len(image_data)
            })
        
        logger.info(f"Partes detectadas: {list(body_detection['body_parts'].keys())}")
        
        # Gerar session ID único
        session_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Extrair, salvar e classificar cada parte do corpo
        saved_parts = {}
        classified_parts = {}
        total_parts_saved = 0
        
        for part_name, part_data in body_detection["body_parts"].items():
            try:
                logger.info(f"Processando parte: {part_name}")
                
                # Extrair parte do corpo
                part_image = get_body_part_image(image, part_name)
                
                if part_image is not None:
                    logger.info(f"Dimensões da parte: {part_image.size}")
                    
                    # Gerar nome do arquivo
                    filename = f"{part_name}_{session_id}_{timestamp}.jpg"
                    filepath = os.path.join(BODY_PARTS_DIR, filename)
                    
                    # Salvar imagem
                    logger.info(f"Salvando em: {filepath}")
                    part_image.save(filepath, "JPEG", quality=95)
                    
                    # Classificar a parte extraída
                    logger.info(f"Classificando...")
                    classifications, top_prediction = classify_clothing_image(part_image, part_name)
                    
                    # Detectar cor da peça
                    logger.info(f"Detectando cor...")
                    color_analysis = detect_clothing_color(part_image)
                    
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
                    
                    # Resultados da classificação
                    classified_parts[part_name] = {
                        "predictions": classifications,
                        "top_prediction": top_prediction,
                        "color_analysis": color_analysis,
                        "url": f"/api/v1/static/body-parts/{filename}"
                    }
                    
                    total_parts_saved += 1
                    logger.info(f"{part_name} processado com sucesso")
                    
            except Exception as e:
                logger.error(f"Erro ao processar parte {part_name}: {e}")
                continue
        
        logger.info(f"Análise completa finalizada. {total_parts_saved} partes salvas.")
        
        # Analisar compatibilidade entre as peças detectadas
        logger.info("Analisando compatibilidade do outfit...")
        compatibility_analysis = analyze_outfit_compatibility(classified_parts)
        logger.info(f"Score de compatibilidade: {compatibility_analysis.get('compatibility_score', 0)}")
        
        # Analisar a imagem completa com CLIP
        logger.info("Analisando outfit completo com CLIP...")
        complete_outfit_analysis = analyze_complete_outfit_image(image, classified_parts)
        logger.info(f"Análise completa realizada com sucesso")
        
        # Salvar visualização das partes do corpo na imagem original
        vis_filename = f"bodyparts_{session_id}_{timestamp}.jpg"
        vis_filepath = os.path.join(BODY_PARTS_DIR, vis_filename)
        try:
            from utils.body_parts_detector import detector
            detector.save_body_parts_visualization(image, body_detection, vis_filepath)
            vis_url = f"/api/v1/static/body-parts/{vis_filename}"
        except Exception as e:
            logger.error(f"Erro ao salvar visualização das partes do corpo: {e}")
            vis_url = None
        
        # Resultado final
        result = {
            "success": True,
            "session_id": session_id,
            "timestamp": timestamp,
            "image_size": len(image_data),
            "device_used": get_device_info(),
            "total_parts_saved": total_parts_saved,
            "body_parts": {
                part_name: part_info["url"] 
                for part_name, part_info in saved_parts.items()
            },
            "saved_parts": saved_parts,
            "classifications": classified_parts,
            "outfit_compatibility": compatibility_analysis,
            "complete_outfit_analysis": complete_outfit_analysis,
            "body_parts_visualization_url": vis_url,
            "summary": {
                "total_parts_detected": len(body_detection["body_parts"]),
                "total_parts_classified": len(classified_parts),
                "people_detected": len(body_detection.get("people", [])),
                "compatibility_score": compatibility_analysis.get("compatibility_score", 0),
                "overall_coordination_score": complete_outfit_analysis.get("full_image_analysis", {}).get("coordination_analysis", {}).get("coordination_score", 0)
            }
        }
        
        logger.info("=" * 50)
        logger.info("FIM - Análise Completa (SUCESSO)")
        logger.info("=" * 50)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error("=" * 50)
        logger.error("ERRO - Análise Completa")
        logger.error("=" * 50)
        logger.error(f"Tipo de erro: {type(e).__name__}")
        logger.error(f"Mensagem: {str(e)}")
        logger.error(f"Detalhes completos: {e}")
        
        # Capturar mais informações sobre o erro
        import traceback
        logger.error(f"Traceback completo:")
        logger.error(traceback.format_exc())
        
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}") 