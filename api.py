# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
import uvicorn
import json
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Importa os módulos refatorados
from utils.clip_classifier import load_classifier, get_device_info

# Importa os routers
from routers.clothing import router as clothing_router
from routers.body_parts import router as body_parts_router
from routers.analysis import router as analysis_router
from routers.config import router as config_router
from routers.static_files import router as static_files_router

app = FastAPI(
    title="CLIP Clothing & Body Parts API",
    description="""
    ## API para classificação de roupas e detecção de partes do corpo
    
    ### Funcionalidades:
    - **Classificação de Roupas**: Usando modelo CLIP para identificar tipos de roupas
    - **Detecção de Partes do Corpo**: Usando MediaPipe e YOLO para detectar torso, pernas e pés
    - **Extração de Partes**: Salva partes do corpo como imagens estáticas
    - **Análise Completa**: Combina classificação e detecção em uma única chamada
    
    ### Endpoints Principais (REST):
    - `/api/v1/clothing/classify` - Classificação de roupas
    - `/api/v1/body-parts/detect` - Detecção de partes do corpo
    - `/api/v1/body-parts/extract` - Extração e salvamento de partes
    - `/api/v1/analysis/complete` - Análise completa
    """,
    version="2.0.0",
    openapi_tags=[
        {
            "name": "Clothing Classification",
            "description": "Endpoints para classificação de roupas usando CLIP"
        },
        {
            "name": "Body Parts Detection", 
            "description": "Endpoints para detecção e extração de partes do corpo"
        },
        {
            "name": "Analysis",
            "description": "Endpoints para análise completa combinando classificação e detecção"
        },
        {
            "name": "Configuration",
            "description": "Endpoints para configuração da API"
        },
        {
            "name": "Static Files",
            "description": "Endpoints para acessar arquivos estáticos salvos"
        }
    ]
)

# Middleware para capturar erros de parsing
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logar detalhes das requisições e capturar erros de parsing"""
    
    # Log da requisição
    logger.info(f"📥 {request.method} {request.url}")
    logger.info(f"   Headers: {dict(request.headers)}")
    
    # Capturar o body da requisição para debugging
    body_content = None
    try:
        if request.method in ["POST", "PUT", "PATCH"]:
            # Verificar se é multipart/form-data (upload de arquivo)
            content_type = request.headers.get("content-type", "")
            
            if "multipart/form-data" in content_type:
                logger.info("   Content-Type: multipart/form-data (upload de arquivo)")
                # Para multipart, não tentar parsear como JSON
                body_bytes = await request.body()
                if body_bytes:
                    body_content = body_bytes.decode('utf-8', errors='ignore')
                    logger.info(f"   Body (multipart): {body_content[:200]}...")  # Primeiros 200 chars
            else:
                # Para outros tipos, tentar ler como texto/JSON
                body_bytes = await request.body()
                if body_bytes:
                    body_content = body_bytes.decode('utf-8')
                    logger.info(f"   Body (raw): {body_content[:500]}...")  # Primeiros 500 chars
                    
                    # Tentar parsear como JSON apenas se não for multipart
                    try:
                        body_json = json.loads(body_content)
                        logger.info(f"   Body (JSON): {json.dumps(body_json, indent=2)[:500]}...")
                    except json.JSONDecodeError as e:
                        logger.error(f"   ❌ Erro ao parsear JSON: {e}")
                        logger.error(f"   Body inválido: {body_content}")
                    
    except Exception as e:
        logger.error(f"   ❌ Erro ao ler body: {e}")
    
    # Processar a requisição
    try:
        response = await call_next(request)
        logger.info(f"📤 {request.method} {request.url} - Status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"   ❌ Erro na requisição: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(e),
                "request_info": {
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers),
                    "body_preview": body_content[:200] if body_content else None
                }
            }
        )

# Configuração de CORS para permitir qualquer requisição
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],  # Permite qualquer método HTTP
    allow_headers=["*"],  # Permite qualquer header
)

# Configuração de pastas estáticas
STATIC_DIR = "static"
BODY_PARTS_DIR = os.path.join(STATIC_DIR, "body_parts")
os.makedirs(BODY_PARTS_DIR, exist_ok=True)

# Monta pasta estática
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
async def load_models():
    """Carrega os modelos na inicialização da API"""
    print("🔄 Carregando modelos...")
    load_classifier()
    print("✅ Modelos carregados com sucesso!")

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "CLIP Clothing & Body Parts API",
        "version": "2.0.0",
        "status": "running",
        "device": get_device_info(),
        "features": [
            "clothing_classification",
            "body_parts_detection",
            "body_part_extraction",
            "static_file_serving"
        ],
        "static_files": "/static",
        "endpoints": {
            "clothing": "/api/v1/clothing/classify",
            "body_parts": "/api/v1/body-parts/detect",
            "analysis": "/api/v1/analysis/complete",
            "config": "/api/v1/config/margin"
        }
    }

@app.get("/health")
async def health_check():
    """Verificação de saúde da API"""
    return {
        "status": "healthy",
        "device": get_device_info(),
        "features_available": True
    }

# Handler para erros de validação de requisição
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação de requisição"""
    logger.error(f"❌ Erro de validação na requisição: {exc}")
    logger.error(f"   URL: {request.url}")
    logger.error(f"   Method: {request.method}")
    logger.error(f"   Headers: {dict(request.headers)}")
    
    # Tentar capturar o body da requisição
    body_content = None
    try:
        if request.method in ["POST", "PUT", "PATCH"]:
            body_bytes = await request.body()
            if body_bytes:
                body_content = body_bytes.decode('utf-8')
                logger.error(f"   Body: {body_content}")
    except Exception as e:
        logger.error(f"   Erro ao ler body: {e}")
    
    # Log detalhado dos erros de validação
    for error in exc.errors():
        logger.error(f"   Campo: {error.get('loc', 'N/A')}")
        logger.error(f"   Tipo: {error.get('type', 'N/A')}")
        logger.error(f"   Mensagem: {error.get('msg', 'N/A')}")
    
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": "Erro na validação dos dados da requisição",
            "validation_errors": exc.errors(),
            "request_info": {
                "method": request.method,
                "url": str(request.url),
                "body_preview": body_content[:500] if body_content else None
            }
        }
    )

# Handler para erros HTTP
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handler para erros HTTP"""
    logger.error(f"❌ Erro HTTP {exc.status_code}: {exc.detail}")
    logger.error(f"   URL: {request.url}")
    logger.error(f"   Method: {request.method}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "status_code": exc.status_code,
            "request_info": {
                "method": request.method,
                "url": str(request.url)
            }
        }
    )

# Inclui os routers
app.include_router(clothing_router)
app.include_router(body_parts_router)
app.include_router(analysis_router)
app.include_router(config_router)
app.include_router(static_files_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 