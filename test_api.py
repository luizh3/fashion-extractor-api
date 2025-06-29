import requests
import base64
import json

# Configuração
BASE_URL = "http://localhost:8000"
TEST_IMAGE = "shorts.jpg"

def test_health():
    """Testa o endpoint de saúde"""
    print("🔍 Testando endpoint de saúde...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print()

def test_classify():
    """Testa classificação de roupas"""
    print("👕 Testando classificação de roupas...")
    
    # Upload de arquivo
    with open(TEST_IMAGE, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/api/v1/clothing/classify", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Resposta: {result}")
    
    # Mostra as classificações de forma mais legível
    if "predictions" in result:
        print(f"🎯 Classificações:")
        for i, pred in enumerate(result["predictions"][:5]):  # Top 5
            print(f"   {i+1}. {pred['category']} ({pred['name']}): {pred['percentage']}")
    
    if "top_prediction" in result:
        top = result["top_prediction"]
        print(f"🏆 Top predição: {top['category']} ({top['name']}) - {top['percentage']}")
    print()

def test_body_parts_detection():
    """Testa detecção de partes do corpo"""
    print("🦵 Testando detecção de partes do corpo...")
    
    with open(TEST_IMAGE, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/api/v1/body-parts/detect", files=files)
    
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print()

def test_body_parts_extraction():
    """Testa extração e salvamento de partes do corpo"""
    print("💾 Testando extração e salvamento de partes do corpo...")
    
    with open(TEST_IMAGE, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/api/v1/body-parts/extract", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Resposta: {result}")
    
    # Testa acessar as imagens salvas
    if "body_parts" in result:
        for part_name, url in result["body_parts"].items():
            print(f"Testando acesso a {part_name}: {url}")
            img_response = requests.get(url)
            print(f"Status da imagem: {img_response.status_code}")
    print()

def test_complete_analysis():
    """Testa análise completa"""
    print("🔍 Testando análise completa...")
    
    with open(TEST_IMAGE, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{BASE_URL}/api/v1/analysis/complete", files=files)
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Resposta: {result}")
    
    # Verifica se a análise foi bem-sucedida
    if result.get("success"):
        print(f"✅ Análise completa realizada com sucesso!")
        print(f"📊 Resumo:")
        print(f"   - Partes detectadas: {result['summary']['total_parts_detected']}")
        print(f"   - Partes classificadas: {result['summary']['total_parts_classified']}")
        print(f"   - Pessoas detectadas: {result['summary']['people_detected']}")
        
        # Mostra classificações de cada parte
        if "classifications" in result:
            print(f"🎯 Classificações por parte:")
            for part_name, classification in result["classifications"].items():
                top_pred = classification["top_prediction"]
                print(f"   - {part_name}: {top_pred['category']} ({top_pred['name']}) - {top_pred['percentage']}")
        
        # Testa acessar as imagens salvas
        if "body_parts" in result:
            print(f"🖼️ Testando acesso às imagens salvas:")
            for part_name, url in result["body_parts"].items():
                print(f"   - {part_name}: {url}")
                img_response = requests.get(url)
                print(f"     Status: {img_response.status_code}")
    else:
        print(f"❌ Erro na análise: {result.get('error', 'Erro desconhecido')}")
    print()

def test_margin_config():
    """Testa configuração de margem"""
    print("⚙️ Testando configuração de margem...")
    
    # Ver configuração atual
    response = requests.get(f"{BASE_URL}/api/v1/config/margin")
    print(f"Configuração atual - Status: {response.status_code}")
    print(f"Configuração atual: {response.json()}")
    
    # Definir nova margem
    new_margin = {"margin_percentage": 0.20}
    response = requests.put(f"{BASE_URL}/api/v1/config/margin", 
                          json=new_margin)
    print(f"Definir margem - Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print()

def test_base64_endpoints():
    """Testa endpoints com base64"""
    print("📄 Testando endpoints com base64...")
    
    # Converte imagem para base64
    with open(TEST_IMAGE, "rb") as f:
        image_data = f.read()
        base64_string = base64.b64encode(image_data).decode('utf-8')
    
    # Testa classificação com base64
    payload = {"image": base64_string}
    response = requests.post(f"{BASE_URL}/api/v1/clothing/classify/base64", 
                           json=payload)
    print(f"Classificação base64 - Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    
    # Testa detecção de partes com base64
    response = requests.post(f"{BASE_URL}/api/v1/body-parts/detect/base64", 
                           json=payload)
    print(f"Detecção base64 - Status: {response.status_code}")
    print(f"Resposta: {response.json()}")
    print()

if __name__ == "__main__":
    print("🚀 Iniciando testes da API...")
    print("=" * 50)
    
    try:
        test_health()
        test_classify()
        test_body_parts_detection()
        test_body_parts_extraction()
        test_complete_analysis()
        test_margin_config()
        test_base64_endpoints()
        
        print("✅ Todos os testes concluídos!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API.")
        print("Certifique-se de que a API está rodando em http://localhost:8000")
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo {TEST_IMAGE} não encontrado.")
        print("Certifique-se de que o arquivo existe no diretório atual.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}") 