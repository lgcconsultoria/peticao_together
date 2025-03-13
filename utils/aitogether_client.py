#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cliente para a API do Together.
"""

import os
import json
import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AITogetherClient:
    """Cliente para interagir com a API do Together"""
    
    def __init__(self, api_key: str):
        """Inicializa o cliente
        
        Args:
            api_key: Chave de API do Together
        """
        self.api_key = api_key
        self.base_url = "https://api.together.xyz/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """Lista os modelos disponíveis na API
        
        Returns:
            Lista de modelos disponíveis
        """
        try:
            url = f"{self.base_url}/models"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Erro ao listar modelos: {response.status_code} - {response.text}")
                raise Exception(f"Erro ao listar modelos: {response.status_code}")
                
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao listar modelos: {str(e)}")
            raise
    
    def generate_text(self, model: str, prompt: str, max_tokens: int = 2000,
                     temperature: float = 0.7, top_p: float = 0.7,
                     top_k: int = 50, repetition_penalty: float = 1.0) -> Dict[str, Any]:
        """Gera texto usando um modelo específico
        
        Args:
            model: ID do modelo a ser usado
            prompt: Texto de entrada para o modelo
            max_tokens: Número máximo de tokens a serem gerados
            temperature: Temperatura para amostragem (0.0 a 1.0)
            top_p: Probabilidade acumulada para amostragem núcleo
            top_k: Número de tokens mais prováveis a considerar
            repetition_penalty: Penalidade para repetição de tokens
            
        Returns:
            Resposta da API com o texto gerado
        """
        try:
            url = f"{self.base_url}/chat/completions"
            
            data = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "repetition_penalty": repetition_penalty
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code != 200:
                logger.error(f"Erro ao gerar texto: {response.status_code} - {response.text}")
                raise Exception(f"Erro ao gerar texto: {response.status_code}")
                
            result = response.json()
            
            return {
                "choices": [{
                    "text": result["choices"][0]["message"]["content"]
                }]
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar texto: {str(e)}")
            raise
    
    def test_connection(self) -> bool:
        """Testa a conexão com a API
        
        Returns:
            True se a conexão foi bem-sucedida, False caso contrário
        """
        try:
            models = self.list_models()
            logger.info(f"Conexão bem-sucedida! {len(models)} modelos disponíveis.")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao testar conexão: {str(e)}")
            return False

    def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """Obtém detalhes de um modelo específico
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Detalhes do modelo
            
        Raises:
            Exception: Se ocorrer um erro na API
        """
        if not self.api_key:
            raise ValueError("Chave de API do Together não configurada")
        
        try:
            url = f"{self.base_url}/models/{model_id}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Erro ao obter detalhes do modelo: {response.status_code} - {response.text}")
                raise Exception(f"Erro ao obter detalhes do modelo: {response.status_code}")
                
            return response.json()
            
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do modelo {model_id}: {str(e)}")
            raise
    
    def chat_completion(self, 
                       model: str, 
                       messages: List[Dict[str, str]], 
                       max_tokens: int = 1000, 
                       temperature: float = 0.7,
                       top_p: float = 0.9,
                       top_k: int = 50,
                       repetition_penalty: float = 1.1) -> Dict[str, Any]:
        """Gera uma resposta de chat usando o modelo especificado
        
        Args:
            model: ID do modelo no Together
            messages: Lista de mensagens no formato de chat
            max_tokens: Número máximo de tokens a serem gerados
            temperature: Temperatura para amostragem
            top_p: Probabilidade acumulada para amostragem de núcleo
            top_k: Número de tokens mais prováveis a considerar
            repetition_penalty: Penalidade para repetição de tokens
            
        Returns:
            Resposta da API
            
        Raises:
            Exception: Se ocorrer um erro na API
        """
        if not self.api_key:
            raise ValueError("Chave de API do Together não configurada")
        
        try:
            url = f"{self.base_url}/chat/completions"
            
            data = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
                "repetition_penalty": repetition_penalty
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code != 200:
                logger.error(f"Erro na API de chat do Together: {response.status_code} - {response.text}")
                raise Exception(f"Erro na API de chat do Together: {response.status_code}")
                
            result = response.json()
            
            return {
                "choices": [{
                    "message": {
                        "content": result["choices"][0]["message"]["content"]
                    }
                }]
            }
            
        except Exception as e:
            logger.error(f"Erro na API de chat do Together: {str(e)}")
            raise 