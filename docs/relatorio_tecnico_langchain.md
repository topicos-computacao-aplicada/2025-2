**Paper Técnico** sobre o **LangChain**, cobrindo conceitos fundamentais, componentes, cadeias (chains), exemplos de uso e um estudo de caso de aplicação (RAG com PDFs).

Armando Soares Sousa - UFPI/DC - 22/08/2025

# LangChain: Um Framework para Construção de Aplicações Baseadas em Modelos de Linguagem

## Resumo

Os **Large Language Models ([LLMs](https://arxiv.org/abs/2402.06196))** têm se consolidado como tecnologias-chave para aplicações de Inteligência Artificial (IA) em diversas áreas, incluindo **busca semântica**, **geração de texto**, **sumarização** e **agentes conversacionais**. Entretanto, a integração desses modelos em sistemas reais demanda uma camada de orquestração, capaz de gerenciar interações, conectar dados externos e oferecer memória conversacional. O **LangChain** surge como um framework projetado para atender a essas necessidades, oferecendo abstrações para desenvolvimento de **aplicações baseadas em LLMs de maneira modular e escalável**. Este artigo apresenta uma visão técnica do LangChain, seus principais componentes, cadeias (chains), exemplos de uso e um estudo de caso prático envolvendo **RAG ([Retrieval-Augmented Generation](https://arxiv.org/abs/2404.19543))** aplicado a documentos PDF.

## 1. Introdução

O avanço dos **LLMs** como [GPT-4](https://cdn.openai.com/papers/gpt-4.pdf?utm_source=chatgpt.com), [LLaMA](https://arxiv.org/abs/2302.13971) e [Mistral](https://arxiv.org/abs/2310.06825) transformou o paradigma de interação humano-máquina, permitindo a construção de sistemas capazes de raciocínio, contextualização e inferência em linguagem natural (Brown et al., 2020; Touvron et al., 2023). No entanto, para transformar tais modelos em **aplicações de produção**, é necessário lidar com desafios como:

* Gerenciamento de **prompts complexos**.
* Integração com **bases de dados externas**.
* Suporte a **memória conversacional**.
* Criação de **agentes autônomos** capazes de decidir qual ferramenta utilizar em um dado contexto.

O **LangChain** (LangChain, 2025) foi projetado para abstrair esses aspectos, fornecendo uma estrutura modular para construção de aplicações robustas de IA.

## 2. Componentes do LangChain

O LangChain organiza suas funcionalidades em componentes principais:

### 2.1. Modelos

Permite integrar LLMs de diferentes provedores ([OpenAI](https://openai.com), [Anthropic](https://www.anthropic.com), [Hugging Face](https://huggingface.co), [Ollama](https://ollama.com)), oferecendo suporte tanto para **LLMs de geração** quanto para **chat models**.

### 2.2. Prompts

Prompts podem ser representados de forma estruturada através de **Prompt Templates**, que facilitam a reusabilidade e reduzem riscos de inconsistência semântica (White et al., 2023).

### 2.3. Cadeias (Chains)

Uma **Chain** representa a orquestração de chamadas a LLMs e ferramentas externas.
Exemplos:

* **LLMChain**: simples, executa prompt → LLM.
* **SequentialChain**: encadeia múltiplos passos.
* **ConversationalRetrievalChain**: integra busca em vetores (RAG) com diálogo.

### 2.4. Memória

O LangChain oferece abstrações de **Memory**, que permitem armazenar contexto de interações anteriores, seja em memória volátil ou persistida em bancos externos (Redis, SQLite).

### 2.5. Retrievers e VectorStores

Integração com bancos vetoriais ([FAISS](https://faiss.ai), [Chroma](https://www.trychroma.com), [Milvus](https://milvus.io)) para **busca semântica** em documentos. Essa camada é fundamental para **RAG** (Lewis et al., 2020).

### 2.6. Agentes

Agentes utilizam LLMs como mecanismo de decisão, selecionando dinamicamente ferramentas (APIs, cálculos, bancos de dados). Essa abordagem aproxima-se da noção de **autonomous LLM agents** discutida em literatura recente (Park et al., 2023).

## 3. Funcionamento e Arquitetura

A arquitetura do LangChain pode ser entendida em três camadas:

1. **Core Abstractions**: Modelos, Prompts, Memory.
2. **Chains e Agents**: Orquestração lógica de fluxos de decisão.
3. **Aplicações**: Interfaces de usuário, integrações com sistemas externos (via APIs, bancos de dados, pipelines).

Essa arquitetura permite **composabilidade**, onde novos sistemas podem ser construídos reutilizando blocos já existentes.

## 4. Exemplos de Uso

### 4.1. Tradução Automática com Prompt Template

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template("Traduza para português: {texto}")
chain = LLMChain(llm=llm, prompt=prompt)

resposta = chain.run({"texto": "Artificial Intelligence is transforming the world."})
print(resposta)
```

### 4.2. Chatbot com Memória

```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

llm = ChatOpenAI(model="gpt-4o-mini")
memory = ConversationBufferMemory()
chat = ConversationChain(llm=llm, memory=memory)

print(chat.predict(input="Olá, quem é você?"))
print(chat.predict(input="E qual foi minha pergunta anterior?"))
```

### 4.3 Resumo de textos

```python
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# LangChain (v0.2+)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

# ---- Configurações principais ----
MODEL_NAME = "gpt-4o-mini"
CHUNK_SIZE = 1500       # caracteres
CHUNK_OVERLAP = 150     # caracteres
LONG_TEXT_THRESHOLD = 3500  # acima disso, aplicar chunking

def build_summary_chain(model: ChatOpenAI):
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Você é um assistente experiente em escrita técnica. "
         "Resuma o texto do usuário em português claro, conciso e fiel, "
         "preservando ideias centrais e evitando detalhes supérfluos. "
         "Se houver listas, sintetize-as em bullets curtos."),
        ("user", "Texto a resumir:\n\n{input_text}")
    ])
    return prompt | model | StrOutputParser()

def build_combine_chain(model: ChatOpenAI):
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Combine os resumos parciais abaixo em um único resumo coeso, "
         "eliminando redundâncias e mantendo apenas as ideias principais. "
         "Escreva em português objetivo, ~5-10 linhas."),
        ("user", "Resumos parciais:\n\n{partials}")
    ])
    return prompt | model | StrOutputParser()

def summarize_text(text: str, temperature: float = 0.2) -> str:
    model = ChatOpenAI(model=MODEL_NAME, temperature=temperature)

    # Caso curto: resumo direto
    if len(text) <= LONG_TEXT_THRESHOLD:
        chain = build_summary_chain(model)
        return chain.invoke({"input_text": text})

    # Caso longo: chunking + resumo por parte + combinação
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " "]
    )
    chunks = splitter.split_text(text)

    summary_chain = build_summary_chain(model)
    partials = []
    for i, chunk in enumerate(chunks, start=1):
        partial = summary_chain.invoke({"input_text": chunk})
        partials.append(f"[Parte {i}]\n{partial}")

    combine_chain = build_combine_chain(model)
    combined = combine_chain.invoke({"partials": "\n\n".join(partials)})
    return combined

def read_input(args) -> str:
    # 1) --text tem prioridade
    if args.text:
        return args.text

    # 2) arquivo
    if args.file:
        p = Path(args.file)
        if not p.exists():
            sys.exit(f"Arquivo não encontrado: {p}")
        return p.read_text(encoding="utf-8")

    # 3) stdin
    if not sys.stdin.isatty():
        return sys.stdin.read()

    sys.exit("Nenhum texto fornecido. Use --text, --file ou stdin.")

def main():
    parser = argparse.ArgumentParser(
        description="Resumo de texto usando LangChain + OpenAI gpt-4o-mini (RAG-free)."
    )
    parser.add_argument("--text", type=str, help="Texto a ser resumido (string).")
    parser.add_argument("--file", type=str, help="Caminho para arquivo de texto.")
    parser.add_argument("--temperature", type=float, default=0.2,
                        help="Temperatura do modelo (padrão: 0.2).")
    args = parser.parse_args()

    text = read_input(args)
    summary = summarize_text(text, temperature=args.temperature)
    print(summary.strip())

if __name__ == "__main__":
    main()
```

## 5. Estudo de Caso: RAG com PDFs

O **RAG (Retrieval-Augmented Generation)** combina **busca em documentos vetorizados** com **geração de texto por LLMs**.

### Pipeline:

1. **Ingestão de documentos PDF** → divisão em *chunks*.
2. **Indexação** em um **VectorStore** (ChromaDB).
3. **Retriever** para buscar trechos relevantes.
4. **ConversationalRetrievalChain** para integrar contexto ao diálogo.

Exemplo simplificado:

```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI

# 1. Carregar PDF
loader = PyPDFLoader("documento.pdf")
docs = loader.load()

# 2. Dividir em chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
chunks = splitter.split_documents(docs)

# 3. Criar vetor semântico
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = Chroma.from_documents(chunks, embeddings)

# 4. Criar RAG
retriever = vectordb.as_retriever(search_kwargs={"k":3})
llm = ChatOpenAI(model="gpt-4o-mini")
qa = ConversationalRetrievalChain.from_llm(llm, retriever=retriever)

# 5. Pergunta
resposta = qa({"question":"Resuma o documento", "chat_history":[]})
print(resposta["answer"])
```

Essa abordagem é extensível a **chatbots corporativos**, **sistemas jurídicos** ou **educacionais**, permitindo consulta a grandes coleções de documentos.

## 6. Discussão

O LangChain se destaca como **middleware para LLMs**, fornecendo recursos para integração de dados externos e memória conversacional. Seu uso em **RAG** reforça o potencial dos LLMs em contextos de **knowledge-intensive tasks**, mitigando limitações como **alucinações** (Shuster et al., 2021).

Entretanto, desafios permanecem:

* Custos de execução em produção.
* Garantia de **segurança e privacidade** de dados.
* Necessidade de **avaliação de qualidade** das respostas (Zheng et al., 2023).

## 7. Conclusão

O LangChain é um framework essencial para **transformar LLMs em aplicações reais**, suportando desde casos simples de tradução até sistemas complexos de RAG e agentes autônomos. Sua modularidade, aliada à ampla adoção da comunidade, o coloca como um dos pilares na nova geração de aplicações de IA.

## Referências

* Brown, T., et al. (2020). *Language Models are Few-Shot Learners*. Advances in Neural Information Processing Systems (NeurIPS).
* Lewis, P., et al. (2020). *Retrieval-augmented generation for knowledge-intensive NLP tasks*. NeurIPS.
* Park, J. S., et al. (2023). *Generative Agents: Interactive Simulacra of Human Behavior*. ACM.
* Shuster, K., et al. (2021). *Retrieval Augmentation Reduces Hallucination in Conversation*. EMNLP.
* Touvron, H., et al. (2023). *LLaMA: Open and Efficient Foundation Language Models*. arXiv preprint arXiv:2302.13971.
* White, J., et al. (2023). *A Prompt Pattern Catalog to Enhance Prompt Engineering with ChatGPT*. arXiv:2302.11382.
* Zheng, C., et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. arXiv:2306.05685.
* **LangChain Official Documentation**: [https://www.langchain.com](https://www.langchain.com) (acesso em agosto de 2025).
