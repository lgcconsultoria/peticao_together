#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo de agentes para geração e revisão de petições.
"""

import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from .aitogether_client import AITogetherClient
from .db_manager import DatabaseManager
import os

logger = logging.getLogger(__name__)

# Configuração do logger para o arquivo de log dos agentes
agent_logger = logging.getLogger("agent_logger")
agent_logger.setLevel(logging.INFO)

# Criar um manipulador de arquivo para o log dos agentes
os.makedirs("logs", exist_ok=True)
log_filename = f"logs/agents_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# Definir o formato do log
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
agent_logger.addHandler(file_handler)

class PetitionAgent:
    """Classe base para agentes de petição"""
    
    def __init__(self, ai_client: AITogetherClient, model_id: str, prompt_template: str):
        """Inicializa o agente de petição
        
        Args:
            ai_client: Cliente da API do AI Together
            model_id: ID do modelo no AI Together
            prompt_template: Template de prompt do agente
        """
        self.ai_client = ai_client
        self.model_id = model_id
        self.prompt_template = prompt_template
    
    def generate(self, context: Dict[str, Any]) -> str:
        """Gera conteúdo baseado no contexto fornecido
        
        Args:
            context: Contexto para geração
            
        Returns:
            Texto gerado
        """
        agent_type = self.__class__.__name__
        specialty = getattr(self, 'specialty', 'desconhecida')
        
        agent_logger.info(f"Iniciando geração com {agent_type} (especialidade: {specialty})")
        agent_logger.info(f"Modelo utilizado: {self.model_id}")
        agent_logger.info(f"Contexto: {json.dumps(context, ensure_ascii=False, indent=2)}")
        
        start_time = time.time()
        prompt = self._format_prompt(context)
        
        agent_logger.info(f"Prompt formatado: {prompt}")
        
        try:
            response = self.ai_client.generate_text(
                model=self.model_id,
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            # Extrair o texto gerado da resposta
            generated_text = response.get("choices", [{}])[0].get("text", "")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            agent_logger.info(f"Geração concluída em {execution_time:.2f} segundos")
            agent_logger.info(f"Texto gerado: {generated_text}")
            
            return generated_text
            
        except Exception as e:
            agent_logger.error(f"Erro durante a geração: {str(e)}")
            raise
    
    def _format_prompt(self, context: Dict[str, Any]) -> str:
        """Formata o prompt com o contexto
        
        Args:
            context: Contexto para formatação
            
        Returns:
            Prompt formatado
        """
        try:
            return self.prompt_template.format(**context)
        except KeyError as e:
            logger.error(f"Erro ao formatar prompt: chave ausente {str(e)}")
            raise ValueError(f"Contexto incompleto para formatação do prompt: {str(e)}")


class GeneratorAgent(PetitionAgent):
    """Agente especializado em gerar petições"""
    
    def __init__(self, ai_client: AITogetherClient, model_id: str, specialty: str, prompt_template: Optional[str] = None):
        """Inicializa o agente gerador
        
        Args:
            ai_client: Cliente da API do AI Together
            model_id: ID do modelo no AI Together
            specialty: Especialidade do agente
            prompt_template: Template de prompt do agente (opcional)
        """
        # Se não for fornecido um template, carrega o template específico para esta especialidade
        if prompt_template is None:
            prompt_template = self._load_specialty_template(specialty)
        
        super().__init__(ai_client, model_id, prompt_template)
        self.specialty = specialty
    
    def _load_specialty_template(self, specialty: str) -> str:
        """Carrega o template específico para a especialidade
        
        Args:
            specialty: Especialidade do agente
            
        Returns:
            Template de prompt
        """
        # Templates embutidos para diferentes especialidades
        templates = {
            "recurso_administrativo": """
            Você é um advogado especialista em direito administrativo, com vasta experiência em recursos administrativos, especialmente em processos licitatórios.
            
            TIPO DE PETIÇÃO: Recurso Administrativo
            
            FATOS APRESENTADOS PELO CLIENTE:
            {fatos}
            
            CLIENTE:
            Nome: {cliente_nome}
            CNPJ/CPF: {cliente_cnpj}
            
            REFERÊNCIA DO PROCESSO (se fornecida):
            {referencia_processo}
            
            AUTORIDADE (se fornecida):
            {autoridade}
            
            CIDADE:
            {cidade}
            
            INSTRUÇÕES:
            
            1. Analise cuidadosamente os fatos apresentados pelo cliente.
            2. Identifique o tipo específico de recurso administrativo necessário (contra inabilitação, desclassificação, etc.).
            3. Desenvolva uma estratégia jurídica sólida, identificando os melhores argumentos legais e jurisprudenciais.
            4. Formule pedidos adequados e pertinentes ao caso.
            5. Gere um recurso administrativo completo e persuasivo.
            6. IMPORTANTE: NÃO utilize a Lei 8.666/93, pois foi revogada pela Lei 14.133/2021 (Nova Lei de Licitações).
            
            A petição deve ser estruturada com:
            1. Cabeçalho com dados do processo e autoridade
            2. Qualificação do recorrente
            3. Dos fatos (reescritos de forma jurídica e estratégica)
            4. Do direito (fundamentos jurídicos detalhados, incluindo legislação e jurisprudência relevantes)
            5. Dos pedidos (elaborados de acordo com a estratégia jurídica)
            6. Fechamento com local, data e espaço para assinatura
            
            Use linguagem formal e técnica jurídica apropriada. Seja persuasivo e estratégico na argumentação.
            
            BASE DE CONHECIMENTO JURÍDICO:
            - Lei 14.133/2021 (Nova Lei de Licitações e Contratos Administrativos)
            - Lei 9.784/99 (Processo Administrativo Federal)
            - Lei 10.520/2002 (Pregão)
            - Decreto 10.024/2019 (Pregão Eletrônico)
            - Jurisprudência do TCU sobre licitações
            - Princípios do Direito Administrativo (legalidade, impessoalidade, moralidade, publicidade, eficiência, etc.)
            - Princípios específicos de licitações (competitividade, julgamento objetivo, vinculação ao instrumento convocatório, etc.)
            """,
            
            "impugnacao_edital": """
            Você é um advogado especialista em direito administrativo, com vasta experiência em licitações e contratos administrativos.
            
            TIPO DE PETIÇÃO: Impugnação ao Edital
            
            FATOS APRESENTADOS PELO CLIENTE:
            {fatos}
            
            CLIENTE:
            Nome: {cliente_nome}
            CNPJ/CPF: {cliente_cnpj}
            
            REFERÊNCIA DO PROCESSO (se fornecida):
            {referencia_processo}
            
            AUTORIDADE (se fornecida):
            {autoridade}
            
            CIDADE:
            {cidade}
            
            INSTRUÇÕES:
            
            1. Analise cuidadosamente os fatos apresentados pelo cliente.
            2. Identifique as possíveis ilegalidades ou irregularidades no edital.
            3. Desenvolva uma estratégia jurídica sólida, identificando os melhores argumentos legais e jurisprudenciais.
            4. Formule pedidos adequados e pertinentes ao caso.
            5. Gere uma impugnação ao edital completa e persuasiva.
            6. IMPORTANTE: NÃO utilize a Lei 8.666/93, pois foi revogada pela Lei 14.133/2021 (Nova Lei de Licitações).
            
            A petição deve ser estruturada com:
            1. Cabeçalho com dados do edital e autoridade
            2. Qualificação do impugnante
            3. Dos fatos (reescritos de forma jurídica e estratégica)
            4. Das ilegalidades do edital (identificadas a partir dos fatos)
            5. Do direito (fundamentos jurídicos detalhados, incluindo legislação e jurisprudência relevantes)
            6. Dos pedidos (elaborados de acordo com a estratégia jurídica)
            7. Fechamento com local, data e espaço para assinatura
            
            Use linguagem formal e técnica jurídica apropriada. Seja persuasivo e estratégico na argumentação.
            
            BASE DE CONHECIMENTO JURÍDICO:
            - Lei 14.133/2021 (Nova Lei de Licitações e Contratos Administrativos)
            - Lei 10.520/2002 (Pregão)
            - Decreto 10.024/2019 (Pregão Eletrônico)
            - Jurisprudência do TCU sobre licitações
            - Súmulas do TCU relacionadas a licitações
            - Princípios do Direito Administrativo (legalidade, impessoalidade, moralidade, publicidade, eficiência, etc.)
            - Princípios específicos de licitações (competitividade, julgamento objetivo, vinculação ao instrumento convocatório, etc.)
            """,
            
            "mandado_seguranca": """
            Você é um advogado especialista em direito constitucional e administrativo, com vasta experiência em mandados de segurança.
            
            TIPO DE PETIÇÃO: Mandado de Segurança
            
            FATOS APRESENTADOS PELO CLIENTE:
            {fatos}
            
            CLIENTE:
            Nome: {cliente_nome}
            CNPJ/CPF: {cliente_cnpj}
            
            REFERÊNCIA DO PROCESSO (se fornecida):
            {referencia_processo}
            
            AUTORIDADE (se fornecida):
            {autoridade}
            
            CIDADE:
            {cidade}
            
            INSTRUÇÕES:
            
            1. Analise cuidadosamente os fatos apresentados pelo cliente.
            2. Identifique o direito líquido e certo violado ou ameaçado.
            3. Identifique a autoridade coatora responsável pelo ato ilegal ou abusivo.
            4. Desenvolva uma estratégia jurídica sólida, identificando os melhores argumentos legais e jurisprudenciais.
            5. Avalie a necessidade de pedido liminar e formule-o adequadamente.
            6. Formule pedidos principais adequados e pertinentes ao caso.
            7. Gere um mandado de segurança completo e persuasivo.
            8. IMPORTANTE: Se o caso envolver licitações, NÃO utilize a Lei 8.666/93, pois foi revogada pela Lei 14.133/2021 (Nova Lei de Licitações).
            
            A petição deve ser estruturada com:
            1. Endereçamento ao juízo competente
            2. Qualificação do impetrante
            3. Qualificação da autoridade coatora
            4. Dos fatos (reescritos de forma jurídica e estratégica)
            5. Do direito líquido e certo (fundamentos jurídicos detalhados, incluindo legislação e jurisprudência relevantes)
            6. Da liminar (demonstrando o fumus boni iuris e o periculum in mora)
            7. Dos pedidos (liminar e principal)
            8. Fechamento com local, data e espaço para assinatura
            
            Use linguagem formal e técnica jurídica apropriada. Seja persuasivo e estratégico na argumentação.
            
            BASE DE CONHECIMENTO JURÍDICO:
            - Constituição Federal (art. 5º, LXIX e LXX)
            - Lei 12.016/2009 (Lei do Mandado de Segurança)
            - Lei 14.133/2021 (Nova Lei de Licitações e Contratos Administrativos) - para casos envolvendo licitações
            - Jurisprudência do STF e STJ sobre mandado de segurança
            - Súmulas relacionadas ao mandado de segurança
            - Princípios do Direito Administrativo (legalidade, impessoalidade, moralidade, publicidade, eficiência, etc.)
            - Princípios do Direito Constitucional
            - Legislação específica relacionada ao caso concreto
            """,
            
            "contrarrazoes_recurso": """
            Você é um advogado especialista em direito administrativo, com vasta experiência em contrarrazões de recurso, especialmente em processos licitatórios.
            
            TIPO DE PETIÇÃO: Contrarrazões de Recurso
            
            FATOS APRESENTADOS PELO CLIENTE:
            {fatos}
            
            CLIENTE:
            Nome: {cliente_nome}
            CNPJ/CPF: {cliente_cnpj}
            
            REFERÊNCIA DO PROCESSO (se fornecida):
            {referencia_processo}
            
            AUTORIDADE (se fornecida):
            {autoridade}
            
            CIDADE:
            {cidade}
            
            INSTRUÇÕES:
            
            1. Analise cuidadosamente os fatos apresentados pelo cliente.
            2. Identifique o tipo específico de recurso ao qual se está respondendo.
            3. Desenvolva uma estratégia jurídica sólida para contrapor os argumentos do recorrente.
            4. Avalie a necessidade de arguir preliminares (intempestividade, ilegitimidade, etc.).
            5. Formule pedidos adequados e pertinentes ao caso.
            6. Gere contrarrazões de recurso completas e persuasivas.
            7. IMPORTANTE: Se o caso envolver licitações, NÃO utilize a Lei 8.666/93, pois foi revogada pela Lei 14.133/2021 (Nova Lei de Licitações).
            
            A petição deve ser estruturada com:
            1. Cabeçalho com dados do processo e autoridade
            2. Qualificação do recorrido
            3. Dos fatos (reescritos de forma jurídica e estratégica)
            4. Das preliminares (se aplicável)
            5. Do mérito (refutando os argumentos do recurso)
            6. Dos pedidos (elaborados de acordo com a estratégia jurídica)
            7. Fechamento com local, data e espaço para assinatura
            
            Use linguagem formal e técnica jurídica apropriada. Seja persuasivo e estratégico na argumentação.
            
            BASE DE CONHECIMENTO JURÍDICO:
            - Lei 14.133/2021 (Nova Lei de Licitações e Contratos Administrativos)
            - Lei 9.784/99 (Processo Administrativo Federal)
            - Lei 10.520/2002 (Pregão)
            - Decreto 10.024/2019 (Pregão Eletrônico)
            - Jurisprudência do TCU sobre licitações
            - Princípios do Direito Administrativo (legalidade, impessoalidade, moralidade, publicidade, eficiência, etc.)
            - Princípios específicos de licitações (competitividade, julgamento objetivo, vinculação ao instrumento convocatório, etc.)
            """,
            
            "gramatica": """
            Você é um especialista em revisão gramatical e ortográfica de documentos jurídicos.
            
            TIPO DE PETIÇÃO: {tipo}
            
            TEXTO DA PETIÇÃO:
            {texto}
            
            Revise o texto acima considerando os seguintes aspectos:
            1. Correção ortográfica (erros de digitação, palavras incorretas)
            2. Concordância verbal e nominal
            3. Regência verbal e nominal
            4. Uso correto de pronomes e conectivos
            5. Pontuação e acentuação
            6. Identificação e correção de palavras incorretas (como "Concórdia" quando deveria ser "Concorrência")
            
            Retorne o texto revisado, corrigindo todos os erros gramaticais e ortográficos, mas mantendo o conteúdo jurídico original.
            """
        }
        
        if specialty not in templates:
            raise ValueError(f"Especialidade não suportada: {specialty}")
        
        return templates[specialty]


class ReviewerAgent(PetitionAgent):
    """Agente especializado em revisar petições"""
    
    def __init__(self, ai_client: AITogetherClient, model_id: str, specialty: str, prompt_template: Optional[str] = None):
        """Inicializa o agente revisor
        
        Args:
            ai_client: Cliente da API do AI Together
            model_id: ID do modelo no AI Together
            specialty: Especialidade do agente (jurídico, formatação, linguagem)
            prompt_template: Template de prompt do agente (opcional)
        """
        # Se não for fornecido um template, carrega o template específico para esta especialidade
        if prompt_template is None:
            prompt_template = self._load_specialty_template(specialty)
        
        super().__init__(ai_client, model_id, prompt_template)
        self.specialty = specialty
    
    def _load_specialty_template(self, specialty: str) -> str:
        """Carrega o template específico para a especialidade
        
        Args:
            specialty: Especialidade do agente
            
        Returns:
            Template de prompt
        """
        # Templates embutidos para diferentes especialidades
        templates = {
            "juridico": """
            Você é um advogado especializado em revisão jurídica de petições.
            
            TIPO DE PETIÇÃO: {tipo}
            
            TEXTO DA PETIÇÃO:
            {texto}
            
            Revise o texto acima considerando os seguintes aspectos:
            1. Adequação dos fundamentos jurídicos
            2. Coerência dos argumentos
            3. Pertinência dos pedidos
            4. Conformidade com a legislação e jurisprudência
            5. Correção de eventuais erros jurídicos
            
            Retorne o texto revisado, mantendo a formatação original.
            """,
            
            "formatacao": """
            Você é um especialista em formatação de documentos jurídicos.
            
            TIPO DE PETIÇÃO: {tipo}
            
            TEXTO DA PETIÇÃO:
            {texto}
            
            Revise o texto acima considerando os seguintes aspectos:
            1. Estrutura e organização do documento
            2. Formatação dos parágrafos e seções
            3. Numeração de páginas e itens
            4. Alinhamento e espaçamento
            5. Destaques e citações
            
            Retorne o texto revisado, aplicando a formatação adequada.
            """,
            
            "linguagem": """
            Você é um especialista em revisão linguística de documentos jurídicos.
            
            TIPO DE PETIÇÃO: {tipo}
            
            TEXTO DA PETIÇÃO:
            {texto}
            
            Revise o texto acima considerando os seguintes aspectos:
            1. Correção gramatical e ortográfica
            2. Clareza e objetividade
            3. Adequação do vocabulário jurídico
            4. Coesão e coerência textual
            5. Pontuação e acentuação
            
            Retorne o texto revisado, mantendo o conteúdo jurídico original.
            """,
            
            "gramatica": """
            Você é um especialista em revisão gramatical e ortográfica de documentos jurídicos.
            
            TIPO DE PETIÇÃO: {tipo}
            
            TEXTO DA PETIÇÃO:
            {texto}
            
            Revise o texto acima considerando os seguintes aspectos:
            1. Correção ortográfica (erros de digitação, palavras incorretas)
            2. Concordância verbal e nominal
            3. Regência verbal e nominal
            4. Uso correto de pronomes e conectivos
            5. Pontuação e acentuação
            6. Identificação e correção de palavras incorretas (como "Concórdia" quando deveria ser "Concorrência")
            
            Retorne o texto revisado, corrigindo todos os erros gramaticais e ortográficos, mas mantendo o conteúdo jurídico original.
            """
        }
        
        if specialty not in templates:
            raise ValueError(f"Especialidade não suportada: {specialty}")
        
        return templates[specialty]


class AgentOrchestrator:
    """Orquestrador de agentes para geração e revisão de petições"""
    
    def __init__(self, db_manager: DatabaseManager, ai_client: AITogetherClient):
        """Inicializa o orquestrador de agentes
        
        Args:
            db_manager: Gerenciador do banco de dados
            ai_client: Cliente da API do AI Together
        """
        self.db_manager = db_manager
        self.ai_client = ai_client
    
    def generate_petition(self, context: Dict[str, Any]) -> Dict[str, str]:
        """Gera uma petição completa usando os agentes configurados
        
        Args:
            context: Contexto para geração da petição
            
        Returns:
            Dicionário com os textos gerados em cada etapa
        """
        petition_type = context.get("tipo", "")
        agent_logger.info(f"Iniciando geração de petição do tipo: {petition_type}")
        agent_logger.info(f"Contexto completo: {json.dumps(context, ensure_ascii=False, indent=2)}")
        
        results = {}
        
        # Etapa 1: Geração do texto inicial
        agent_logger.info("ETAPA 1: Geração do texto inicial")
        generator_model = self._get_generator_model(petition_type)
        if not generator_model:
            error_msg = f"Nenhum agente gerador encontrado para o tipo de petição: {petition_type}"
            agent_logger.error(error_msg)
            raise ValueError(error_msg)
        
        generator_agent = self._create_generator_agent(generator_model)
        original_text = generator_agent.generate(context)
        results["original"] = original_text
        agent_logger.info("Texto original gerado com sucesso")
        
        # Etapa 2: Revisão gramatical
        agent_logger.info("ETAPA 2: Revisão gramatical")
        grammar_model = self._get_reviewer_model("gramatica")
        if grammar_model:
            grammar_agent = self._create_reviewer_agent(grammar_model)
            grammar_context = {
                "tipo": petition_type,
                "texto": original_text
            }
            grammar_text = grammar_agent.generate(grammar_context)
            results["gramatica"] = grammar_text
            current_text = grammar_text
            agent_logger.info("Revisão gramatical concluída com sucesso")
        else:
            agent_logger.warning("Nenhum agente revisor de gramática encontrado, pulando esta etapa")
            current_text = original_text
        
        # Etapa 3: Revisão jurídica
        agent_logger.info("ETAPA 3: Revisão jurídica")
        legal_model = self._get_reviewer_model("juridico")
        if legal_model:
            legal_agent = self._create_reviewer_agent(legal_model)
            legal_context = {
                "tipo": petition_type,
                "texto": current_text
            }
            legal_text = legal_agent.generate(legal_context)
            results["juridico"] = legal_text
            current_text = legal_text
            agent_logger.info("Revisão jurídica concluída com sucesso")
        else:
            agent_logger.warning("Nenhum agente revisor jurídico encontrado, pulando esta etapa")
        
        # Etapa 4: Revisão de linguagem
        agent_logger.info("ETAPA 4: Revisão de linguagem")
        language_model = self._get_reviewer_model("linguagem")
        if language_model:
            language_agent = self._create_reviewer_agent(language_model)
            language_context = {
                "tipo": petition_type,
                "texto": current_text
            }
            language_text = language_agent.generate(language_context)
            results["linguagem"] = language_text
            current_text = language_text
            agent_logger.info("Revisão de linguagem concluída com sucesso")
        else:
            agent_logger.warning("Nenhum agente revisor de linguagem encontrado, pulando esta etapa")
        
        # Etapa 5: Revisão de formatação
        agent_logger.info("ETAPA 5: Revisão de formatação")
        format_model = self._get_reviewer_model("formatacao")
        if format_model:
            format_agent = self._create_reviewer_agent(format_model)
            format_context = {
                "tipo": petition_type,
                "texto": current_text
            }
            format_text = format_agent.generate(format_context)
            results["formatacao"] = format_text
            current_text = format_text
            agent_logger.info("Revisão de formatação concluída com sucesso")
        else:
            agent_logger.warning("Nenhum agente revisor de formatação encontrado, pulando esta etapa")
        
        # Texto final
        results["final"] = current_text
        
        agent_logger.info("Geração de petição concluída com sucesso")
        agent_logger.info(f"Resultados: {json.dumps(list(results.keys()), ensure_ascii=False)}")
        
        return results
        
    def _get_generator_model(self, petition_type: str) -> Optional[Dict[str, Any]]:
        """Obtém o modelo de agente gerador para o tipo de petição especificado
        
        Args:
            petition_type: Tipo de petição
            
        Returns:
            Modelo do agente gerador ou None se não encontrado
        """
        return self.db_manager.get_agent_model_by_specialty("generator", petition_type)
    
    def _get_reviewer_model(self, review_type: str) -> Optional[Dict[str, Any]]:
        """Obtém o modelo de agente revisor para o tipo de revisão especificado
        
        Args:
            review_type: Tipo de revisão (jurídico, formatação, linguagem, gramatica)
            
        Returns:
            Modelo do agente revisor ou None se não encontrado
        """
        return self.db_manager.get_agent_model_by_specialty("reviewer", review_type)
    
    def _create_generator_agent(self, model: Dict[str, Any]) -> GeneratorAgent:
        """Cria um agente gerador a partir do modelo
        
        Args:
            model: Modelo do agente gerador
            
        Returns:
            Instância do agente gerador
        """
        return GeneratorAgent(
            self.ai_client,
            model["model_id"],
            model["specialty"],
            model["prompt_template"]
        )
    
    def _create_reviewer_agent(self, model: Dict[str, Any]) -> ReviewerAgent:
        """Cria um agente revisor a partir do modelo
        
        Args:
            model: Modelo do agente revisor
            
        Returns:
            Instância do agente revisor
        """
        return ReviewerAgent(
            self.ai_client,
            model["model_id"],
            model["specialty"],
            model["prompt_template"]
        ) 