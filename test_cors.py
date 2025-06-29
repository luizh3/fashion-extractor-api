#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar a configuração de CORS da API
"""

import requests
import json

def test_cors():
    """Testa se o CORS está configurado corretamente"""
    
    # URL da API
    base_url = "http://localhost:8000"
    
    # Headers para simular uma requisição de origem diferente
    headers = {
        "Origin": "http://example.com",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    print("🧪 Testando configuração de CORS...")
    
    try:
        # Teste 1: Requisição simples
        print("\n1. Testando requisição GET simples...")
        response = requests.get(f"{base_url}/health", headers=headers)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Verificar headers de CORS na resposta
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        print(f"   CORS Headers: {json.dumps(cors_headers, indent=2)}")
        
        # Teste 2: OPTIONS request (preflight)
        print("\n2. Testando requisição OPTIONS (preflight)...")
        options_response = requests.options(f"{base_url}/health", headers=headers)
        
        print(f"   Status Code: {options_response.status_code}")
        
        options_cors_headers = {
            "Access-Control-Allow-Origin": options_response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": options_response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": options_response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": options_response.headers.get("Access-Control-Allow-Credentials")
        }
        
        print(f"   CORS Headers: {json.dumps(options_cors_headers, indent=2)}")
        
        # Verificar se CORS está funcionando
        if cors_headers["Access-Control-Allow-Origin"] == "*":
            print("\n✅ CORS configurado corretamente! Qualquer origem é permitida.")
        else:
            print("\n❌ CORS não está configurado corretamente.")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar à API. Verifique se ela está rodando.")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    test_cors() 