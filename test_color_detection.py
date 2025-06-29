#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para detecção de cores de peças de roupa
"""

import requests
import json
import os

# Configuração
API_BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_images/outfit_test.jpg"

def test_color_detection():
    """Testa a detecção de cores das peças de roupa"""
    print("🎨 TESTE DE DETECÇÃO DE CORES")
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
            
            # Exibir resultados da detecção de cores
            display_color_detection_results(result)
            
            return True
        else:
            print(f"❌ Erro na análise: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar imagem: {e}")
        return False

def display_color_detection_results(result):
    """Exibe os resultados da detecção de cores"""
    print("\n🎨 DETECÇÃO DE CORES DAS PEÇAS")
    print("=" * 50)
    
    # Informações básicas
    print(f"📋 Arquivo: {result.get('filename', 'N/A')}")
    print(f"🆔 Session ID: {result.get('session_id', 'N/A')}")
    
    # Análise de cores por parte
    classifications = result.get('classifications', {})
    print(f"\n👕 CORES DETECTADAS ({len(classifications)} peças):")
    
    for region, data in classifications.items():
        if 'top_prediction' in data and 'color_analysis' in data:
            prediction = data['top_prediction']
            color_analysis = data['color_analysis']
            
            print(f"\n   🎯 {region.upper()}:")
            print(f"      Peça: {prediction['name']} ({prediction['percentage']})")
            
            if 'error' not in color_analysis:
                dominant_color = color_analysis.get('dominant_color', 'unknown')
                confidence = color_analysis.get('confidence', 0)
                method = color_analysis.get('detection_method', 'unknown')
                
                print(f"      Cor: {dominant_color.title()}")
                print(f"      Confiança: {confidence:.3f}")
                print(f"      Método: {method}")
                
                # Mostrar outras cores detectadas
                all_colors = color_analysis.get('all_colors', {})
                if all_colors:
                    print(f"      Outras cores:")
                    # Ordenar por confiança e mostrar top 3
                    sorted_colors = sorted(all_colors.items(), key=lambda x: x[1], reverse=True)[:3]
                    for color_name, color_score in sorted_colors:
                        if color_name != dominant_color:
                            print(f"        • {color_name.title()}: {color_score:.3f}")
            else:
                print(f"      ❌ Erro na detecção de cor: {color_analysis['error']}")
    
    # Análise de compatibilidade de cores
    print(f"\n🌈 ANÁLISE DE COMPATIBILIDADE DE CORES:")
    
    # Extrair cores detectadas
    detected_colors = {}
    for region, data in classifications.items():
        if 'color_analysis' in data and 'error' not in data['color_analysis']:
            color = data['color_analysis'].get('dominant_color')
            if color and color != 'unknown':
                detected_colors[region] = color
    
    if len(detected_colors) >= 2:
        print(f"   Cores detectadas: {', '.join([f'{region}: {color}' for region, color in detected_colors.items()])}")
        
        # Verificar compatibilidade básica
        color_compatibility = analyze_color_compatibility(detected_colors)
        print(f"   Compatibilidade: {color_compatibility}")
    else:
        print(f"   ⚠️  Poucas cores detectadas para análise de compatibilidade")

def analyze_color_compatibility(detected_colors):
    """Análise básica de compatibilidade de cores"""
    # Cores complementares
    complementary_pairs = [
        ('red', 'blue'), ('red', 'green'),
        ('blue', 'orange'), ('yellow', 'purple'),
        ('black', 'white'), ('black', 'any'),
        ('white', 'any')
    ]
    
    # Cores neutras
    neutral_colors = ['black', 'white', 'gray', 'beige', 'cream', 'navy']
    
    colors_list = list(detected_colors.values())
    
    # Verificar se há cores neutras
    has_neutral = any(color in neutral_colors for color in colors_list)
    
    # Verificar pares complementares
    for color1, color2 in complementary_pairs:
        if (color1 in colors_list and color2 in colors_list) or \
           (color1 in colors_list and color2 == 'any' and len(colors_list) > 1):
            return "Excelente - Cores complementares"
    
    if has_neutral:
        return "Boa - Cores neutras presentes"
    
    return "Regular - Considere adicionar cores neutras"

def explain_color_detection():
    """Explica como funciona a detecção de cores"""
    print("\n🧠 COMO FUNCIONA A DETECÇÃO DE CORES")
    print("=" * 50)
    
    print("\n1️⃣ ANÁLISE DE IMAGEM:")
    print("   • Processamento tradicional de pixels")
    print("   • Comparação com cores de referência")
    print("   • Contagem de pixels por cor")
    print("   • Detecção da cor predominante")
    
    print("\n2️⃣ ANÁLISE CLIP:")
    print("   • Prompts: 'red colored clothing', 'blue colored clothing', etc.")
    print("   • CLIP analisa o contexto da cor na roupa")
    print("   • Mais inteligente que análise de pixels")
    print("   • Considera iluminação e contexto")
    
    print("\n3️⃣ COMBINAÇÃO:")
    print("   • Se ambos concordam: Boost na confiança")
    print("   • Se discordam: Prioriza CLIP")
    print("   • Resultado final mais preciso")
    
    print("\n4️⃣ VANTAGENS:")
    print("   ✅ Detecta cores reais (não apenas pixels)")
    print("   ✅ Considera contexto da roupa")
    print("   ✅ Funciona com diferentes iluminações")
    print("   ✅ Combina dois métodos para maior precisão")

if __name__ == "__main__":
    print("🚀 Iniciando teste de detecção de cores...")
    
    # Executar teste principal
    success = test_color_detection()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        explain_color_detection()
    else:
        print("\n❌ Teste falhou!")
    
    print("\n" + "=" * 50)
    print("🎯 Para testar a detecção de cores:")
    print("   1. Coloque uma imagem com uma pessoa vestida em test_images/outfit_test.jpg")
    print("   2. Execute: python test_color_detection.py")
    print("   3. Observe as cores detectadas em cada peça!")
    print("   4. Veja a análise de compatibilidade de cores")
    print("=" * 50) 