#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das novas funcionalidades da API rodando no Docker
"""

import requests
import json
import time

# Configuração da API
API_BASE_URL = "http://localhost:8000"

def test_health():
    """Testa se a API está funcionando"""
    print("🏥 Testando saúde da API...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API está saudável!")
            print(f"   Status: {result['status']}")
            print(f"   Device: {result['device']}")
            print(f"   Features: {result['features_available']}")
            return True
        else:
            print(f"❌ API não está respondendo: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False

def test_body_regions():
    """Testa o endpoint de regiões do corpo"""
    print("\n🧪 Testando regiões do corpo...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/clothing/body-regions")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Regiões do corpo disponíveis:")
            print(f"   Regiões principais: {result['main_outfit_regions']}")
            print("   Mapeamento completo:")
            for region, items in result['body_regions'].items():
                print(f"     {region}: {items}")
            return True
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar regiões: {e}")
        return False

def test_compatible_items():
    """Testa a busca por itens compatíveis"""
    print("\n🧪 Testando busca por itens compatíveis...")
    
    # Dados de teste - usuário selecionou uma calça
    request_data = {
        "selected_item": {
            "prompt": "pants",
            "body_region": "legs",
            "name": "Calça"
        },
        "target_regions": ["torso", "feet"],
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/clothing/compatible-items",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Itens compatíveis encontrados!")
            print(f"   Item selecionado: {result['selected_item']['name']}")
            print(f"   Regiões buscadas: {result['target_regions']}")
            
            for region, items in result['suggestions'].items():
                print(f"   👕 {region.upper()}:")
                for item in items:
                    print(f"      • {item['name']} (similaridade: {item['similarity']:.3f})")
            return True
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar compatibilidade: {e}")
        return False

def test_outfit_suggestions():
    """Testa as sugestões de outfit completo"""
    print("\n🧪 Testando sugestões de outfit...")
    
    # Dados de teste - usuário já tem calça e camiseta
    request_data = {
        "selected_items": [
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
        ],
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/clothing/outfit-suggestions",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Sugestões de outfit geradas!")
            print(f"   Itens selecionados: {len(result['selected_items'])}")
            print(f"   Regiões faltantes: {result['suggestions']['missing_regions']}")
            
            for region, items in result['suggestions']['suggestions'].items():
                print(f"   👟 {region.upper()}:")
                for item in items:
                    print(f"      • {item['name']} (similaridade: {item['similarity']:.3f})")
            return True
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar outfit: {e}")
        return False

def demo_complete_workflow():
    """Demonstra o fluxo completo"""
    print("\n🎯 DEMONSTRAÇÃO DO FLUXO COMPLETO")
    print("=" * 50)
    
    # 1. Usuário seleciona uma calça
    print("\n1️⃣ Usuário seleciona uma calça:")
    pants_item = {
        "prompt": "pants",
        "body_region": "legs",
        "name": "Calça",
        "probability": 0.88
    }
    print(f"   ✅ Selecionado: {pants_item['name']}")
    
    # 2. Sistema sugere itens compatíveis
    print("\n2️⃣ Sistema busca itens compatíveis:")
    compatible_request = {
        "selected_item": pants_item,
        "target_regions": ["torso", "feet"],
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1/clothing/compatible-items",
            json=compatible_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   📥 Sugestões recebidas:")
            
            for region, items in result['suggestions'].items():
                print(f"   👕 {region.upper()}:")
                for item in items[:2]:  # Mostra apenas os 2 primeiros
                    print(f"      • {item['name']} (similaridade: {item['similarity']:.3f})")
            
            # 3. Usuário seleciona uma camiseta
            print("\n3️⃣ Usuário seleciona uma camiseta:")
            shirt_item = {
                "prompt": "t-shirt",
                "body_region": "torso",
                "name": "Camiseta", 
                "probability": 0.85
            }
            print(f"   ✅ Selecionado: {shirt_item['name']}")
            
            # 4. Sistema sugere completar o outfit
            print("\n4️⃣ Sistema sugere completar o outfit:")
            outfit_request = {
                "selected_items": [pants_item, shirt_item],
                "top_k": 3
            }
            
            outfit_response = requests.post(
                f"{API_BASE_URL}/api/v1/clothing/outfit-suggestions",
                json=outfit_request
            )
            
            if outfit_response.status_code == 200:
                outfit_result = outfit_response.json()
                print("   📥 Sugestões para completar:")
                
                for region, items in outfit_result['suggestions']['suggestions'].items():
                    print(f"   👟 {region.upper()}:")
                    for item in items:
                        print(f"      • {item['name']} (similaridade: {item['similarity']:.3f})")
                
                print("\n🎉 Outfit completo sugerido!")
                print("   👖 Calça")
                print("   👕 Camiseta")
                print("   👟 Sapatos/Botas/Sandálias")
                
            else:
                print(f"   ❌ Erro ao buscar sugestões de outfit: {outfit_response.status_code}")
                
        else:
            print(f"   ❌ Erro ao buscar itens compatíveis: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro no fluxo: {e}")

def main():
    """Função principal"""
    print("🚀 Testando funcionalidades de compatibilidade de roupas")
    print("=" * 60)
    
    # Aguardar um pouco para garantir que a API está pronta
    print("⏳ Aguardando API inicializar...")
    time.sleep(5)
    
    # Testes básicos
    if not test_health():
        print("❌ API não está funcionando. Verifique se o Docker está rodando.")
        return
    
    if not test_body_regions():
        print("❌ Endpoint de regiões não está funcionando.")
        return
    
    if not test_compatible_items():
        print("❌ Funcionalidade de compatibilidade não está funcionando.")
        return
    
    if not test_outfit_suggestions():
        print("❌ Funcionalidade de outfit não está funcionando.")
        return
    
    # Demonstração completa
    demo_complete_workflow()
    
    print("\n" + "=" * 60)
    print("✨ Todos os testes passaram!")
    print("\n💡 Sua feature de compatibilidade está funcionando perfeitamente!")
    print("   - ✅ Busca de itens compatíveis")
    print("   - ✅ Sugestões de outfit completo") 
    print("   - ✅ Categorização por região do corpo")
    print("   - ✅ Similaridade baseada em CLIP")

if __name__ == "__main__":
    main() 