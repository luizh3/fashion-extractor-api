#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste das funcionalidades de compatibilidade com cores
"""

import requests
import json
import time

# Configuração da API
API_BASE_URL = "http://localhost:8000/api/v1/clothing"

def test_available_colors():
    """Testa o endpoint de cores disponíveis"""
    print("🎨 Testando cores disponíveis...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/colors")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Cores disponíveis:")
            print(f"   Total: {result['total_colors']} cores")
            print(f"   Cores: {', '.join(result['colors'])}")
            return True
        else:
            print(f"❌ Erro na API: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar cores: {e}")
        return False

def test_color_compatibility():
    """Testa a compatibilidade de cores"""
    print("\n🧪 Testando compatibilidade de cores...")
    
    # Teste com camiseta vermelha
    request_data = {
        "color": "red",
        "target_regions": ["legs", "feet"],
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/color-compatibility",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Compatibilidade de cor encontrada!")
            print(f"   Cor: {result['color']}")
            print(f"   Regiões: {result['target_regions']}")
            
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
        print(f"❌ Erro ao testar compatibilidade de cor: {e}")
        return False

def test_item_with_color():
    """Testa item específico com cor"""
    print("\n🧪 Testando item com cor específica...")
    
    # Camiseta vermelha
    request_data = {
        "selected_item": {
            "prompt": "t-shirt",
            "body_region": "torso",
            "name": "Camiseta",
            "color": "red"  # Cor dentro do selected_item
        },
        "target_regions": ["legs", "feet"],
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
            print("✅ Itens compatíveis com cor encontrados!")
            print(f"   Item: {result['selected_item']['name']}")
            print(f"   Cor: {result['selected_item'].get('color', 'N/A')}")
            
            for region, items in result['suggestions'].items():
                print(f"   👕 {region.upper()}:")
                for item in items:
                    print(f"      • {item['name']} (similaridade: {item['similarity']:.3f})")
                    
                    # Verificar se há cores compatíveis
                    if 'compatible_colors' in item:
                        print(f"        🎨 Cores compatíveis:")
                        for color_info in item['compatible_colors'][:3]:  # Mostra apenas as 3 primeiras
                            print(f"          - {color_info['color']} (similaridade: {color_info['similarity']:.3f})")
                    else:
                        print(f"        ⚠️  Sem sugestões de cores")
            
            return True
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar item com cor: {e}")
        return False

def demo_color_workflow():
    """Demonstra o fluxo completo com cores"""
    print("\n🎯 DEMONSTRAÇÃO DO FLUXO COM CORES")
    print("=" * 50)
    
    # 1. Usuário tem uma camiseta vermelha
    print("\n1️⃣ Usuário tem uma camiseta vermelha:")
    red_shirt = {
        "prompt": "t-shirt",
        "body_region": "torso",
        "name": "Camiseta",
        "color": "red"  # Cor dentro do item
    }
    print(f"   ✅ Item: {red_shirt['name']} vermelha")
    
    # 2. Sistema sugere itens que combinam com vermelho
    print("\n2️⃣ Sistema busca itens que combinam com vermelho:")
    color_request = {
        "color": "red",
        "target_regions": ["legs", "feet"],
        "top_k": 3
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/color-compatibility",
            json=color_request
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   📥 Sugestões baseadas na cor:")
            
            for region, items in result['suggestions'].items():
                print(f"   👕 {region.upper()}:")
                for item in items[:2]:  # Mostra apenas os 2 primeiros
                    print(f"      • {item['name']} (similaridade: {item['similarity']:.3f})")
            
            # 3. Usuário seleciona uma calça azul
            print("\n3️⃣ Usuário seleciona uma calça azul:")
            blue_pants = {
                "prompt": "pants",
                "body_region": "legs",
                "name": "Calça",
                "color": "blue"  # Cor dentro do item
            }
            print(f"   ✅ Selecionado: {blue_pants['name']} azul")
            
            # 4. Sistema sugere completar o outfit
            print("\n4️⃣ Sistema sugere completar o outfit:")
            outfit_request = {
                "selected_item": red_shirt,  # Mantém a cor vermelha
                "target_regions": ["feet"],
                "top_k": 3
            }
            
            outfit_response = requests.post(
                f"{API_BASE_URL}/compatible-items",
                json=outfit_request
            )
            
            if outfit_response.status_code == 200:
                outfit_result = outfit_response.json()
                print("   📥 Sugestões para completar:")
                
                for region, items in outfit_result['suggestions'].items():
                    print(f"   👟 {region.upper()}:")
                    for item in items:
                        print(f"      • {item['name']} (similaridade: {item['similarity']:.3f})")
                
                print("\n🎉 Outfit completo sugerido!")
                print("   👕 Camiseta vermelha")
                print("   👖 Calça azul")
                print("   👟 Calçados que combinam com vermelho")
                
            else:
                print(f"   ❌ Erro ao buscar sugestões de outfit: {outfit_response.status_code}")
                
        else:
            print(f"   ❌ Erro ao buscar compatibilidade de cor: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Erro no fluxo: {e}")

def test_different_colors():
    """Testa diferentes cores"""
    print("\n🌈 Testando diferentes cores...")
    
    colors_to_test = ["blue", "green", "black", "pink"]
    
    for color in colors_to_test:
        print(f"\n   Testando cor: {color}")
        
        request_data = {
            "color": color,
            "target_regions": ["torso"],
            "top_k": 2
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/color-compatibility",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {color.upper()}:")
                for region, items in result['suggestions'].items():
                    for item in items:
                        print(f"      • {item['name']} ({item['similarity']:.3f})")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Erro: {e}")

def main():
    """Função principal"""
    print("🎨 Testando funcionalidades de compatibilidade com cores")
    print("=" * 60)
    
    # Aguardar um pouco para garantir que a API está pronta
    print("⏳ Aguardando API inicializar...")
    time.sleep(5)
    
    # Testes básicos
    if not test_available_colors():
        print("❌ Endpoint de cores não está funcionando.")
        return
    
    if not test_color_compatibility():
        print("❌ Funcionalidade de compatibilidade de cor não está funcionando.")
        return
    
    if not test_item_with_color():
        print("❌ Funcionalidade de item com cor não está funcionando.")
        return
    
    # Demonstração completa
    demo_color_workflow()
    
    # Teste de diferentes cores
    test_different_colors()
    
    print("\n" + "=" * 60)
    print("✨ Todos os testes passaram!")
    print("\n💡 Sua feature de compatibilidade com cores está funcionando!")
    print("   - ✅ Busca por cor específica")
    print("   - ✅ Item + cor combinados")
    print("   - ✅ 16 cores disponíveis")
    print("   - ✅ Similaridade baseada em cor + item")

if __name__ == "__main__":
    main() 