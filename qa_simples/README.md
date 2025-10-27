# Chat simples usando o Langchain

## Configuração

Crie um arquivo .env e salve o valor da respectiva API_KEY (GOOGLE_API_KEY)

Crie o ambiente virtual (venv)

Instale as dependências

```bash
pip3 install -r requirements.txt
```

Execute a aplicação

```bash
python3 gemini_qa_lc.py
```

## Troubleshooting

```bash
# Desinstalar versões conflitantes (opcional)
pip3 uninstall langchain langchain-core langchain-google-genai -y

# Instalar as versões mais recentes
pip3 install -U langchain langchain-core langchain-google-genai python-dotenv
```
