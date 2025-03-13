# Instruções para enviar o projeto para o GitHub

Siga estas instruções para enviar o projeto para o repositório "peticao_together" no GitHub:

## Pré-requisitos

1. Ter o Git instalado no seu computador
2. Ter uma conta no GitHub
3. Ter permissões para enviar para o repositório "peticao_together"

## Passos

1. Abra o terminal (ou Git Bash no Windows)

2. Navegue até o diretório do projeto:
   ```bash
   cd /caminho/para/python_app
   ```

3. Inicialize um repositório Git local (se ainda não existir):
   ```bash
   git init
   ```

4. Adicione o repositório remoto:
   ```bash
   git remote add origin https://github.com/seu-usuario/peticao_together.git
   ```
   (Substitua "seu-usuario" pelo seu nome de usuário do GitHub)

5. Adicione todos os arquivos ao staging:
   ```bash
   git add .
   ```

6. Faça o commit dos arquivos:
   ```bash
   git commit -m "Versão inicial do sistema de geração de petições"
   ```

7. Envie os arquivos para o GitHub:
   ```bash
   git push -u origin main
   ```
   (Se o branch principal for "master" em vez de "main", use "master" no comando acima)

8. Se solicitado, insira suas credenciais do GitHub.

## Observações

- O arquivo `.gitignore` já foi configurado para excluir arquivos desnecessários como:
  - Ambientes virtuais (venv, .venv, etc.)
  - Arquivos de cache Python (__pycache__, *.pyc, etc.)
  - Banco de dados SQLite (*.db)
  - Arquivos de log
  - Arquivos de ambiente (.env)
  - Diretórios de resultados de teste

- Se você encontrar problemas com arquivos grandes, pode usar o Git LFS (Large File Storage):
  ```bash
  git lfs install
  git lfs track "*.json"  # Para arquivos JSON grandes
  git add .gitattributes
  ```

- Se você precisar atualizar o repositório após fazer alterações locais:
  ```bash
  git add .
  git commit -m "Descrição das alterações"
  git push
  ``` 