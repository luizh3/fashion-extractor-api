# CLIP Clothing & Body Parts API

Uma API REST para classificação de roupas e detecção de partes do corpo usando o modelo CLIP da OpenAI, MediaPipe e YOLO. A API recebe imagens e retorna classificações e detecções em formato JSON.

## 🚀 Funcionalidades

- **Classificação de roupas**: Identifica 7 categorias diferentes (camiseta, calça, shorts, vestido, jaqueta, blusa, saia)
- **Detecção de partes do corpo**: Identifica torso, pernas e pés usando MediaPipe Pose
- **Detecção de pessoas**: Usa YOLOv8 para detectar pessoas na imagem
- **Extração de partes**: Extrai imagens específicas de partes do corpo
- **Análise completa**: Combina classificação de roupas e detecção de partes
- **Múltiplos formatos de entrada**: Suporte para upload de arquivo e base64
- **Resposta JSON estruturada**: Dados organizados e fáceis de processar
- **Documentação automática**: Swagger UI integrado
- **Verificação de saúde**: Endpoint para monitoramento

## 📋 Pré-requisitos

- Python 3.8+
- CUDA (opcional, para aceleração GPU)
- Docker (opcional, para execução em container)

## 🛠️ Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## 🐳 Execução com Docker

### Usando Docker Compose (Recomendado)

```bash
# Construir e executar
docker-compose up --build

# Executar em background
docker-compose up -d --build

# Parar os serviços
docker-compose down
```

### Usando Docker Compose para Desenvolvimento (Hot Reload)

```bash
# Para desenvolvimento com volume (mudanças no código sem rebuild)
docker-compose -f docker-compose.dev.yml up --build

# Executar em background
docker-compose -f docker-compose.dev.yml up -d --build

# Parar os serviços
docker-compose -f docker-compose.dev.yml down
```

**Vantagens do modo desenvolvimento:**
- ✅ Mudanças no código são aplicadas automaticamente
- ✅ Não precisa rebuildar para mudanças no código Python
- ✅ Mais rápido para desenvolvimento
- ⚠️ Primeira execução ainda precisa do build inicial

### Usando Docker diretamente

```bash
# Construir a imagem
docker build -t clip-api .

# Executar o container
docker run -p 8000:8000 clip-api

# Executar em background
docker run -d -p 8000:8000 --name clip-api-container clip-api
```

A API estará disponível em `http://localhost:8000`

## 🏃‍♂️ Como executar

### Iniciar a API

```bash
python api.py
```

A API estará disponível em `http://localhost:8000`

### Documentação interativa

Acesse `http://localhost:8000/docs` para ver a documentação Swagger UI

## 📡 Endpoints

### 1. Informações da API
- **GET** `/` - Informações básicas da API
- **GET** `/health` - Status de saúde e carregamento dos modelos

### 2. Classificação de Roupas

#### Upload de arquivo
- **POST** `/api/v1/clothing/classify`
- **Content-Type**: `multipart/form-data`
- **Parâmetro**: `file` (arquivo de imagem)

#### Base64
- **POST** `/api/v1/clothing/classify/base64`
- **Content-Type**: `application/json`
- **Body**: `{"image": "base64_string"}`

### 3. Detecção de Partes do Corpo

#### Upload de arquivo
- **POST** `/api/v1/body-parts/detect`
- **Content-Type**: `multipart/form-data`
- **Parâmetro**: `file` (arquivo de imagem)

#### Base64
- **POST** `/api/v1/body-parts/detect/base64`
- **Content-Type**: `application/json`
- **Body**: `{"image": "base64_string"}`

#### Extração e Salvamento
- **POST** `/api/v1/body-parts/extract`
- **Content-Type**: `multipart/form-data`
- **Parâmetro**: `file` (arquivo de imagem)
- **Retorna**: URLs para acessar as imagens salvas

#### Extração de Parte Específica
- **GET** `/api/v1/body-parts/{part_name}`
- **Content-Type**: `multipart/form-data`
- **Parâmetros**: 
  - `file` (arquivo de imagem)
  - `part_name` (torso, legs, feet)
- **Retorna**: Imagem da parte extraída em base64

### 4. Análise Completa
- **POST** `/api/v1/analysis/complete`
- **Content-Type**: `multipart/form-data`
- **Parâmetro**: `file` (arquivo de imagem)
- **Retorna**: Extração de todas as partes do corpo + classificação individual de cada parte
- **Funcionalidades**:
  - Detecta todas as partes do corpo (torso, pernas, pés)
  - Extrai e salva cada parte como imagem estática
  - Classifica individualmente cada parte extraída
  - Retorna URLs para acessar as imagens salvas
  - Fornece classificações detalhadas para cada parte

### 5. Configuração
- **GET** `/api/v1/config/margin`
- **Retorna**: Configuração atual da margem

- **PUT** `/api/v1/config/margin`
- **Content-Type**: `application/json`
- **Body**: `{"margin_percentage": 0.30}` (30% de margem)
- **Retorna**: Confirmação da configuração

### 6. Arquivos Estáticos
- **GET** `/api/v1/static/body-parts/{filename}`
- **Retorna**: Imagem da parte do corpo salva

## 📊 Exemplos de Resposta

### Classificação de Roupas
```json
{
  "filename": "shorts.jpg",
  "file_size": 67584,
  "content_type": "image/jpeg",
  "device_used": "cpu",
  "predictions": [
    {
      "category": 6,
      "name": "Suéter",
      "probability": 0.9133208394050598,
      "percentage": "91.33%"
    },
    {
      "category": 4,
      "name": "Blusa", 
      "probability": 0.0866791605949402,
      "percentage": "8.67%"
    }
  ],
  "top_prediction": {
    "category": 6,
    "name": "Suéter",
    "probability": 0.9133208394050598,
    "percentage": "91.33%"
  }
}
```

### Categorias Disponíveis
A API usa categorias padronizadas em inglês maiúsculo para identificação pelo cliente:

| Category | Name (PT) | Description |
|----------|-----------|-------------|
| `TSHIRT` | Camiseta | T-shirts e camisetas |
| `PANTS` | Calça | Calças e jeans |
| `SHORTS` | Shorts | Shorts e bermudas |
| `DRESS` | Vestido | Vestidos |
| `JACKET` | Jaqueta | Jaquetas e blazers |
| `BLOUSE` | Blusa | Blusas femininas |
| `SKIRT` | Saia | Saias |
| `SWEATER` | Suéter | Suéteres e pulôveres |
| `HOODIE` | Moletom | Moletons com capuz |
| `COAT` | Casaco | Casacos pesados |
| `SUIT` | Terno | Ternos e trajes |
| `UNIFORM` | Uniforme | Uniformes |
| `SWIMSUIT` | Maiô | Maiôs e sungas |
| `UNDERWEAR` | Roupa Íntima | Roupas íntimas |
| `SOCKS` | Meias | Meias e meias-calças |
| `SHOES` | Sapatos | Sapatos e tênis |
| `BOOTS` | Botas | Botas |
| `SANDALS` | Sandálias | Sandálias |
| `HAT` | Chapéu | Chapéus |
| `CAP` | Boné | Bonés |
| `SCARF` | Cachecol | Cachecóis |
| `GLOVES` | Luvas | Luvas |
| `BELT` | Cinto | Cintos |
| `BAG` | Bolsa | Bolsas |
| `BACKPACK` | Mochila | Mochilas |

### Detecção de Partes do Corpo
```json
{
  "success": true,
  "filename": "person.jpg",
  "body_parts": {
    "torso": {
      "bbox": [100, 50, 300, 200],
      "area": 20000
    },
    "legs": {
      "bbox": [120, 200, 280, 400],
      "area": 32000
    },
    "feet": {
      "bbox": [140, 380, 260, 450],
      "area": 8400
    }
  },
  "people": [[80, 30, 320, 480]],
  "image_dimensions": {
    "width": 400,
    "height": 500
  }
}
```

### Análise Completa
```json
{
  "success": true,
  "session_id": "a1b2c3d4",
  "timestamp": "20250628_143022",
  "filename": "outfit.jpg",
  "file_size": 139406,
  "content_type": "image/jpeg",
  "device_used": "cpu",
  "total_parts_saved": 3,
  "body_parts": {
    "torso": "/api/v1/static/body-parts/torso_a1b2c3d4_20250628_143022.jpg",
    "legs": "/api/v1/static/body-parts/legs_a1b2c3d4_20250628_143022.jpg",
    "feet": "/api/v1/static/body-parts/feet_a1b2c3d4_20250628_143022.jpg"
  },
  "saved_parts": {
    "torso": {
      "filename": "torso_a1b2c3d4_20250628_143022.jpg",
      "url": "/api/v1/static/body-parts/torso_a1b2c3d4_20250628_143022.jpg",
      "dimensions": {
        "width": 189,
        "height": 280
      },
      "area": 52920
    },
    "legs": {
      "filename": "legs_a1b2c3d4_20250628_143022.jpg",
      "url": "/api/v1/static/body-parts/legs_a1b2c3d4_20250628_143022.jpg",
      "dimensions": {
        "width": 99,
        "height": 420
      },
      "area": 41580
    },
    "feet": {
      "filename": "feet_a1b2c3d4_20250628_143022.jpg",
      "url": "/api/v1/static/body-parts/feet_a1b2c3d4_20250628_143022.jpg",
      "dimensions": {
        "width": 65,
        "height": 43
      },
      "area": 2795
    }
  },
  "classifications": {
    "torso": {
      "predictions": [
        {
          "category": 6,
          "name": "Suéter",
          "probability": 0.9133208394050598,
          "percentage": "91.33%"
        },
        {
          "category": 4,
          "name": "Blusa",
          "probability": 0.0866791605949402,
          "percentage": "8.67%"
        }
      ],
      "top_prediction": {
        "category": 6,
        "name": "Suéter",
        "probability": 0.9133208394050598,
        "percentage": "91.33%"
      },
      "url": "/api/v1/static/body-parts/torso_a1b2c3d4_20250628_143022.jpg"
    },
    "legs": {
      "predictions": [
        {
          "category": 1,
          "name": "Calça",
          "probability": 0.7361973524093628,
          "percentage": "73.62%"
        },
        {
          "category": 2,
          "name": "Shorts",
          "probability": 0.2638026475906372,
          "percentage": "26.38%"
        }
      ],
      "top_prediction": {
        "category": 1,
        "name": "Calça",
        "probability": 0.7361973524093628,
        "percentage": "73.62%"
      },
      "url": "/api/v1/static/body-parts/legs_a1b2c3d4_20250628_143022.jpg"
    },
    "feet": {
      "predictions": [
        {
          "category": 13,
          "name": "Sapatos",
          "probability": 0.6441813707351685,
          "percentage": "64.42%"
        },
        {
          "category": 14,
          "name": "Botas",
          "probability": 0.3558186292648315,
          "percentage": "35.58%"
        }
      ],
      "top_prediction": {
        "category": 13,
        "name": "Sapatos",
        "probability": 0.6441813707351685,
        "percentage": "64.42%"
      },
      "url": "/api/v1/static/body-parts/feet_a1b2c3d4_20250628_143022.jpg"
    }
  },
  "summary": {
    "total_parts_detected": 3,
    "total_parts_classified": 3,
    "people_detected": 1
  }
}
```

### Detecção e Salvamento de Partes
```json
{
  "filename": "person.jpg",
  "session_id": "a1b2c3d4",
  "timestamp": "20241228_143022",
  "total_parts_saved": 3,
  "saved_parts": {
    "torso": {
      "filename": "torso_a1b2c3d4_20241228_143022.jpg",
      "url": "/static/body_parts/torso_a1b2c3d4_20241228_143022.jpg",
      "bbox": [100, 50, 300, 200],
      "area": 20000,
      "dimensions": {
        "width": 200,
        "height": 150
      }
    },
    "legs": {
      "filename": "legs_a1b2c3d4_20241228_143022.jpg",
      "url": "/static/body_parts/legs_a1b2c3d4_20241228_143022.jpg",
      "bbox": [120, 200, 280, 400],
      "area": 32000,
      "dimensions": {
        "width": 160,
        "height": 200
      }
    }
  }
}
```

## 🧪 Testando a API

Execute o script de teste:

```bash
python test_api.py
```

## 🚀 Exemplos de Uso

### 1. Classificação de Roupas
```bash
# Upload de arquivo
curl -X POST "http://localhost:8000/api/v1/clothing/classify" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@shorts.jpg"

# Base64
curl -X POST "http://localhost:8000/api/v1/clothing/classify/base64" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_string_here"}'
```

### 2. Detecção de Partes do Corpo
```bash
# Upload de arquivo
curl -X POST "http://localhost:8000/api/v1/body-parts/detect" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@shorts.jpg"

# Base64
curl -X POST "http://localhost:8000/api/v1/body-parts/detect/base64" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"image": "base64_string_here"}'

# Extração e salvamento
curl -X POST "http://localhost:8000/api/v1/body-parts/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@shorts.jpg"
```

### 3. Análise Completa
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/complete" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@shorts.jpg"
```

### 4. Configuração de Margem
```bash
# Ver configuração atual
curl -X GET "http://localhost:8000/api/v1/config/margin"

# Definir margem de 30%
curl -X PUT "http://localhost:8000/api/v1/config/margin" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{"margin_percentage": 0.30}'
```

### 5. Acessar Imagens Salvas
```bash
# Após extrair partes do corpo, você receberá URLs como:
# "http://localhost:8000/api/v1/static/body-parts/torso_abc123.jpg"
curl "http://localhost:8000/api/v1/static/body-parts/torso_abc123.jpg"
```

## 🔧 Configuração

### Variáveis de ambiente (opcional)
- `PORT`: Porta da API (padrão: 8000)
- `HOST`: Host da API (padrão: 0.0.0.0)

### Categorias de roupas suportadas
- camiseta
- calça
- shorts
- vestido
- jaqueta
- blusa
- saia

### Partes do corpo detectadas
- torso
- legs (pernas)
- feet (pés)

## 📁 **Nova Estrutura de Arquivos**
```
clip/
├── api.py                    # Arquivo principal (113 linhas vs 567 antes!)
├── routers/                  # Módulos de endpoints
│   ├── __init__.py
│   ├── clothing.py          # Endpoints de classificação de roupas
│   ├── body_parts.py        # Endpoints de detecção de partes do corpo
│   ├── analysis.py          # Endpoints de análise completa
│   ├── config.py            # Endpoints de configuração
│   └── static_files.py      # Endpoints de arquivos estáticos
├── utils/                    # Utilitários e módulos principais
│   ├── __init__.py
│   ├── image_utils.py       # Funções de processamento de imagem
│   ├── clip_classifier.py   # Módulo de classificação CLIP
│   ├── body_parts_detector.py # Módulo de detecção de partes do corpo
│   └── parts_separator.py   # Módulo de separação de partes (legacy)
├── static/                   # Arquivos estáticos salvos
├── test_images/             # Imagens para testes
└── ... (outros arquivos)
```

## 🐛 Solução de Problemas

### Modelos não carregam
- Verifique se o CUDA está disponível (se usando GPU)
- Certifique-se de que todas as dependências estão instaladas
- Para YOLO, o modelo será baixado automaticamente na primeira execução

### Erro de memória
- Use CPU em vez de GPU: modifique `device = "cpu"` no código
- Reduza o tamanho das imagens antes do envio
- Considere usar modelos menores (YOLOv8n já é o menor)

### Erro de formato de arquivo
- Certifique-se de que o arquivo é uma imagem válida (JPG, PNG, etc.)
- Verifique se o Content-Type está correto

### Nenhuma pose detectada
- Certifique-se de que há uma pessoa visível na imagem
- A pessoa deve estar de corpo inteiro ou pelo menos com torso visível
- Imagens muito pequenas podem não ser detectadas

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. 

### Categorias de Roupas

A API classifica roupas nas seguintes categorias (usando IDs numéricos):

- **0**: Camiseta
- **1**: Calça  
- **2**: Shorts
- **3**: Jaqueta
- **4**: Blusa
- **5**: Saia
- **6**: Suéter
- **7**: Moletom
- **8**: Casaco
- **9**: Terno
- **10**: Maiô
- **11**: Roupa Íntima
- **12**: Meias
- **13**: Sapatos
- **14**: Botas
- **15**: Sandálias
- **16**: Chapéu
- **17**: Boné
- **18**: Cachecol
- **19**: Luvas
- **20**: Cinto
- **21**: Bolsa
- **22**: Mochila 