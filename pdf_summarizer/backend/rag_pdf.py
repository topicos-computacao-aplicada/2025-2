import os
from typing import List
from dotenv import load_dotenv

# 1) Carregamento do PDF
from langchain_community.document_loaders import PyPDFLoader
# 2) Chunking
from langchain_text_splitters import RecursiveCharacterTextSplitter
# 3) Embeddings e Vetorstore (FAISS)
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
# (alternativa OpenAI: from langchain_openai import OpenAIEmbeddings)
# 4) LLM e Prompt
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()  # carrega OPENAI_API_KEY do .env (se existir)

def load_pdf_docs(pdf_path: str):
    """Carrega páginas do PDF como Document objects do LangChain."""
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()  # lista de Documents, um por página
    return docs

def chunk_documents(docs, chunk_size=1200, chunk_overlap=200):
    """Quebra documentos em chunks com índices para rastreabilidade."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(docs)

def build_vectorstore(chunks):
    """Gera embeddings e constrói um FAISS local."""
    embedder = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vs = FAISS.from_documents(chunks, embedder)
    return vs

def make_retriever(vs, k=6):
    """Cria um retriever (Top-k) em cima do índice FAISS."""
    return vs.as_retriever(search_kwargs={"k": k})

def build_llm(model_name: str = "gpt-4o-mini", temperature: float = 0.2):
    """Instancia o LLM. Padrão: OpenAI (gpt-4o-mini)."""
    # Vai ler OPENAI_API_KEY do ambiente
    return ChatOpenAI(model=model_name, temperature=temperature)

def format_docs(docs: List) -> str:
    """Concatena chunks em um único contexto com metadados de página/índice."""
    out = []
    for i, d in enumerate(docs, start=1):
        page = d.metadata.get("page", "NA")
        start = d.metadata.get("start_index", "NA")
        out.append(f"[Chunk {i} | page {page} | start {start}]\n{d.page_content}")
    return "\n\n".join(out)

def build_summary_chain(llm):
    """
    Cadeia LCEL:
      input: {"question": ..., "context": ...}
      output: resposta/summary focado na pergunta, citando apenas o contexto.
    """
    system_msg = (
        "Você é um assistente que responde SOMENTE com base no CONTEXTO fornecido.\n"
        "Se algo não estiver no contexto, diga que não há evidências no material recuperado.\n"
        "Produza um resumo claro, fiel e objetivo, e destaque os pontos-chave.\n"
        "Idioma: português."
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_msg),
            (
                "human",
                "Pergunta do usuário:\n{question}\n\n"
                "Contexto (chunks recuperados do PDF):\n{context}\n\n"
                "Instruções:\n"
                "- Faça um resumo focado na pergunta acima, citando apenas o contexto.\n"
                "- Liste tópicos-chave em bullet points.\n"
                "- Se houver limitações, seja explícito.\n"
            ),
        ]
    )

    chain = (
        {"question": RunnablePassthrough(), "context": RunnablePassthrough()}
        | prompt
        | llm
    )
    return chain

def query_and_summarize(pdf_path: str, question: str, k: int = 6):
    """Executa todo o pipeline de recuperação e resumo de um PDF com LangChain."""

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF não encontrado: {pdf_path}")

    # 1) PDF -> docs
    docs = load_pdf_docs(pdf_path)

    # 2) chunking
    chunks = chunk_documents(docs)

    # 3) embeddings + index
    vs = build_vectorstore(chunks)

    # 4) retrieval
    retriever = make_retriever(vs, k=k)
    relevant_docs = retriever.invoke(question)

    # 5) summary via LLM baseado APENAS nos chunks recuperados
    llm = build_llm()
    chain = build_summary_chain(llm)
    context_text = format_docs(relevant_docs)

    # Executa a cadeia:
    resp = chain.invoke({"question": question, "context": context_text})

    summary = resp.content if hasattr(resp, "content") else str(resp)

    return {
        "matches": relevant_docs,
        "summary": summary,
    }