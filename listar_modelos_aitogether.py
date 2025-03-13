#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para listar os modelos disponíveis na API do AI Together.
"""

import os
import sys
import logging
import json
from dotenv import load_dotenv
from utils.aitogether_client import AITogetherClient
from tabulate import tabulate

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def listar_modelos():
    """Lista os modelos disponíveis na API do AI Together"""
    api_key = os.getenv("AITOGETHER_API_KEY")
    if not api_key:
        logger.error("Chave de API do AI Together não configurada!")
        return
    
    logger.info("Conectando à API do AI Together...")
    client = AITogetherClient(api_key)
    
    try:
        models = client.list_models()
        
        # Filtrar e organizar os modelos
        modelos_filtrados = []
        for model in models:
            # Extrair informações relevantes
            model_id = model.get("id", "")
            context_length = model.get("context_length", 0)
            pricing = model.get("pricing", {})
            input_price = pricing.get("input", 0)
            output_price = pricing.get("output", 0)
            
            # Adicionar à lista filtrada
            modelos_filtrados.append([
                model_id,
                context_length,
                f"${input_price}/1M tokens",
                f"${output_price}/1M tokens"
            ])
        
        # Ordenar por ID do modelo
        modelos_filtrados.sort(key=lambda x: x[0])
        
        # Exibir tabela
        headers = ["Modelo", "Contexto (tokens)", "Preço de Entrada", "Preço de Saída"]
        print("\nModelos disponíveis no AI Together:\n")
        print(tabulate(modelos_filtrados, headers=headers, tablefmt="grid"))
        print(f"\nTotal de modelos: {len(modelos_filtrados)}")
        
        # Salvar em arquivo JSON
        with open("modelos_aitogether.json", "w", encoding="utf-8") as f:
            json.dump(models, f, indent=2)
        
        logger.info(f"Lista completa de modelos salva em 'modelos_aitogether.json'")
        
    except Exception as e:
        logger.error(f"Erro ao listar modelos: {str(e)}")

def main():
    """Função principal"""
    listar_modelos()

if __name__ == "__main__":
    main() 