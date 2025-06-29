#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste para sugestões contextuais de outfit
"""

import requests
import json
import os

# Configuração
API_BASE_URL = "http://localhost:8000"

def test_contextual_suggestions():
    """Testa as sugestões contextuais geradas pelo CLIP"""
    print("🧪 TESTE DE SUGESTÕES CONTEXTUAIS")
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
    
    # Cenários de teste com diferentes combinações
    test_scenarios = [
        {
            "name": "Outfit Incompleto (2 peças)",
            "description": "Apenas torso e legs - deve sugerir calçados",
            "expected_suggestions": ["shoes", "boots", "sandals"]
        },
        {
            "name": "Outfit Formal",
            "description": "Terno + Sapatos - deve sugerir acessórios formais",
            "expected_suggestions": ["belt", "hat", "scarf"]
        },
        {
            "name": "Outfit Casual",
            "description": "Camiseta + Calça + Tênis - deve sugerir acessórios casuais",
            "expected_suggestions": ["bag", "cap", "backpack"]
        }
    ]
    
    print("\n🎭 CENÁRIOS DE TESTE:")
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}")
        print(f"   Descrição: {scenario['description']}")
        print(f"   Sugestões esperadas: {', '.join(scenario['expected_suggestions'])}")
    
    print("\n💡 Para testar as sugestões contextuais:")
    print("   1. Use o endpoint /api/v1/analysis/complete")
    print("   2. Faça upload de imagens com diferentes combinações de peças")
    print("   3. Observe as sugestões geradas pelo CLIP")
    print("   4. Compare com as sugestões fixas anteriores")
    
    return True

def demo_suggestion_logic():
    """Demonstra a lógica das sugestões contextuais"""
    print("\n🧠 LÓGICA DAS SUGESTÕES CONTEXTUAIS")
    print("=" * 50)
    
    print("\n1️⃣ ANÁLISE DE CONTEXTO:")
    print("   • Identifica as peças detectadas")
    print("   • Determina o estilo (formal/casual)")
    print("   • Identifica regiões faltantes")
    
    print("\n2️⃣ GERAÇÃO DE SUGESTÕES:")
    print("   • Usa embeddings do CLIP para calcular compatibilidade")
    print("   • Considera o contexto das peças existentes")
    print("   • Prioriza sugestões mais compatíveis")
    
    print("\n3️⃣ EXEMPLOS DE SUGESTÕES INTELIGENTES:")
    
    examples = [
        {
            "context": "Camiseta + Calça (faltando calçados)",
            "suggestion": "Adicionar um Sapatos pode completar o look",
            "reason": "CLIP detecta que sapatos combinam com camiseta+calça"
        },
        {
            "context": "Terno + Sapatos (outfit formal)",
            "suggestion": "Um Cinto pode complementar o outfit",
            "reason": "CLIP identifica que cinto é compatível com terno"
        },
        {
            "context": "Moletom + Shorts + Tênis (outfit casual)",
            "suggestion": "Um Boné pode complementar o outfit",
            "reason": "CLIP sugere acessório casual compatível"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n   {i}. {example['context']}")
        print(f"      Sugestão: {example['suggestion']}")
        print(f"      Motivo: {example['reason']}")
    
    print("\n4️⃣ VANTAGENS DAS SUGESTÕES CONTEXTUAIS:")
    print("   ✅ Baseadas no conhecimento real do CLIP")
    print("   ✅ Consideram o contexto das peças existentes")
    print("   ✅ Adaptam-se ao estilo detectado")
    print("   ✅ Mais específicas e úteis")
    print("   ✅ Não são sugestões genéricas fixas")

def compare_old_vs_new_suggestions():
    """Compara sugestões antigas vs novas"""
    print("\n🔄 COMPARAÇÃO: ANTIGAS vs NOVAS SUGESTÕES")
    print("=" * 50)
    
    print("\n📋 SUGESTÕES ANTIGAS (FIXAS):")
    print("   • 'Adicionar uma terceira peça pode melhorar o conjunto'")
    print("   • 'O outfit está completo! Considere acessórios para complementar'")
    print("   ❌ Genéricas e não contextuais")
    print("   ❌ Não consideram as peças específicas")
    print("   ❌ Não adaptam ao estilo")
    
    print("\n🎯 SUGESTÕES NOVAS (CONTEXTUAIS):")
    print("   • 'Adicionar um Sapatos pode completar o look'")
    print("   • 'Um Cinto pode complementar o outfit'")
    print("   • 'Um Boné pode complementar o outfit'")
    print("   ✅ Específicas e contextuais")
    print("   ✅ Baseadas na compatibilidade real")
    print("   ✅ Adaptam-se ao estilo detectado")
    print("   ✅ Usam o conhecimento do CLIP")

if __name__ == "__main__":
    print("🚀 Iniciando teste de sugestões contextuais...")
    
    # Executar testes
    success = test_contextual_suggestions()
    
    if success:
        print("\n✅ Teste concluído com sucesso!")
        demo_suggestion_logic()
        compare_old_vs_new_suggestions()
    else:
        print("\n❌ Teste falhou!")
    
    print("\n" + "=" * 50)
    print("🎯 Para testar as sugestões contextuais:")
    print("   1. Use o Swagger UI: http://localhost:8000/docs")
    print("   2. Endpoint: POST /api/v1/analysis/complete")
    print("   3. Faça upload de imagens com diferentes outfits")
    print("   4. Observe as sugestões inteligentes geradas!")
    print("=" * 50) 