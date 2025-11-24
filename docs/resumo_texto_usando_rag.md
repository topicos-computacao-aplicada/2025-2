# **Construindo uma Aplicação RAG para Resumo de PDFs**

Introdução prática ao Retrieval-Augmented Generation
*Carregamento de PDFs · Chunking · Embeddings · Recuperação · Geração de resumo*

---

## **O que é RAG?**

### **Retrieval-Augmented Generation (RAG)**

* RAG combina recuperação de informação com geração de texto.
* **Problema:** LLMs têm conhecimento limitado e podem “alucinar”.
* **Solução:** Buscar informações relevantes e gerar respostas baseadas nelas.
* **Analogia:** Estudante que consulta livros antes de responder.

**Ideia central:** Em vez de “inventar”, o modelo consulta uma base atualizada.

---

## **Por que RAG para PDFs?**

### **Desafios com documentos longos**

* Limite de contexto dos modelos.
* Conteúdo técnico e especializado.
* PDFs contêm dados recentes fora do treinamento do LLM.
* Precisão: garantir que a resposta vem do documento.

### **Objetivo da aplicação**

* Receber um PDF do usuário.
* Recuperar apenas trechos relevantes.
* Produzir resumo fiel e útil.
* Pipeline modular e transparente.

---

## **Arquitetura de uma Aplicação RAG**

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   LOADING   │ →  │  CHUNKING   │ →  │ EMBEDDING   │
│   (PDF)     │    │ (Text Split)│    │ (Vectors)   │
└─────────────┘    └─────────────┘    └─────────────┘
                                        │
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   OUTPUT    │ ←  │  GENERATION │ ←  │ RETRIEVAL   │
│  (Resumo)   │    │   (LLM)     │    │  (Search)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### **Componentes principais**

* Loading (extração do PDF)
* Chunking (divisão do texto)
* Embedding (vetorização)
* Retrieval (busca dos K mais relevantes)
* Generation (LLM produz resumo)
* Output (apresentação ao usuário)

---

## Dependências da Aplicação

**`langchain-text-splitters`**: Divide textos longos em chunks menores para processamento eficiente pelos modelos de IA.

**`langchain-openai`**: Fornece integração com os modelos da OpenAI (GPT-4, GPT-3.5) para geração de resumos.

**`sentence-transformers`**: Gera embeddings vetoriais para representação semântica do texto.

**`faiss-cpu`**: Biblioteca de busca por similaridade para encontrar os chunks mais relevantes rapidamente.

**`pypdf`**: Extrai texto de arquivos PDF.

**`langchain-community`**: Oferece componentes adicionais e integrações com ferramentas de código aberto.

## Fluxo da Aplicação

### **Fluxo Principal:**

1. **Carregamento do Documento**
   - Entrada: Arquivo PDF
   - Processo: Extrai todo o texto do PDF, organizando por páginas
   - Saída: Lista de documentos estruturados

2. **Divisão em Chunks (Chunking)**
   - Divide o texto em segmentos menores (1200 caracteres)
   - Mantém sobreposição de 200 caracteres para preservar contexto
   - Adiciona metadados de localização (página, índice inicial)

3. **Indexação Vetorial**
   - Converte cada chunk em vetor numérico (embedding)
   - Cria índice de busca por similaridade usando FAISS
   - Permite busca semântica por conteúdo relacionado

4. **Recuperação de Informação**
   - Recebe a pergunta/consulta do usuário
   - Encontra os K chunks mais relevantes (default: 6)
   - Baseia-se na similaridade semântica

5. **Geração do Resumo**
   - Combina os chunks recuperados em contexto estruturado
   - Envia para o LLM (GPT-4o-mini) com prompt específico
   - Gera resumo focalizado na pergunta do usuário

### **Características Específicas:**

- **Rastreabilidade**: Cada chunk inclui metadados de página e posição
- **Contexto Limitado**: LLM só utiliza informações dos chunks recuperados
- **Idioma Português**: Resposta sempre em português
- **Transparência**: Exibe tanto os chunks recuperados quanto o resumo final

### **Entrada/Saída:**
- **Input**: PDF + Pergunta específica
- **Output**: Chunks relevantes + Resumo contextualizado
- **Configuração**: Parâmetros ajustáveis (K, tamanho de chunks, modelo LLM)

### **Tratamento de Limitações:**
- Verifica existência do arquivo PDF
- LLM declara quando informações não estão no contexto fornecido
- Estrutura clara de bullet points para organização do conteúdo


## **Fase 1: Carregamento do PDF**

### Extraindo conteúdo do documento

```python
from langchain_community.document_loaders import PyPDFLoader

def load_pdf_docs(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()  # lista de Documents (1 por página)
    return docs
```

* Extrai texto por página.
* Produz objetos `Document` com metadados.
* Facilita rastreamento de páginas e posições.

---

## **Fase 2: Chunking**

### Dividindo para conquistar

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    add_start_index=True,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_documents(docs)
```

* LLMs têm limites de tokens.
* Busca mais precisa em trechos menores.
* Overlap evita cortes ruins em frases.
* Separadores hierárquicos preservam semântica.

---

## **Fase 3: Embeddings & Indexação**

### Transformando texto em vetores

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embedder = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.from_documents(chunks, embedder)
```

* Embeddings representam significado do texto.
* Textos similares → vetores próximos.
* Suporte multilíngue: PT + EN.
* FAISS permite buscas rápidas e armazenamento local.

---

## **Fase 4: Sistema de Recuperação**

### Encontrando os trechos corretos

```python
def make_retriever(vectorstore, k=6):
    return vectorstore.as_retriever(
        search_kwargs={"k": k}
    )

retriever = make_retriever(vectorstore)
relevant_chunks = retriever.invoke("resuma o documento")
```

* Pergunta → embedding de consulta.
* Similaridade com todos os chunks.
* Retorno dos **K mais relevantes**.

---

## **Fase 5: Geração do Resumo**

### Juntando as peças

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente... Use APENAS o contexto."),
    ("human", "Pergunta: {question}\nContexto: {context}")
])

chain = prompt | llm

response = chain.invoke({
    "question": "Resuma o documento",
    "context": formatted_chunks
})
```

* Modelo organiza e condensa o conteúdo recuperado.
* Mantém clareza, coerência e fidelidade ao PDF.

---

## **Prompt Engineering**

### Instruções eficientes

```python
system_prompt = """
Você é um assistente que responde SOMENTE
com base no CONTEXTO fornecido.
Se algo não estiver no contexto, diga que
não há evidências.
Produza um resumo claro, fiel e objetivo.
Idioma: português.
"""
```

**Boas práticas**:

* Explicitar que deve usar apenas o contexto.
* Solicitar confirmação quando algo não existir no texto.
* Definir formato de resposta.
* Definir idioma.

---

## **Pipeline Completo**

### End-to-End

```python
def query_and_summarize(pdf_path, question, k=6):
    # 1. Loading
    docs = load_pdf_docs(pdf_path)

    # 2. Chunking
    chunks = chunk_documents(docs)

    # 3. Embedding + Indexing
    vectorstore = build_vectorstore(chunks)

    # 4. Retrieval
    retriever = make_retriever(vectorstore, k)
    relevant_chunks = retriever.invoke(question)

    # 5. Generation
    context = format_docs(relevant_chunks)
    summary = chain.invoke({
        "question": question,
        "context": context
    })
    return summary
```

---

## **Desafios e Soluções**

| Desafio                 | Solução                            |
| ----------------------- | ---------------------------------- |
| Chunks quebram frases   | Overlap + separadores hierárquicos |
| Informação perdida      | Ajustar chunk_size e k             |
| Contexto insuficiente   | Aumentar k ou chunk_size           |
| Metadados insuficientes | `add_start_index=True`             |

---

## **Boas Práticas**

1. Rastreabilidade: manter página e posição.
2. Parâmetros ajustáveis: `k`, `chunk_size`.
3. Validação: verificar existência do arquivo.
4. Transparência: exibir chunks usados.
5. Especificar idioma no prompt.

**Observabilidade mínima**

* Medir tempo por etapa.
* Registrar quantos chunks viram contexto.
* Gravar amostras de Q&A.

---

## **Extensões Possíveis**

### Indo além

* Multimodal: imagens, tabelas e fórmulas.
* Cache de embeddings.
* Hybrid search: semântica + BM25.
* Métricas de qualidade.
* Web interface.

### Casos de uso

* Artigos científicos.
* Relatórios técnicos.
* Bases documentais institucionais.

---

## **Ferramentas e Tecnologias**

### Core

* LangChain
* FAISS
* Sentence Transformers
* OpenAI / Gemini LLMs

### Alternativas

* Chroma, Pinecone, Qdrant
* Cohere, Anthropic
* Haystack, LlamaIndex

---

## **Conclusões**

* RAG supera limite de contexto dos LLMs.
* Arquitetura modular permite evolução rápida.
* Chunking inteligente é crucial.
* Prompts moldam o comportamento do modelo.
* Rastreabilidade é essencial para produção.

**Próximos passos:** testar com diferentes PDFs e iterar.

---

## **Q&A**

### Perguntas para discussão

* Como avaliar a qualidade do resumo?
* Quais métricas usar?
* Como lidar com PDFs complexos?
* Quando RAG não é adequado?
