#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar o endpoint /api/v1/analysis/complete e identificar problemas
"""

import requests
import json
import os
from PIL import Image
import io

def test_analysis_endpoint():
    """Testa o endpoint de análise completa"""
    
    # URL da API
    url = "http://localhost:8000/api/v1/analysis/complete"
    
    print("Testando endpoint /api/v1/analysis/complete...")
    
    # Verificar se há imagens de teste
    test_images_dir = "test_images"
    if not os.path.exists(test_images_dir):
        print(f"Diretorio {test_images_dir} nao encontrado")
        return
    
    # Listar imagens de teste
    image_files = [f for f in os.listdir(test_images_dir) 
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    
    if not image_files:
        print(f"Nenhuma imagem encontrada em {test_images_dir}")
        return
    
    print(f"Encontradas {len(image_files)} imagens de teste")
    
    # Testar com a primeira imagem
    test_image = os.path.join(test_images_dir, image_files[0])
    print(f"Testando com: {test_image}")
    
    try:
        # Abrir e verificar a imagem
        with Image.open(test_image) as img:
            print(f"   Dimensoes: {img.size}")
            print(f"   Modo: {img.mode}")
            print(f"   Formato: {img.format}")
        
        # Preparar arquivo para upload
        with open(test_image, 'rb') as f:
            files = {'file': (os.path.basename(test_image), f, 'image/jpeg')}
            
            print("Enviando requisicao...")
            print(f"   URL: {url}")
            print(f"   Arquivo: {os.path.basename(test_image)}")
            
            # Fazer a requisição
            response = requests.post(url, files=files, timeout=60)
            
            print(f"Resposta recebida:")
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print("Sucesso!")
                print(f"   Session ID: {result.get('session_id')}")
                print(f"   Partes salvas: {result.get('total_parts_saved')}")
                print(f"   Partes detectadas: {list(result.get('body_parts', {}).keys())}")
            else:
                print("Erro na requisicao")
                try:
                    error_detail = response.json()
                    print(f"   Erro: {json.dumps(error_detail, indent=2)}")
                except:
                    print(f"   Resposta: {response.text}")
                    
    except requests.exceptions.ConnectionError:
        print("Erro: Nao foi possivel conectar a API. Verifique se ela esta rodando.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
        import traceback
        traceback.print_exc()

def test_invalid_requests():
    """Testa requisições inválidas para identificar problemas"""
    
    url = "http://localhost:8000/api/v1/analysis/complete"
    
    print("\nTestando requisicoes invalidas...")
    
    # Teste 1: Sem arquivo
    print("\n1. Testando sem arquivo...")
    try:
        response = requests.post(url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Teste 2: Arquivo vazio
    print("\n2. Testando arquivo vazio...")
    try:
        files = {'file': ('empty.txt', io.BytesIO(b''), 'text/plain')}
        response = requests.post(url, files=files, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Teste 3: Arquivo de texto
    print("\n3. Testando arquivo de texto...")
    try:
        files = {'file': ('test.txt', io.BytesIO(b'Hello World'), 'text/plain')}
        response = requests.post(url, files=files, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    except Exception as e:
        print(f"   Erro: {e}")

if __name__ == "__main__":
    test_analysis_endpoint()
    test_invalid_requests() 