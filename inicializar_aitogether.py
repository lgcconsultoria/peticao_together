#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para inicializar o banco de dados e configurar os agentes do AI Together.
"""

import os
import sys
import logging
import json
from dotenv import load_dotenv
from utils.db_manager import DatabaseManager
from utils.aitogether_client import AITogetherClient
from utils.agents import GeneratorAgent, ReviewerAgent

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def inicializar_banco_dados():
    """Inicializa o banco de dados"""
    logger.info("Inicializando banco de dados...")
    db_manager = DatabaseManager()
    logger.info("Banco de dados inicializado com sucesso!")
    return db_manager

def testar_conexao_aitogether():
    """Testa a conexão com a API do Together"""
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        logger.error("Chave de API do Together não configurada!")
        return False
    
    logger.info("Testando conexão com a API do Together...")
    client = AITogetherClient(api_key)
    
    try:
        models = client.list_models()
        logger.info(f"Conexão bem-sucedida! {len(models)} modelos disponíveis.")
        return True
    except Exception as e:
        logger.error(f"Erro ao conectar com a API do Together: {str(e)}")
        return False

def configurar_agentes_padrao(db_manager):
    """Configura os agentes padrão no banco de dados"""
    logger.info("Configurando agentes padrão...")
    
    # Verificar se já existem agentes configurados
    generator_models = db_manager.get_agent_models(agent_type="generator")
    reviewer_models = db_manager.get_agent_models(agent_type="reviewer")
    
    if generator_models and reviewer_models:
        logger.info("Agentes já configurados. Pulando configuração.")
        return
    
    # Modelo padrão para todos os agentes
    default_model = "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        logger.error("Chave de API do Together não configurada!")
        return
    client = AITogetherClient(api_key)
    
    # Configurar agentes geradores
    if not generator_models:
        logger.info("Configurando agentes geradores...")
        petition_types = ["recurso_administrativo", "impugnacao_edital", "mandado_seguranca", "contrarrazoes_recurso"]
        
        for petition_type in petition_types:
            # Criar um agente gerador temporário para obter o template
            temp_agent = GeneratorAgent(client, default_model, petition_type)
            
            # Adicionar o agente ao banco de dados
            db_manager.add_agent_model(
                name=f"Gerador de {petition_type.replace('_', ' ').title()}",
                description=f"Agente especializado em gerar petições do tipo {petition_type.replace('_', ' ').title()}",
                model_id=default_model,
                agent_type="generator",
                specialty=petition_type,
                prompt_template=temp_agent.prompt_template
            )
            logger.info(f"Agente gerador para {petition_type} configurado com sucesso!")
    
    # Configurar agentes revisores
    if not reviewer_models:
        logger.info("Configurando agentes revisores...")
        review_types = ["juridico", "formatacao", "linguagem", "gramatica"]
        
        for review_type in review_types:
            # Criar um agente revisor temporário para obter o template
            temp_agent = ReviewerAgent(client, default_model, review_type)
            
            # Adicionar o agente ao banco de dados
            db_manager.add_agent_model(
                name=f"Revisor {review_type.title()}",
                description=f"Agente especializado em revisão {review_type} de petições",
                model_id=default_model,
                agent_type="reviewer",
                specialty=review_type,
                prompt_template=temp_agent.prompt_template
            )
            logger.info(f"Agente revisor para {review_type} configurado com sucesso!")
    
    logger.info("Configuração de agentes concluída com sucesso!")

def listar_agentes(db_manager):
    """Lista os agentes configurados"""
    logger.info("Agentes configurados:")
    
    # Listar agentes geradores
    generator_models = db_manager.get_agent_models(agent_type="generator")
    logger.info(f"\nAgentes Geradores ({len(generator_models)}):")
    for model in generator_models:
        logger.info(f"  - {model['name']} (ID: {model['id']}, Modelo: {model['model_id']}, Especialidade: {model['specialty']})")
    
    # Listar agentes revisores
    reviewer_models = db_manager.get_agent_models(agent_type="reviewer")
    logger.info(f"\nAgentes Revisores ({len(reviewer_models)}):")
    for model in reviewer_models:
        logger.info(f"  - {model['name']} (ID: {model['id']}, Modelo: {model['model_id']}, Especialidade: {model['specialty']})")

def main():
    """Função principal"""
    logger.info("Iniciando configuração do sistema de petições com Together...")
    
    # Testar conexão com a API do Together
    if not testar_conexao_aitogether():
        logger.error("Não foi possível conectar com a API do Together. Verifique sua chave de API.")
        sys.exit(1)
    
    # Inicializar banco de dados
    db_manager = inicializar_banco_dados()
    
    # Configurar agentes padrão
    configurar_agentes_padrao(db_manager)
    
    # Listar agentes configurados
    listar_agentes(db_manager)
    
    logger.info("Configuração concluída com sucesso!")

if __name__ == "__main__":
    main() 