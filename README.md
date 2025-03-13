# Sistema de Geração de Petições Jurídicas

Sistema de geração de petições jurídicas utilizando IA para o mercado de licitações públicas.

## Descrição

Este projeto implementa um sistema de geração automática de petições jurídicas para o mercado de licitações públicas, utilizando a API da Together AI para processamento de linguagem natural e geração de texto.

O sistema é capaz de gerar diferentes tipos de petições, como:
- Recurso administrativo
- Pedido de reconsideração
- Pedido de reajustamento
- Pedido de reequilíbrio econômico-financeiro
- Pedido de troca de marca
- Pedido de rescisão unilateral
- Pedido de paralisação de obra
- Entre outros

## Funcionalidades

- Geração de petições jurídicas com base em templates
- Revisão gramatical automática
- Revisão jurídica automática
- Revisão de linguagem automática
- Revisão de formatação automática
- Exportação para formato de texto

## Tecnologias Utilizadas

- Python
- Together AI API
- SQLite
- Biblioteca python-docx para manipulação de documentos Word
- Biblioteca requests para comunicação com APIs

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/peticao_together.git
cd peticao_together
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

## Uso

Para gerar uma petição, execute o script `testar_aitogether.py` com o tipo de petição desejado:

```bash
python testar_aitogether.py recurso_administrativo
```

Os resultados serão salvos na pasta `resultados_teste/`.

## Estrutura do Projeto

- `app.py`: Aplicação web principal
- `inicializar_aitogether.py`: Script para inicializar o banco de dados e configurar os agentes
- `limpar_banco.py`: Script para limpar o banco de dados
- `testar_aitogether.py`: Script para testar a geração de petições
- `testar_conexao.py`: Script para testar a conexão com a API da Together AI
- `utils/`: Módulos utilitários para o funcionamento do sistema
- `templates/`: Templates HTML para a interface web
- `templates_docx/`: Templates DOCX para geração de petições
- `data/`: Dados necessários para o sistema

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para mais detalhes. 