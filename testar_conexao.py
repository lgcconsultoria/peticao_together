#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar a conexão com a API do Together.
"""

import os
import logging
import requests
import json
from together import Together

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def testar_conexao():
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        print("Chave de API do Together não configurada!")
        return

    client = Together()  # Remova o argumento 'api_key' se não for necessário
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
            messages=[
                {"role": "system", "content": "You are a helpful chatbot."},
                {"role": "user", "content": "O que são reuniões de 'skip-level'?"},
            ],
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Erro ao conectar com a API: {e}")

def testar_conexao_chat():
    """Testa a conexão com a API do Together usando o endpoint de chat"""
    logger.info("Carregando variáveis de ambiente...")
    api_key = os.getenv("TOGETHER_API_KEY")
    
    if not api_key:
        logger.error("Chave de API do Together não encontrada nas variáveis de ambiente!")
        return
        
    logger.info("Iniciando teste de conexão para chat completion...")
    logger.info(f"Usando a chave de API: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        # URL da API do Together para chat completion
        url = "https://api.together.xyz/v1/chat/completions"
        
        # Cabeçalhos da requisição
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Corpo da requisição
        data = {
            "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "messages": [
                {"role": "system", "content": "Você é um assistente útil e amigável."},
                {"role": "user", "content": "Olá! Como você está?"}
            ],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        logger.info(f"Fazendo requisição para: {url}")
        logger.info(f"Modelo: {data['model']}")
        
        # Fazer a requisição
        response = requests.post(url, headers=headers, json=data)
        
        # Verificar o status da resposta
        logger.info(f"Status da resposta: {response.status_code}")
        
        if response.status_code == 200:
            # Converter a resposta para JSON
            result = response.json()
            
            # Extrair a resposta do modelo
            model_response = result['choices'][0]['message']['content']
            
            logger.info("Conexão bem sucedida!")
            logger.info(f"Resposta do modelo: {model_response}")
            
            # Salvar a resposta em um arquivo JSON
            with open("resposta_chat.json", "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info("Resposta completa salva em 'resposta_chat.json'")
        else:
            logger.error(f"Erro na requisição: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Erro ao testar conexão: {str(e)}")
    
    logger.info("Teste de chat completion concluído.")

if __name__ == "__main__":
    testar_conexao() 