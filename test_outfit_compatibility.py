#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para análise de compatibilidade de outfit
"""

import requests
import json
import os
from datetime import datetime

# Configuração
API_BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_images/outfit_test.jpg"  # Ajuste o caminho conforme necessário

def test_outfit_compatibility():
    """Testa a análise de compatibilidade de outfit"""
    print("🧪 TESTE DE COMPATIBILIDADE DE OUTFIT")
    print("=" * 50)
    
    # Verificar se a API está rodando
    try:
        health_response = requests.get(f"{API_BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ API não está respondendo")
            return False
        print("✅ API está funcionando")
    except Exception as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False
    
    # Verificar se existe uma imagem de teste
    if not os.path.exists(TEST_IMAGE_PATH):
        print(f"⚠️  Imagem de teste não encontrada: {TEST_IMAGE_PATH}")
        print("   Você pode usar qualquer imagem com uma pessoa vestida")
        return False
    
    # Fazer upload da imagem para análise
    print(f"\n📤 Enviando imagem: {TEST_IMAGE_PATH}")
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as image_file:
            files = {'file': (os.path.basename(TEST_IMAGE_PATH), image_file, 'image/jpeg')}
            
            response = requests.post(
                f"{API_BASE_URL}/api/v1/analysis/complete",
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Análise completa realizada com sucesso!")
            
            # Exibir resultados da compatibilidade
            display_compatibility_results(result)
            
            return True
        else:
            print(f"❌ Erro na análise: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar imagem: {e}")
        return False

def display_compatibility_results(result):
    """Exibe os resultados da análise de compatibilidade"""
    print("\n🎯 RESULTADOS DA COMPATIBILIDADE")
    print("=" * 50)
    
    # Informações básicas
    print(f"📋 Arquivo: {result.get('filename', 'N/A')}")
    print(f"🆔 Session ID: {result.get('session_id', 'N/A')}")
    print(f"📅 Timestamp: {result.get('timestamp', 'N/A')}")
    
    # Peças detectadas
    classifications = result.get('classifications', {})
    print(f"\n👕 PEÇAS DETECTADAS ({len(classifications)}):")
    
    for region, data in classifications.items():
        if 'top_prediction' in data:
            prediction = data['top_prediction']
            print(f"   • {region.upper()}: {prediction['name']} ({prediction['percentage']})")
    
    # Análise de compatibilidade
    compatibility = result.get('outfit_compatibility', {})
    
    if 'error' in compatibility:
        print(f"\n❌ Erro na análise: {compatibility['error']}")
        return
    
    print(f"\n🌟 COMPATIBILIDADE DO OUTFIT:")
    print(f"   Score: {compatibility.get('compatibility_score', 0):.3f}")
    
    # Rating do outfit
    rating = compatibility.get('outfit_rating', {})
    if rating:
        print(f"   Avaliação: {rating.get('emoji', '')} {rating.get('level', 'N/A')}")
        print(f"   Descrição: {rating.get('description', 'N/A')}")
    
    # Compatibilidade entre pares
    pairwise = compatibility.get('pairwise_compatibility', {})
    if pairwise:
        print(f"\n🔗 COMPATIBILIDADE ENTRE PEÇAS:")
        for pair_key, pair_data in pairwise.items():
            part1 = pair_data['part1']
            part2 = pair_data['part2']
            similarity = pair_data['similarity']
            level = pair_data['compatibility_level']
            
            print(f"   • {part1['name']} vs {part2['name']}: {similarity:.3f} ({level})")
    
    # Sugestões
    suggestions = compatibility.get('suggestions', [])
    if suggestions:
        print(f"\n💡 SUGESTÕES DE MELHORIA:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
    
    # Resumo
    summary = result.get('summary', {})
    print(f"\n📊 RESUMO:")
    print(f"   • Peças detectadas: {summary.get('total_parts_detected', 0)}")
    print(f"   • Peças classificadas: {summary.get('total_parts_classified', 0)}")
    print(f"   • Pessoas detectadas: {summary.get('people_detected', 0)}")
    print(f"   • Score de compatibilidade: {summary.get('compatibility_score', 0):.3f}")

def demo_compatibility_scenarios():
    """Demonstra diferentes cenários de compatibilidade"""
    print("\n🎭 DEMONSTRAÇÃO DE CENÁRIOS")
    print("=" * 50)
    
    scenarios = [
        {
            "name": "Outfit Casual",
            "description": "Camiseta + Calça + Tênis",
            "expected_score": "0.6-0.8"
        },
        {
            "name": "Outfit Formal", 
            "description": "Terno + Sapatos",
            "expected_score": "0.7-0.9"
        },
        {
            "name": "Outfit Esportivo",
            "description": "Moletom + Shorts + Tênis",
            "expected_score": "0.5-0.7"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n📋 {scenario['name']}")
        print(f"   Descrição: {scenario['description']}")
        print(f"   Score esperado: {scenario['expected_score']}")
    
    print("\n💡 Dica: Teste com diferentes tipos de outfit para ver como o sistema avalia a compatibilidade!")

if __name__ == "__main__":
    print("🚀 Iniciando teste de compatibilidade de outfit...")
    
    # Executar teste principal
    success = test_outfit_compatibility()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        demo_compatibility_scenarios()
    else:
        print("\n❌ Teste falhou!")
    
    print("\n" + "=" * 50)
    print("🎯 Para testar:")
    print("   1. Coloque uma imagem com uma pessoa vestida em test_images/outfit_test.jpg")
    print("   2. Execute: python test_outfit_compatibility.py")
    print("   3. Ou use o Swagger UI: http://localhost:8000/docs")
    print("=" * 50) 