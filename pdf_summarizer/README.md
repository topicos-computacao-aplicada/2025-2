# Instruções

## Preparar ambiente backend

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
```

Instalar dependências

```bash
pip install -r requirements.txt
```

Configure sua chave da API de manipulação do Modelo LLM OPENAI_API_KEY=?

## Executando o servidor

```bash
uvicorn backend.app.main:app
```

## Teste via CURL

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/summary/pdf' \
  -F 'file=@/caminho/para/seu.pdf' \
  -F 'question=Faça um resumo geral' \
  -F 'k=6'
```

## Executar o cliente

```bash
cd pdf_summarizer
source .venv/bin/activate          # se ainda não estiver ativo
python frontend/client.py
```

Saída:
```bash
=== Cliente de Terminal: Resumo de PDF (RAG) ===
Backend configurado em: http://localhost:8000

Menu:
1 - Resumir um PDF
0 - Sair
```

Fluxo padrão:

1. Escolha opção `1`.
2. Informe o caminho do PDF, por exemplo:
   `/Users/armando/Documentos/artigo.pdf`
3. Informe a pergunta, por exemplo:
   `Faça um resumo geral destacando os principais resultados.`
4. Informe `k` (ou aperte Enter para usar 6).

O cliente:

* Lê o PDF local.
* Envia o arquivo para o backend via `multipart/form-data`.
* O backend:

  * Carrega o PDF com `PyPDFLoader`
  * Faz chunking (`RecursiveCharacterTextSplitter`)
  * Cria embeddings com `HuggingFaceEmbeddings`
  * Indexa em FAISS
  * Recupera os `k` chunks mais relevantes
  * Monta um prompt com contexto + pergunta
  * Chama `ChatOpenAI` (modelo `gpt-4o-mini`)
* Backend devolve resumo + preview dos chunks.
* O cliente imprime tudo no terminal.