#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das funcionalidades de compatibilidade de roupas e sugestões de outfit
"""

import requests
import json
import base64
from PIL import Image
import io

# Configuração da API
API_BASE_URL = "http://localhost:8000/api/v1/clothing"

def test_classify_clothing():
    """Testa a classificação básica de roupas"""
    print("🧪 Testando classificação de roupas...")
    
    # Simular uma imagem (você pode substituir por uma imagem real)
    # Por enquanto, vamos usar um exemplo com dados mockados
    mock_classification = {
        "predictions": [
            {
                "category": 0,
                "name": "Camiseta",
                "prompt": "t-shirt",
                "body_region": "torso",
                "probability": 0.95,
                "percentage": "95.00%"
            },
            {
                "category": 3,
                "name": "Jaqueta",
                "prompt": "jacket",
                "body_region": "torso",
                "probability": 0.03,
                "percentage": "3.00%"
            }
        ],
        "top_prediction": {
            "category": 0,
            "name": "Camiseta",
            "prompt": "t-shirt",
            "body_region": "torso",
            "probability": 0.95,
            "percentage": "95.00%"
        }
    }
    
    print("✅ Classificação simulada:")
    print(json.dumps(mock_classification, indent=2, ensure_ascii=False))
    return mock_classification

def test_compatible_items():
    """Testa a busca por itens compatíveis"""
    print("\n🧪 Testando busca por itens compatíveis...")
    
    # Dados de teste
    selected_item = {
        "prompt": "t-shirt",
        "body_region": "torso",
        "name": "Camiseta",
        "probability": 0.95
    }
    
    request_data = {
        "selected_item": selected_item,
        "target_regions": ["legs", "feet"],  # Buscar apenas para pernas e pés
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/compatible-items",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Itens compatíveis encontrados:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API. Certifique-se de que o servidor está rodando.")
        print("💡 Execute: uvicorn api:app --reload --host 0.0.0.0 --port 8000")

def test_outfit_suggestions():
    """Testa as sugestões de outfit completo"""
    print("\n🧪 Testando sugestões de outfit...")
    
    # Dados de teste - usuário selecionou uma calça
    selected_items = [
        {
            "prompt": "pants",
            "body_region": "legs",
            "name": "Calça",
            "probability": 0.92
        }
    ]
    
    request_data = {
        "selected_items": selected_items,
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/outfit-suggestions",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sugestões de outfit:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API. Certifique-se de que o servidor está rodando.")

def test_body_regions():
    """Testa o endpoint de regiões do corpo"""
    print("\n🧪 Testando regiões do corpo...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/body-regions")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Regiões do corpo disponíveis:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API. Certifique-se de que o servidor está rodando.")

def demo_complete_workflow():
    """Demonstra o fluxo completo de uso"""
    print("\n🎯 DEMONSTRAÇÃO DO FLUXO COMPLETO")
    print("=" * 50)
    
    print("\n1️⃣ Usuário classifica uma imagem de calça:")
    pants_classification = {
        "top_prediction": {
            "category": 1,
            "name": "Calça",
            "prompt": "pants",
            "body_region": "legs",
            "probability": 0.88,
            "percentage": "88.00%"
        }
    }
    print(f"   ✅ Classificado como: {pants_classification['top_prediction']['name']}")
    
    print("\n2️⃣ Sistema busca itens compatíveis para torso e pés:")
    compatible_request = {
        "selected_item": pants_classification["top_prediction"],
        "target_regions": ["torso", "feet"],
        "top_k": 3
    }
    
    print("   📤 Enviando requisição para /compatible-items...")
    print(f"   📋 Dados: {json.dumps(compatible_request, indent=2, ensure_ascii=False)}")
    
    print("\n3️⃣ Sistema retorna sugestões:")
    mock_suggestions = {
        "suggestions": {
            "torso": [
                {"name": "Camiseta", "prompt": "t-shirt", "similarity": 0.85},
                {"name": "Blusa", "prompt": "blouse", "similarity": 0.82},
                {"name": "Suéter", "prompt": "sweater", "similarity": 0.78}
            ],
            "feet": [
                {"name": "Sapatos", "prompt": "shoes", "similarity": 0.91},
                {"name": "Botas", "prompt": "boots", "similarity": 0.87},
                {"name": "Sandálias", "prompt": "sandals", "similarity": 0.83}
            ]
        }
    }
    
    print("   📥 Resposta recebida:")
    for region, items in mock_suggestions["suggestions"].items():
        print(f"   👕 {region.upper()}:")
        for item in items:
            print(f"      • {item['name']} (similaridade: {item['similarity']:.2f})")
    
    print("\n4️⃣ Usuário seleciona uma camiseta:")
    selected_outfit = [
        pants_classification["top_prediction"],
        {
            "prompt": "t-shirt",
            "body_region": "torso",
            "name": "Camiseta",
            "probability": 0.85
        }
    ]
    
    print("   ✅ Outfit atual: Calça + Camiseta")
    
    print("\n5️⃣ Sistema sugere completar com calçados:")
    outfit_request = {
        "selected_items": selected_outfit,
        "top_k": 3
    }
    
    print("   📤 Enviando requisição para /outfit-suggestions...")
    print("   📥 Sugestões para completar o outfit:")
    
    mock_outfit_suggestions = {
        "missing_regions": ["feet"],
        "suggestions": {
            "feet": [
                {"name": "Sapatos", "prompt": "shoes", "similarity": 0.89},
                {"name": "Botas", "prompt": "boots", "similarity": 0.85},
                {"name": "Sandálias", "prompt": "sandals", "similarity": 0.81}
            ]
        }
    }
    
    for item in mock_outfit_suggestions["suggestions"]["feet"]:
        print(f"      👟 {item['name']} (similaridade: {item['similarity']:.2f})")
    
    print("\n🎉 Outfit completo sugerido!")
    print("   👖 Calça")
    print("   👕 Camiseta") 
    print("   👟 Sapatos")

if __name__ == "__main__":
    print("🚀 Testando funcionalidades de compatibilidade de roupas")
    print("=" * 60)
    
    # Testes individuais
    test_classify_clothing()
    test_compatible_items()
    test_outfit_suggestions()
    test_body_regions()
    
    # Demonstração completa
    demo_complete_workflow()
    
    print("\n" + "=" * 60)
    print("✨ Testes concluídos!")
    print("\n💡 Para usar em produção:")
    print("   1. Inicie o servidor: uvicorn api:app --reload")
    print("   2. Use os endpoints /compatible-items e /outfit-suggestions")
    print("   3. Integre com seu frontend para criar a experiência de seleção") 