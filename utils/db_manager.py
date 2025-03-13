import sqlite3
import os
import json
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador de banco de dados SQLite para o sistema de petições"""
    
    def __init__(self, db_path: str = "aitogether.db"):
        """Inicializa o gerenciador de banco de dados
        
        Args:
            db_path: Caminho para o arquivo do banco de dados
        """
        self.db_path = db_path
        self._ensure_db_dir()
        self._init_db()
    
    def _ensure_db_dir(self):
        """Garante que o diretório do banco de dados existe"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtém uma conexão com o banco de dados
        
        Returns:
            Conexão com o banco de dados
        """
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Tabela de Modelos de Agentes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS agent_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            model_id TEXT NOT NULL,
            type TEXT NOT NULL,
            specialty TEXT NOT NULL,
            prompt_template TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tabela de Tipos de Petição
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS petition_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            template_path TEXT,
            required_fields TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Tabela de Petições
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS petitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            client_id TEXT,
            petition_type_id TEXT,
            status TEXT DEFAULT 'draft',
            facts TEXT,
            arguments TEXT,
            requests TEXT,
            generated_text TEXT,
            reviewed_text TEXT,
            final_text TEXT,
            final_document_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (petition_type_id) REFERENCES petition_types(code)
        )
        ''')
        
        # Tabela de Histórico de Geração
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS generation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            petition_id INTEGER,
            agent_model_id INTEGER,
            prompt TEXT,
            response TEXT,
            generation_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (petition_id) REFERENCES petitions(id),
            FOREIGN KEY (agent_model_id) REFERENCES agent_models(id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        # Importar tipos de petição do arquivo JSON se a tabela estiver vazia
        self._import_petition_types()
    
    def _import_petition_types(self):
        """Importa os tipos de petição do arquivo JSON para o banco de dados"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Verificar se já existem tipos de petição
        cursor.execute("SELECT COUNT(*) FROM petition_types")
        count = cursor.fetchone()[0]
        
        if count == 0:
            try:
                # Carregar tipos de petição do arquivo JSON
                with open("data/tipos_peticao.json", "r", encoding="utf-8") as f:
                    tipos_peticao = json.load(f)
                
                # Inserir tipos de petição no banco de dados
                for tipo in tipos_peticao:
                    required_fields = json.dumps(["fatos", "argumentos", "pedidos"])
                    template_path = f"templates_docx/{tipo['id']}.docx"
                    
                    cursor.execute('''
                    INSERT INTO petition_types (code, name, description, template_path, required_fields)
                    VALUES (?, ?, ?, ?, ?)
                    ''', (
                        tipo["id"],
                        tipo["nome"],
                        tipo["descricao"],
                        template_path,
                        required_fields
                    ))
                
                conn.commit()
                logger.info(f"Importados {len(tipos_peticao)} tipos de petição")
            except Exception as e:
                logger.error(f"Erro ao importar tipos de petição: {str(e)}")
        
        conn.close()
    
    def add_agent_model(self, name: str, description: str, model_id: str, 
                       agent_type: str, specialty: str, prompt_template: str) -> int:
        """Adiciona um novo modelo de agente ao banco de dados
        
        Args:
            name: Nome do modelo
            description: Descrição do modelo
            model_id: ID do modelo no AI Together
            agent_type: Tipo do agente ('generator' ou 'reviewer')
            specialty: Especialidade do agente
            prompt_template: Template de prompt do agente
            
        Returns:
            ID do modelo adicionado
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO agent_models (name, description, model_id, type, specialty, prompt_template)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, model_id, agent_type, specialty, prompt_template))
        
        model_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return model_id
    
    def get_agent_models(self, agent_type: Optional[str] = None, 
                        specialty: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtém modelos de agente do banco de dados
        
        Args:
            agent_type: Filtrar por tipo de agente
            specialty: Filtrar por especialidade
            
        Returns:
            Lista de modelos de agente
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM agent_models"
        params = []
        
        if agent_type or specialty:
            query += " WHERE"
            
            if agent_type:
                query += " type = ?"
                params.append(agent_type)
                
                if specialty:
                    query += " AND"
            
            if specialty:
                query += " specialty = ?"
                params.append(specialty)
        
        cursor.execute(query, params)
        models = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return models
    
    def get_agent_model(self, model_id: int) -> Optional[Dict[str, Any]]:
        """Obtém um modelo de agente pelo ID
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Modelo de agente ou None se não encontrado
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM agent_models WHERE id = ?", (model_id,))
        model = cursor.fetchone()
        
        conn.close()
        return dict(model) if model else None
    
    def get_agent_model_by_specialty(self, agent_type: str, specialty: str) -> Optional[Dict[str, Any]]:
        """Obtém um modelo de agente pelo tipo e especialidade
        
        Args:
            agent_type: Tipo do agente ('generator' ou 'reviewer')
            specialty: Especialidade do agente
            
        Returns:
            Modelo de agente ou None se não encontrado
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM agent_models 
        WHERE type = ? AND specialty = ?
        """, (agent_type, specialty))
        
        model = cursor.fetchone()
        conn.close()
        
        return dict(model) if model else None
    
    def get_petition_types(self) -> List[Dict[str, Any]]:
        """Obtém todos os tipos de petição
        
        Returns:
            Lista de tipos de petição
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM petition_types")
        types = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return types
    
    def get_petition_type(self, type_code: str) -> Optional[Dict[str, Any]]:
        """Obtém um tipo de petição pelo código
        
        Args:
            type_code: Código do tipo de petição
            
        Returns:
            Tipo de petição ou None se não encontrado
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM petition_types WHERE code = ?", (type_code,))
        petition_type = cursor.fetchone()
        
        conn.close()
        return dict(petition_type) if petition_type else None
    
    def add_petition(self, title: str, client_id: str, petition_type_id: str,
                    facts: str, arguments: str, requests: str) -> int:
        """Adiciona uma nova petição ao banco de dados
        
        Args:
            title: Título da petição
            client_id: ID do cliente
            petition_type_id: ID do tipo de petição
            facts: Fatos da petição
            arguments: Argumentos da petição
            requests: Pedidos da petição
            
        Returns:
            ID da petição adicionada
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO petitions (
            title, client_id, petition_type_id, facts, arguments, requests, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, client_id, petition_type_id, facts, arguments, requests, 'draft'))
        
        petition_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return petition_id
    
    def update_petition(self, petition_id: int, generated_text: Optional[str] = None,
                       reviewed_text: Optional[str] = None, final_text: Optional[str] = None,
                       final_document_path: Optional[str] = None, status: Optional[str] = None) -> bool:
        """Atualiza uma petição existente
        
        Args:
            petition_id: ID da petição
            generated_text: Texto gerado
            reviewed_text: Texto revisado
            final_text: Texto final
            final_document_path: Caminho do documento final
            status: Status da petição
            
        Returns:
            True se a atualização foi bem-sucedida
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        update_fields = []
        params = []
        
        if generated_text is not None:
            update_fields.append("generated_text = ?")
            params.append(generated_text)
        
        if reviewed_text is not None:
            update_fields.append("reviewed_text = ?")
            params.append(reviewed_text)
        
        if final_text is not None:
            update_fields.append("final_text = ?")
            params.append(final_text)
        
        if final_document_path is not None:
            update_fields.append("final_document_path = ?")
            params.append(final_document_path)
        
        if status is not None:
            update_fields.append("status = ?")
            params.append(status)
        
        if not update_fields:
            return False
        
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        query = f"UPDATE petitions SET {', '.join(update_fields)} WHERE id = ?"
        params.append(petition_id)
        
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        
        return True
    
    def get_petition(self, petition_id: int) -> Optional[Dict[str, Any]]:
        """Obtém uma petição pelo ID
        
        Args:
            petition_id: ID da petição
            
        Returns:
            Petição ou None se não encontrada
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM petitions WHERE id = ?", (petition_id,))
        petition = cursor.fetchone()
        
        conn.close()
        return dict(petition) if petition else None
    
    def get_petitions(self, client_id: Optional[str] = None, 
                     petition_type_id: Optional[str] = None,
                     status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtém petições com filtros opcionais
        
        Args:
            client_id: Filtrar por ID do cliente
            petition_type_id: Filtrar por ID do tipo de petição
            status: Filtrar por status
            
        Returns:
            Lista de petições
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM petitions"
        params = []
        
        if client_id or petition_type_id or status:
            query += " WHERE"
            conditions = []
            
            if client_id:
                conditions.append("client_id = ?")
                params.append(client_id)
            
            if petition_type_id:
                conditions.append("petition_type_id = ?")
                params.append(petition_type_id)
            
            if status:
                conditions.append("status = ?")
                params.append(status)
            
            query += " " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        petitions = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return petitions
    
    def add_generation_history(self, petition_id: int, agent_model_id: int,
                              prompt: str, response: str, generation_type: str) -> int:
        """Adiciona um registro ao histórico de geração
        
        Args:
            petition_id: ID da petição
            agent_model_id: ID do modelo de agente
            prompt: Prompt utilizado
            response: Resposta gerada
            generation_type: Tipo de geração
            
        Returns:
            ID do registro adicionado
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO generation_history (
            petition_id, agent_model_id, prompt, response, generation_type
        ) VALUES (?, ?, ?, ?, ?)
        ''', (petition_id, agent_model_id, prompt, response, generation_type))
        
        history_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return history_id
    
    def get_generation_history(self, petition_id: int) -> List[Dict[str, Any]]:
        """Obtém o histórico de geração de uma petição
        
        Args:
            petition_id: ID da petição
            
        Returns:
            Lista de registros do histórico
        """
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT h.*, a.name as agent_name, a.type as agent_type, a.specialty as agent_specialty
        FROM generation_history h
        JOIN agent_models a ON h.agent_model_id = a.id
        WHERE h.petition_id = ?
        ORDER BY h.created_at ASC
        ''', (petition_id,))
        
        history = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return history 