#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para análise completa de outfit usando imagem inteira
"""

import requests
import json
import os

# Configuração
API_BASE_URL = "http://localhost:8000"
TEST_IMAGE_PATH = "test_images/outfit_test.jpg"

def test_complete_outfit_analysis():
    """Testa a análise completa de outfit usando a imagem inteira"""
    print("🧪 TESTE DE ANÁLISE COMPLETA DE OUTFIT")
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
            
            # Exibir resultados da análise completa
            display_complete_analysis_results(result)
            
            return True
        else:
            print(f"❌ Erro na análise: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao enviar imagem: {e}")
        return False

def display_complete_analysis_results(result):
    """Exibe os resultados da análise completa"""
    print("\n🎯 ANÁLISE COMPLETA DO OUTFIT")
    print("=" * 50)
    
    # Informações básicas
    print(f"📋 Arquivo: {result.get('filename', 'N/A')}")
    print(f"🆔 Session ID: {result.get('session_id', 'N/A')}")
    
    # Análise da imagem completa
    complete_analysis = result.get('complete_outfit_analysis', {})
    
    if 'error' in complete_analysis:
        print(f"\n❌ Erro na análise completa: {complete_analysis['error']}")
        return
    
    full_image_analysis = complete_analysis.get('full_image_analysis', {})
    
    print(f"\n🌟 ANÁLISE DA IMAGEM COMPLETA:")
    
    # Rating geral
    overall_rating = full_image_analysis.get('overall_rating', {})
    if overall_rating:
        print(f"   Avaliação: {overall_rating.get('emoji', '')} {overall_rating.get('level', 'N/A')}")
        print(f"   Descrição: {overall_rating.get('description', 'N/A')}")
        print(f"   Score de coordenação: {overall_rating.get('coordination_score', 0):.3f}")
        print(f"   Estilo dominante: {overall_rating.get('dominant_style', 'N/A')}")
        print(f"   Confiança do estilo: {overall_rating.get('style_confidence', 0):.3f}")
    
    # Análise de estilo
    style_analysis = full_image_analysis.get('style_analysis', {})
    if style_analysis:
        print(f"\n👔 ANÁLISE DE ESTILO:")
        all_scores = style_analysis.get('all_style_scores', {})
        for style, score in all_scores.items():
            print(f"   • {style.title()}: {score:.3f}")
    
    # Análise de coordenação
    coordination_analysis = full_image_analysis.get('coordination_analysis', {})
    if coordination_analysis:
        print(f"\n🎨 ANÁLISE DE COORDENAÇÃO:")
        all_scores = coordination_analysis.get('all_coordination_scores', {})
        for aspect, score in all_scores.items():
            print(f"   • {aspect.replace('_', ' ').title()}: {score:.3f}")
    
    # Insights
    insights = full_image_analysis.get('insights', [])
    if insights:
        print(f"\n💡 INSIGHTS:")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. {insight}")
    
    # Comparação com análise individual
    individual_analysis = complete_analysis.get('individual_parts_analysis', {})
    if individual_analysis:
        print(f"\n🔗 COMPARAÇÃO COM ANÁLISE INDIVIDUAL:")
        individual_score = individual_analysis.get('compatibility_score', 0)
        overall_score = overall_rating.get('coordination_score', 0)
        
        print(f"   • Score individual (partes): {individual_score:.3f}")
        print(f"   • Score geral (imagem completa): {overall_score:.3f}")
        
        if abs(individual_score - overall_score) < 0.1:
            print(f"   ✅ Análises consistentes")
        else:
            print(f"   ⚠️  Diferença entre análises - CLIP vê o conjunto de forma diferente")
    
    # Resumo
    summary = result.get('summary', {})
    print(f"\n📊 RESUMO:")
    print(f"   • Peças detectadas: {summary.get('total_parts_detected', 0)}")
    print(f"   • Peças classificadas: {summary.get('total_parts_classified', 0)}")
    print(f"   • Score individual: {summary.get('compatibility_score', 0):.3f}")
    print(f"   • Score geral: {summary.get('overall_coordination_score', 0):.3f}")

def explain_analysis_differences():
    """Explica as diferenças entre análise individual e completa"""
    print("\n🧠 DIFERENÇAS ENTRE ANÁLISES")
    print("=" * 50)
    
    print("\n📋 ANÁLISE INDIVIDUAL (ANTES):")
    print("   • Separa imagem em partes (torso, legs, feet)")
    print("   • Classifica cada parte individualmente")
    print("   • Compara embeddings de texto das classificações")
    print("   ❌ Não vê o outfit como um todo")
    print("   ❌ Perde contexto visual")
    print("   ❌ Não considera harmonia geral")
    
    print("\n🎯 ANÁLISE COMPLETA (AGORA):")
    print("   • Usa a imagem inteira da pessoa")
    print("   • CLIP analisa o outfit como um conjunto")
    print("   • Considera coordenação, estilo, cores")
    print("   ✅ Vê o outfit como um todo")
    print("   ✅ Considera contexto visual completo")
    print("   ✅ Avalia harmonia geral")
    
    print("\n💡 VANTAGENS DA ANÁLISE COMPLETA:")
    print("   • Mais precisa e realista")
    print("   • Considera como as peças realmente se veem juntas")
    print("   • Avalia coordenação de cores e estilo")
    print("   • Insights mais relevantes")

if __name__ == "__main__":
    print("🚀 Iniciando teste de análise completa de outfit...")
    
    # Executar teste principal
    success = test_complete_outfit_analysis()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        explain_analysis_differences()
    else:
        print("\n❌ Teste falhou!")
    
    print("\n" + "=" * 50)
    print("🎯 Para testar a análise completa:")
    print("   1. Coloque uma imagem com uma pessoa vestida em test_images/outfit_test.jpg")
    print("   2. Execute: python test_complete_outfit_analysis.py")
    print("   3. Compare análise individual vs completa")
    print("   4. Observe como o CLIP vê o outfit como um todo!")
    print("=" * 50) 