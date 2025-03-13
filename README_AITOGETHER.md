# Sistema de Geração de Petições com AI Together

Este sistema utiliza a API do AI Together para gerar petições jurídicas com múltiplos agentes especializados.

## Visão Geral

O sistema implementa uma arquitetura multi-agente para geração e revisão de petições jurídicas:

1. **Agentes Geradores**: Especializados em criar diferentes tipos de petições
   - Recurso Administrativo
   - Impugnação ao Edital
   - Mandado de Segurança
   - Contrarrazões de Recurso

2. **Agentes Revisores**: Especializados em revisar diferentes aspectos das petições
   - Revisor Jurídico: Verifica precisão legal e argumentação
   - Revisor de Formatação: Garante formatação adequada
   - Revisor de Linguagem: Melhora a clareza e estilo da escrita

## Requisitos

- Python 3.8+
- Chave de API do AI Together
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Copie o arquivo `.env.example` para `.env` e configure suas chaves de API:
   ```
   cp .env.example .env
   ```
4. Edite o arquivo `.env` e adicione sua chave de API do AI Together:
   ```
   AITOGETHER_API_KEY=sua_chave_api_aqui
   ```

## Inicialização do Sistema

Execute o script de inicialização para configurar o banco de dados e os agentes:

```
python inicializar_aitogether.py
```

Este script irá:
- Criar o banco de dados SQLite
- Configurar os agentes geradores e revisores padrão
- Testar a conexão com a API do AI Together

## Testando o Sistema

Para testar a geração de petições, use o script de teste:

```
python testar_aitogether.py recurso_administrativo
```

Substitua `recurso_administrativo` por um dos tipos de petição suportados:
- `recurso_administrativo`
- `impugnacao_edital`
- `mandado_seguranca`
- `contrarrazoes_recurso`

Os resultados serão salvos na pasta `resultados_teste`.

## API REST

O sistema expõe as seguintes rotas de API:

### Geração de Petições

- **POST /api/gerar-peticao-aitogether**
  - Gera uma petição usando o sistema multi-agente
  - Corpo da requisição:
    ```json
    {
      "tipo": "recurso_administrativo",
      "fatos": "Descrição dos fatos...",
      "argumentos": "Argumentos jurídicos...",
      "pedidos": "Pedidos da petição...",
      "cliente_id": "id_do_cliente",
      "cliente_nome": "Nome do Cliente",
      "cliente_cnpj": "12.345.678/0001-90",
      "referencia_processo": "Referência do processo",
      "autoridade": "Autoridade destinatária",
      "cidade": "Cidade"
    }
    ```

### Gerenciamento de Agentes

- **GET /api/agents**
  - Lista os agentes configurados
  - Parâmetros de consulta opcionais:
    - `type`: Filtrar por tipo de agente (`generator` ou `reviewer`)
    - `specialty`: Filtrar por especialidade

- **POST /api/agents**
  - Adiciona um novo agente
  - Corpo da requisição:
    ```json
    {
      "name": "Nome do Agente",
      "description": "Descrição do agente",
      "model_id": "llama-3-70b-instruct",
      "type": "generator",
      "specialty": "recurso_administrativo",
      "prompt_template": "Template de prompt..."
    }
    ```

### Consulta de Modelos

- **GET /api/aitogether/models**
  - Lista os modelos disponíveis na API do AI Together

### Gerenciamento de Petições

- **GET /api/peticoes-aitogether**
  - Lista as petições geradas
  - Parâmetros de consulta opcionais:
    - `client_id`: Filtrar por cliente
    - `petition_type_id`: Filtrar por tipo de petição
    - `status`: Filtrar por status

- **GET /api/peticoes-aitogether/{id}**
  - Obtém detalhes de uma petição específica

## Estrutura do Banco de Dados

O sistema utiliza um banco de dados SQLite com as seguintes tabelas:

1. **agent_models**: Armazena os modelos de agentes
2. **petition_types**: Armazena os tipos de petição
3. **petitions**: Armazena as petições geradas
4. **generation_history**: Armazena o histórico de geração

## Personalização

### Adicionando Novos Tipos de Petição

1. Adicione o novo tipo no arquivo `data/tipos_peticao.json`
2. Crie um template DOCX em `templates_docx/`
3. Adicione um agente gerador para o novo tipo

### Personalizando Agentes

Use a API REST para adicionar ou modificar agentes:

```
POST /api/agents
```

## Solução de Problemas

### Erro de Conexão com a API

Verifique se sua chave de API está correta no arquivo `.env`.

### Erro ao Gerar Petição

Verifique os logs para identificar o problema específico. Possíveis causas:
- Chave de API inválida
- Modelo não disponível
- Dados de entrada incompletos

## Contribuindo

Contribuições são bem-vindas! Por favor, abra um issue ou pull request para sugerir melhorias. 