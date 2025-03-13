#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar a geração de petições usando o AI Together.
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

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

def carregar_dados_teste(tipo_peticao):
    """Carrega dados de teste para o tipo de petição especificado"""
    dados_teste = {
        "recurso_administrativo": {
            "tipo": "recurso_administrativo",
            "fatos": """
            1. A empresa participou da licitação Pregão Eletrônico nº 001/2024.
            2. Foi desclassificada por supostamente não atender ao item 5.1 do edital.
            3. A decisão foi baseada em interpretação equivocada dos documentos apresentados.
            """,
            "argumentos": """
            1. A empresa atendeu plenamente aos requisitos do edital.
            2. A interpretação da comissão foi excessivamente restritiva.
            3. Há jurisprudência consolidada do TCU sobre o tema.
            """,
            "pedidos": """
            1. Reconsideração da decisão de desclassificação.
            2. Retorno à fase de habilitação.
            3. Prosseguimento no certame.
            """,
            "cliente_nome": "Empresa ABC Ltda.",
            "cliente_cnpj": "12.345.678/0001-90",
            "referencia_processo": "Pregão Eletrônico nº 001/2024",
            "autoridade": "Ilmo. Sr. Pregoeiro",
            "cidade": "São Paulo"
        },
        "impugnacao_edital": {
            "tipo": "impugnacao_edital",
            "fatos": """
            1. Foi publicado o Edital de Pregão Eletrônico nº 002/2024.
            2. O item 6.3 contém exigência restritiva à competição.
            3. O prazo de entrega é inexequível.
            """,
            "argumentos": """
            1. A exigência viola o princípio da competitividade.
            2. O prazo de entrega é incompatível com a realidade do mercado.
            3. Há precedentes do TCU contra exigências similares.
            """,
            "pedidos": """
            1. Alteração do item 6.3 do edital.
            2. Ampliação do prazo de entrega.
            3. Republicação do edital com as alterações.
            """,
            "cliente_nome": "Empresa XYZ S.A.",
            "cliente_cnpj": "98.765.432/0001-10",
            "referencia_processo": "Pregão Eletrônico nº 002/2024",
            "autoridade": "Ilmo. Sr. Pregoeiro",
            "cidade": "Rio de Janeiro"
        },
        "mandado_seguranca": {
            "tipo": "mandado_seguranca",
            "fatos": """
            1. A empresa foi impedida de participar de licitações.
            2. A decisão foi tomada sem processo administrativo prévio.
            3. Não houve oportunidade de defesa.
            """,
            "argumentos": """
            1. Violação ao devido processo legal.
            2. Ausência de contraditório e ampla defesa.
            3. Desproporcionalidade da medida.
            """,
            "pedidos": """
            1. Concessão de liminar.
            2. Suspensão dos efeitos da decisão.
            3. Anulação do ato administrativo.
            """,
            "cliente_nome": "Empresa DEF Ltda.",
            "cliente_cnpj": "11.222.333/0001-44",
            "referencia_processo": "Processo Administrativo nº 003/2024",
            "autoridade": "Exmo. Sr. Juiz Federal",
            "cidade": "Brasília"
        },
        "contrarrazoes_recurso": {
            "tipo": "contrarrazoes_recurso",
            "fatos": """
            1. A empresa foi vencedora do Pregão Eletrônico nº 004/2024.
            2. A segunda colocada interpôs recurso.
            3. As alegações são infundadas.
            """,
            "argumentos": """
            1. Todos os requisitos do edital foram atendidos.
            2. A documentação apresentada está completa.
            3. O recurso é meramente protelatório.
            """,
            "pedidos": """
            1. Manutenção da decisão que declarou a empresa vencedora.
            2. Indeferimento do recurso.
            3. Prosseguimento do certame.
            """,
            "cliente_nome": "Empresa GHI S.A.",
            "cliente_cnpj": "55.666.777/0001-88",
            "referencia_processo": "Pregão Eletrônico nº 004/2024",
            "autoridade": "Ilmo. Sr. Pregoeiro",
            "cidade": "Curitiba"
        }
    }
    
    return dados_teste.get(tipo_peticao)

def testar_geracao_peticao(tipo_peticao):
    """Testa a geração de uma petição"""
    logger.info(f"Testando geração de petição do tipo: {tipo_peticao}")
    
    # Carregar dados de teste
    dados_teste = carregar_dados_teste(tipo_peticao)
    if not dados_teste:
        logger.error(f"Tipo de petição não suportado: {tipo_peticao}")
        return
    
    # Inicializar componentes
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        logger.error("Chave de API do Together não configurada!")
        return
    
    try:
        logger.info("Gerando petição...")
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
        with open(f"resultados_teste/{tipo_peticao}_original_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(resultado["original"])
        
        # Salvar texto revisado
        with open(f"resultados_teste/{tipo_peticao}_revisado_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(resultado["reviewed"])
        
        # Salvar texto formatado
        with open(f"resultados_teste/{tipo_peticao}_formatado_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(resultado["formatted"])
        
        # Salvar texto final
        with open(f"resultados_teste/{tipo_peticao}_final_{timestamp}.txt", "w", encoding="utf-8") as f:
            f.write(resultado["final"])
        
        logger.info("Petição gerada com sucesso!")
        logger.info(f"Resultados salvos em: resultados_teste/{tipo_peticao}_*_{timestamp}.txt")
        
    except Exception as e:
        logger.error(f"Erro ao gerar petição: {str(e)}")

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("Uso: python testar_aitogether.py <tipo_peticao>")
        print("\nTipos de petição disponíveis:")
        print("  - recurso_administrativo")
        print("  - impugnacao_edital")
        print("  - mandado_seguranca")
        print("  - contrarrazoes_recurso")
        sys.exit(1)
    
    tipo_peticao = sys.argv[1]
    testar_geracao_peticao(tipo_peticao)

if __name__ == "__main__":
    main() 