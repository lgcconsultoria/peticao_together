#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar a geração de um recurso administrativo contra inabilitação em licitação.
"""

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from utils.db_manager import DatabaseManager
from utils.aitogether_client import AITogetherClient
from utils.agents import AgentOrchestrator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def testar_recurso_inabilitacao():
    """Testa a geração de um recurso administrativo contra inabilitação"""
    
    # Dados do caso de teste
    dados_teste = {
        "tipo": "recurso_administrativo",
        "fatos": """
        Nossa empresa, Construtora Horizonte Ltda., participou da Concorrência Pública nº 023/2024, 
        promovida pela Prefeitura Municipal de Belo Horizonte para contratação de empresa especializada 
        para construção de uma escola municipal.
        
        Na sessão de abertura dos envelopes de habilitação, realizada em 10/03/2024, a Comissão 
        Permanente de Licitação nos inabilitou sob a alegação de que não atendemos ao item 8.4.3 
        do edital, que exige comprovação de capacidade técnico-operacional através de atestados 
        que demonstrem a execução de obras similares.
        
        Apresentamos três atestados de capacidade técnica emitidos por órgãos públicos, que comprovam 
        a execução de obras de construção de prédios públicos, incluindo uma escola estadual com 
        características semelhantes à do objeto licitado.
        
        A Comissão entendeu que os atestados não seriam suficientes porque um deles se refere a uma 
        obra realizada há mais de 10 anos e os outros dois não contemplariam todos os itens de maior 
        relevância exigidos no edital, especificamente a execução de sistema de captação de energia solar.
        
        A decisão de inabilitação foi publicada no Diário Oficial do Município em 11/03/2024, abrindo 
        prazo recursal de 5 dias úteis.
        """,
        "cliente_nome": "Construtora Horizonte Ltda.",
        "cliente_cnpj": "12.345.678/0001-90",
        "referencia_processo": "Concorrência Pública nº 023/2024",
        "autoridade": "Ilmo. Sr. Presidente da Comissão Permanente de Licitação",
        "cidade": "Belo Horizonte"
    }
    
    # Inicializar componentes
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        logger.error("Chave de API do Together não configurada!")
        return
    
    try:
        logger.info("Gerando recurso administrativo contra inabilitação...")
        db_manager = DatabaseManager()
        ai_client = AITogetherClient(api_key)
        orchestrator = AgentOrchestrator(db_manager, ai_client)
        
        # Gerar petição
        resultado = orchestrator.generate_petition(dados_teste)
        
        # Criar diretório para resultados
        os.makedirs("resultados_teste", exist_ok=True)
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Salvar texto original
        with open(f"resultados_teste/recurso_inabilitacao_original_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(resultado["original"])
        
        # Salvar texto revisado
        with open(f"resultados_teste/recurso_inabilitacao_revisado_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(resultado["reviewed"])
        
        # Salvar texto formatado
        with open(f"resultados_teste/recurso_inabilitacao_formatado_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(resultado["formatted"])
        
        # Salvar texto final
        with open(f"resultados_teste/recurso_inabilitacao_final_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(resultado["final"])
        
        logger.info("Recurso administrativo gerado com sucesso!")
        logger.info(f"Resultados salvos em: resultados_teste/recurso_inabilitacao_*_{timestamp}.txt")
        
    except Exception as e:
        logger.error(f"Erro ao gerar recurso administrativo: {str(e)}")

if __name__ == "__main__":
    testar_recurso_inabilitacao() 