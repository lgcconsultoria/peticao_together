#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar o sistema de log dos agentes e o novo agente revisor de gramática.
"""

import os
import sys
import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from utils.db_manager import DatabaseManager
from utils.aitogether_client import AITogetherClient
from utils.agents import AgentOrchestrator
from utils.grammar_revisor import GrammarRevisor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def main():
    """Função principal"""
    logger.info("Iniciando teste do sistema de log dos agentes e do revisor de gramática...")
    
    # Inicializar banco de dados
    db_manager = DatabaseManager()
    
    # Inicializar cliente AI Together
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        logger.error("Chave de API do Together não configurada!")
        sys.exit(1)
    
    client = AITogetherClient(api_key)
    
    # Criar orquestrador de agentes
    orchestrator = AgentOrchestrator(db_manager, client)
    
    # Definir contexto para geração de petição
    petition_type = "recurso_administrativo"  # Ou outro tipo disponível
    
    context = {
        "tipo": petition_type,
        "cliente_nome": "Empresa ABC Ltda.",
        "cliente_cnpj": "12.345.678/0001-90",
        "cliente_razao_social": "ABC Comércio e Serviços Ltda.",
        "referencia_processo": "Pregão Eletrônico nº 123/2023",
        "cidade": "São Paulo",
        "autoridade": "Pregoeiro da Prefeitura Municipal de São Paulo",
        "fatos": """
        Nossa empresa participou do Pregão Eletrônico nº 123/2023, realizado pela Prefeitura Municipal de São Paulo, 
        para fornecimento de equipamentos de informática. Fomos inabilitados na fase de qualificação técnica, 
        sob a alegação de que não apresentamos atestado de capacidade técnica compatível com o objeto licitado.
        
        Contudo, apresentamos sim o atestado emitido pela empresa XYZ S.A., que comprova que fornecemos equipamentos 
        similares em quantidade e especificações. O atestado foi ignorado pela comissão de licitação.
        
        Além disso, a empresa vencedora apresentou documentação com irregularidades, como certidão de regularidade 
        fiscal vencida, o que não foi observado pela comissão.
        
        O prazo para recurso é de 3 dias úteis, contados da publicação do resultado, que ocorreu ontem.
        """
    }
    
    # Gerar petição com log detalhado
    logger.info(f"Gerando petição do tipo: {petition_type}")
    try:
        results = orchestrator.generate_petition(context)
        
        # Salvar resultados em arquivos para análise
        output_dir = "resultados_teste"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        for key, text in results.items():
            filename = f"{output_dir}/{petition_type}_{key}_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
            logger.info(f"Texto '{key}' salvo em: {filename}")
        
        # Testar o revisor de gramática diretamente
        logger.info("Testando o revisor de gramática diretamente...")
        
        # Texto com erros gramaticais para teste
        texto_com_erros = """
        A empresa requereu a impugnação do edital, porem a comissão de licitação negou o pedido.
        O processo de Concórdia foi prejudicado devido a falta de transparencia.
        Nós pedimos que seja reconsiderado a decisão, por que ela não esta de acordo com a lei.
        """
        
        # Criar revisor de gramática
        grammar_revisor = GrammarRevisor()
        
        # Revisar texto
        try:
            texto_revisado = grammar_revisor.revisar_texto(texto_com_erros)
            
            # Salvar resultado
            filename = f"{output_dir}/teste_grammar_revisor_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("TEXTO ORIGINAL:\n\n")
                f.write(texto_com_erros)
                f.write("\n\nTEXTO REVISADO:\n\n")
                f.write(texto_revisado)
            
            logger.info(f"Resultado do teste do revisor de gramática salvo em: {filename}")
        except Exception as e:
            logger.error(f"Erro ao testar o revisor de gramática: {str(e)}")
        
        logger.info("Teste concluído com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante a geração da petição: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 