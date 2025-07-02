# CLIP Clothing & Body Parts API

Uma API REST para classificação de roupas e detecção de partes do corpo usando o modelo CLIP da OpenAI, MediaPipe e YOLO. A API recebe imagens e retorna classificações e detecções em formato JSON.

## 🚀 Funcionalidades

- **Classificação de roupas**: Identifica 23 categorias diferentes de roupas e acessórios
- **Detecção de partes do corpo**: Identifica torso, pernas e pés usando MediaPipe Pose
- **Detecção de pessoas**: Usa YOLOv8 para detectar pessoas na imagem
- **Extração de partes**: Extrai imagens específicas de partes do corpo
- **Análise completa**: Combina classificação de roupas e detecção de partes
- **🆕 Compatibilidade de roupas**: Sugere itens que combinam com peças selecionadas
- **🆕 Sugestões de outfit**: Completa outfits baseado em itens já escolhidos
- **🆕 Categorização por região**: Organiza roupas por região do corpo (torso, legs, feet, etc.)
- **🆕 Compatibilidade com cores**: Sugere itens baseado em cores específicas
- **🆕 Combinação item + cor**: Considera tanto o tipo de roupa quanto a cor
- **Múltiplos formatos de entrada**: Suporte para upload de arquivo e base64
- **Resposta JSON estruturada**: Dados organizados e fáceis de processar
- **Documentação automática**: Swagger UI integrado
- **Verificação de saúde**: Endpoint para monitoramento

## 📋 Pré-requisitos

- Python 3.8+
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

### 7. 🆕 Compatibilidade de Roupas

#### Buscar itens compatíveis
- **POST** `/api/v1/clothing/compatible-items`
- **Content-Type**: `application/json`
- **Body**: 
```json
{
  "selected_item": {
    "prompt": "t-shirt",
    "body_region": "torso",
    "name": "Camiseta",
    "color": "red"  # opcional - cor do item
  },
  "target_regions": ["legs", "feet"],
  "top_k": 5
}
```
- **Retorna**: Sugestões de itens compatíveis por região. Se o item selecionado tiver uma cor, as sugestões incluirão cores compatíveis para cada item.

**Exemplo de resposta com cores:**
```json
{
  "selected_item": {
    "prompt": "t-shirt",
    "body_region": "torso",
    "name": "Camiseta",
    "color": "red"
  },
  "suggestions": {
    "legs": [
      {
        "category": "pants",
        "name": "Calça",
        "prompt": "pants",
        "body_region": "legs",
        "similarity": 0.85,
        "compatible_colors": [
          {"color": "blue", "similarity": 0.92},
          {"color": "black", "similarity": 0.88},
          {"color": "white", "similarity": 0.85}
        ]
      }
    ]
  }
}
```

#### Buscar compatibilidade por cor
- **POST** `/api/v1/clothing/color-compatibility`
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "color": "red",
  "target_regions": ["torso", "legs"],  # opcional
  "top_k": 5
}
```
- **Retorna**: Sugestões de itens que combinam com a cor

#### Sugestões de outfit completo
- **POST** `/api/v1/clothing/outfit-suggestions`
- **Content-Type**: `application/json`
- **Body**:
```json
{
  "selected_items": [
    {
      "prompt": "pants",
      "body_region": "legs",
      "name": "Calça",
      "probability": 0.92
    }
  ],
  "top_k": 3
}
```
- **Retorna**: Sugestões para completar o outfit

#### Regiões do corpo disponíveis
- **GET** `/api/v1/clothing/body-regions`
- **Retorna**: Mapeamento de regiões do corpo e suas categorias

#### Cores disponíveis
- **GET** `/api/v1/clothing/colors`
- **Retorna**: Lista de cores disponíveis para compatibilidade

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
A API usa categorias padronizadas com informações de região do corpo:

| Category | Name (PT) | Prompt (EN) | Body Region |
|----------|-----------|-------------|-------------|
| 0 | Camiseta | t-shirt | torso |
| 1 | Calça | pants | legs |
| 2 | Shorts | shorts | legs |
| 3 | Jaqueta | jacket | torso |
| 4 | Blusa | blouse | torso |
| 5 | Saia | skirt | legs |
| 6 | Suéter | sweater | torso |
| 7 | Moletom | hoodie | torso |
| 8 | Casaco | coat | torso |
| 9 | Terno | suit | torso |
| 10 | Maiô | swimsuit | full_body |
| 11 | Roupa Íntima | underwear | underwear |
| 12 | Meias | socks | feet |
| 13 | Sapatos | shoes | feet |
| 14 | Botas | boots | feet |
| 15 | Sandálias | sandals | feet |
| 16 | Chapéu | hat | head |
| 17 | Boné | cap | head |
| 18 | Cachecol | scarf | neck |
| 19 | Luvas | gloves | hands |
| 20 | Cinto | belt | waist |
| 21 | Bolsa | bag | accessory |
| 22 | Mochila | backpack | accessory |

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

### 6. 🆕 Análise Completa com Compatibilidade

```python
# Upload de imagem para análise completa
with open("outfit.jpg", "rb") as image_file:
    files = {"file": ("outfit.jpg", image_file, "image/jpeg")}
    
    response = requests.post(
        "http://localhost:8000/api/v1/analysis/complete",
        files=files
    )

result = response.json()

# Resultados incluem:
# - Classificação de cada parte do corpo
# - Análise de compatibilidade entre as peças
# - Score geral do outfit
# - Sugestões de melhoria

print("Score de compatibilidade:", result["outfit_compatibility"]["compatibility_score"])
print("Avaliação:", result["outfit_compatibility"]["outfit_rating"]["level"])
```

**Exemplo de resposta com compatibilidade:**
```json
{
  "success": true,
  "classifications": {
    "torso": {
      "top_prediction": {
        "name": "Camiseta",
        "prompt": "t-shirt",
        "probability": 0.85
      }
    },
    "legs": {
      "top_prediction": {
        "name": "Calça", 
        "prompt": "pants",
        "probability": 0.92
      }
    },
    "feet": {
      "top_prediction": {
        "name": "Sapatos",
        "prompt": "shoes", 
        "probability": 0.78
      }
    }
  },
  "outfit_compatibility": {
    "compatibility_score": 0.76,
    "outfit_rating": {
      "level": "Bom",
      "emoji": "👍",
      "description": "Outfit bem combinado. As peças funcionam bem juntas."
    },
    "pairwise_compatibility": {
      "torso_vs_legs": {
        "part1": {"region": "torso", "name": "Camiseta"},
        "part2": {"region": "legs", "name": "Calça"},
        "similarity": 0.82,
        "compatibility_level": "Excelente"
      },
      "torso_vs_feet": {
        "part1": {"region": "torso", "name": "Camiseta"},
        "part2": {"region": "feet", "name": "Sapatos"},
        "similarity": 0.71,
        "compatibility_level": "Boa"
      }
    },
    "suggestions": [
      "Adicionar um Sapatos pode completar o look",
      "Um Cinto pode complementar o outfit"
    ]
  }
}
```

### 7. 🧪 Teste de Compatibilidade

```bash
# Testar análise de compatibilidade
# (Arquivo removido)

# Testar sugestões contextuais
# (Arquivo removido)
```

**Funcionalidades do teste:**
- ✅ Upload de imagem com pessoa vestida
- ✅ Detecção automática de partes do corpo
- ✅ Classificação de cada peça
- ✅ Análise de compatibilidade entre peças
- ✅ Score geral do outfit
- ✅ Sugestões contextuais inteligentes (baseadas no CLIP)

## 🎨 Cores Disponíveis

A API suporta 16 cores para compatibilidade:

- **Cores básicas**: red, blue, green, yellow, black, white, gray, brown
- **Cores vibrantes**: pink, purple, orange
- **Cores neutras**: navy, beige, cream, maroon, olive

### Como usar cores:

1. **Buscar por cor**: `POST /color-compatibility` com `"color": "red"`
2. **Item + cor**: `POST /compatible-items` com `"color": "red"`
3. **Listar cores**: `GET /colors`

## 🔧 Como funciona a compatibilidade com cores

A funcionalidade de compatibilidade com cores usa **combinação de embeddings**:

1. **Embeddings de cores**: Cada cor tem seu próprio embedding CLIP
2. **Combinação inteligente**: 70% peso do item + 30% peso da cor
3. **Similaridade híbrida**: Considera tanto o tipo de roupa quanto a cor
4. **Contexto visual**: CLIP entende combinações de cores que fazem sentido

### Vantagens desta abordagem:
- ✅ **Contexto de cor**: Entende que vermelho combina com azul, preto, etc.
- ✅ **Flexibilidade**: Funciona com qualquer combinação de item + cor
- ✅ **Precisão**: Considera tanto estilo quanto cor
- ✅ **Escalável**: Fácil adicionar novas cores

## 🎯 Exemplos de Uso das Novas Funcionalidades

### 1. Buscar itens compatíveis com uma calça

```python
import requests

# Usuário selecionou uma calça
selected_item = {
    "prompt": "pants",
    "body_region": "legs", 
    "name": "Calça"
}

# Buscar itens compatíveis para torso e pés
response = requests.post(
    "http://localhost:8000/api/v1/clothing/compatible-items",
    json={
        "selected_item": selected_item,
        "target_regions": ["torso", "feet"],
        "top_k": 3
    }
)

suggestions = response.json()
print("Sugestões para torso:", suggestions["suggestions"]["torso"])
print("Sugestões para pés:", suggestions["suggestions"]["feet"])
```

### 2. 🆕 Buscar itens que combinam com uma cor

```python
# Buscar itens que combinam com vermelho
response = requests.post(
    "http://localhost:8000/api/v1/clothing/color-compatibility",
    json={
        "color": "red",
        "target_regions": ["torso", "legs"],
        "top_k": 3
    }
)

result = response.json()
print("Itens que combinam com vermelho:", result["suggestions"])
```

### 3. 🆕 Item específico com cor

```python
# Camiseta vermelha - buscar itens compatíveis
response = requests.post(
    "http://localhost:8000/api/v1/clothing/compatible-items",
    json={
        "selected_item": {
            "prompt": "t-shirt",
            "body_region": "torso",
            "name": "Camiseta",
            "color": "red"  # Cor dentro do selected_item
        },
        "target_regions": ["legs", "feet"],
        "top_k": 3
    }
)

result = response.json()
print("Itens compatíveis com camiseta vermelha:", result["suggestions"])
```

### 4. Completar um outfit

```python
# Usuário já tem calça e camiseta selecionadas
selected_items = [
    {
        "prompt": "pants",
        "body_region": "legs",
        "name": "Calça",
        "probability": 0.92
    },
    {
        "prompt": "t-shirt", 
        "body_region": "torso",
        "name": "Camiseta",
        "probability": 0.88
    }
]

# Buscar sugestões para completar o outfit
response = requests.post(
    "http://localhost:8000/api/v1/clothing/outfit-suggestions",
    json={
        "selected_items": selected_items,
        "top_k": 3
    }
)

result = response.json()
print("Regiões faltantes:", result["suggestions"]["missing_regions"])
print("Sugestões para pés:", result["suggestions"]["suggestions"]["feet"])
```

### 5. 🆕 Fluxo completo com cores

```python
# 1. Usuário tem uma camiseta vermelha
red_shirt = {
    "prompt": "t-shirt",
    "body_region": "torso",
    "name": "Camiseta",
    "color": "red"  # Cor dentro do item
}

# 2. Buscar itens que combinam com vermelho
color_response = requests.post(
    "http://localhost:8000/api/v1/clothing/color-compatibility",
    json={
        "color": "red",
        "target_regions": ["legs", "feet"],
        "top_k": 5
    }
)

# 3. Usuário seleciona calça azul das sugestões
blue_pants = {
    "prompt": "pants",
    "body_region": "legs",
    "name": "Calça",
    "color": "blue"  # Cor dentro do item
}

# 4. Buscar calçados considerando a combinação vermelho + azul
outfit_response = requests.post(
    "http://localhost:8000/api/v1/clothing/compatible-items",
    json={
        "selected_item": red_shirt,  # Mantém a cor vermelha
        "target_regions": ["feet"],
        "top_k": 3
    }
)
``` 