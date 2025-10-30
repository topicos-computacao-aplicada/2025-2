# Retrieval-Augmented Generation (RAG): fundamentos, arquiteturas e práticas de engenharia

## Resumo

Modelos de linguagem de larga escala (LLMs) apresentam limitações importantes em tarefas intensivas em conhecimento, como **factualidade**, **atualização** e **rastreabilidade das fontes**. **Retrieval-Augmented Generation (RAG)** aborda essas limitações ao integrar, na inferência, um mecanismo de **recuperação de passagens** relevantes a partir de corpora externos, que são então usados para **condicionar a geração**. Este artigo apresenta: (i) fundamentos e evolução do RAG, (ii) arquiteturas e componentes (retriever, indexador vetorial, gerador), (iii) boas práticas de engenharia (ingestão, chunking, embeddings, indexação, ranking e prompting), (iv) variações modernas (FiD, RETRO, Self-RAG), e (v) diretrizes de **avaliação** e **confiabilidade** (alucinações, segurança e monitoramento). Situamos o RAG na literatura seminal (REALM, DPR, RAG) e em pesquisas recentes (surveys e frameworks agentic), destacando trade-offs e recomendações para uso em produção. ([arXiv][1])

## 1. Introdução

LLMs armazenam conhecimento **paramétrico** em pesos, mas sua **capacidade de acessar, atualizar e justificar conhecimento** é limitada quando atuam isoladamente. Em tarefas de *open-domain QA* e outras aplicações intensivas em conhecimento, combinar um **mecanismo de busca não-paramétrica** com geração condicional provê ganhos de precisão e interpretabilidade. **RAG**, formalizado por Lewis et al. (2020), acopla um **retriever** (e um índice vetorial de passagens) a um **gerador seq2seq** (p. ex., T5/BART), afinados fim-a-fim. ([arXiv][2])

## 2. Fundamentos e trabalhos relacionados

* **REALM** introduz pretreinamento com recuperador latente, permitindo **retropropagação através da etapa de busca** e ganhos expressivos em *Open-QA*. ([arXiv][1])
* **DPR** demonstra que **representações densas** e um **dual-encoder** superam BM25 para recuperação de passagens em múltiplos *benchmarks*, estabelecendo a base prática do retriever denso no RAG. ([arXiv][3])
* **RAG (Lewis et al.)** combina DPR + gerador seq2seq; variantes **RAG-Token** e **RAG-Sequence** diferem em como condicionam a geração nas passagens. ([proceedings.neurips.cc][4])
* **FiD (Fusion-in-Decoder)** codifica passagens independentemente e as **funde** no decodificador, escalando para dezenas/centenas de passagens com forte desempenho. ([arXiv][5])
* **RETRO** condiciona um transformador autoregressivo em **trechos recuperados de um banco de 2 trilhões de tokens**, alcançando performance comparável a modelos paramétricos muito maiores, com **25× menos parâmetros**. ([Proceedings of Machine Learning Research][6])
* **Self-RAG** adiciona **autorreflexão e uso adaptativo de recuperação** (inclusive decidir **não** recuperar), com *reflection tokens* para controlar factualidade e citações. ([arXiv][7])
* **Pesquisas de síntese** (2024–2025) consolidam taxonomias, variações arquiteturais (retriever-centric, generator-centric, agentic) e **protocolos de avaliação** específicos para RAG. ([arXiv][8])

## 3. Arquitetura de referência

Um pipeline RAG em produção tipicamente segue:

1. **Ingestão & Normalização:** coleta (PDF, HTML, DOCX, CSV, APIs), limpeza e enriquecimento (metadados).
2. **Chunking & Anotação:** divisão em blocos semânticos (p. ex., 300–800 tokens) com sobreposição; *splits* por títulos e seções; *ids* estáveis.
3. **Embeddings & Indexação:** geração de embeddings (denso) e **construção de índice vetorial** (FAISS/Milvus/Weaviate/Chroma) com metadados para filtros.
4. **Consulta (Retrieval):** **re-ranqueamento híbrido** (denso + BM25) e *fusion* (p. ex., **Reciprocal Rank Fusion**); **K** passagens mais relevantes.
5. **Orquestração (Prompting):** empacotar pergunta + contexto (passagens) + instruções (formato de resposta, citações).
6. **Geração & Pós-processamento:** resposta condicionada; *post-hoc* para **citações verificáveis** e **verificadores de factualidade**.
7. **Observabilidade & Feedback:** telemetria de *hits*, latência, *drop-off*, qualidade percebida; *A/B* e *human-in-the-loop*.

A literatura base (REALM/DPR/RAG/FiD/RETRO) embasa as decisões de projeto acima: **busca diferenciável** (pré-treinável), **retrieval denso** superior a BM25, **fusão no decodificador** para agregar múltiplas passagens, e **condicionamento autoregressivo com memória externa** para reduzir dependência paramétrica. ([Proceedings of Machine Learning Research][9])

## 4. Componentes e variações

### 4.1 Recuperação

* **Denso (DPR/bi-encoder):** rápido, escalável, excelente *recall* inicial. ([arXiv][3])
* **Sparso (BM25):** forte baseline; útil em fusões híbridas (*BM25+denso*). (Resumo baseado na comparação em DPR.) ([arXiv][3])
* **Re-rankers cross-encoder:** melhor precisão no *top-k*, custo maior (aplicar após filtragem densa).

### 4.2 Geração condicionada

* **RAG-Seq/RAG-Token** (seq2seq + DPR). ([proceedings.neurips.cc][4])
* **FiD** (passagens → encoder; fusão no decoder). ([arXiv][5])
* **RETRO** (AR LM + condicionamento em vizinhos recuperados). ([Proceedings of Machine Learning Research][6])
* **Self-RAG** (recuperação sob demanda + autorreflexão). ([arXiv][7])

### 4.3 Indexadores vetoriais

Embora nem todos possuam artigo acadêmico, a engenharia com **FAISS/Milvus/Weaviate** é padrão de mercado para **MIPS** e índices HNSW/IVF-PQ, alinhado aos requisitos de latência/escala implicados por DPR/RETRO. (Inferência com base em RETRO e DPR.) ([arXiv][3])

## 5. Engenharia do pipeline RAG (práticas recomendadas)

* **Qualidade de contexto importa:** controle de tamanho e sobreposição de *chunks*; normalização de Unicode, figuras e tabelas; *dedup*. Estudos em FiD destacam a importância da **qualidade das passagens** usadas no *encoder*. ([arXiv][5])
* **Híbrido > único:** combinar **denso + BM25 + re-ranker** aumenta precisão sem perder escalabilidade (síntese da literatura DPR/FiD). ([arXiv][3])
* **Citações e verificabilidade:** projetar *prompting* e *post-processing* para **apontar fontes**; direção também difundida na prática industrial. ([TIME][10])
* **Atualização contínua:** rotinas de re-indexação e *freshness*, *canary indexes* e controle de versões do corpus.
* **Observabilidade:** logs de consultas, *recall@k*, *hit-rate*, tempo de recuperação e geração; *A/B* com anotações humanas. Pesquisas recentes reúnem **métricas e protocolos específicos para RAG**. ([arXiv][11])

## 6. Confiabilidade, alucinações e segurança

RAG **reduz a taxa de alucinações** ao **ancorar** a geração em evidências recuperadas, mas **não elimina** o problema; é necessário **detectar/mitigar**. *Surveys* recentes categorizam tipos de alucinação e estratégias de mitigação (p. ex., verificação de suporte, detecção por incerteza, *faithfulness metrics*). ([arXiv][12])
Abordagens como **Self-RAG** integram **críticas internas** e controle de comportamento via *reflection tokens*, melhorando factualidade e **acurácia de citações**. ([arXiv][7])
Adoção industrial ressalta que **RAG é uma resposta prática** ao problema — mas há **trade-offs** entre precisão e vulnerabilidades de *grounding* (p. ex., **prompt injection** no conteúdo recuperado). Cobertura jornalística técnica recente discute avanços e limitações. ([Financial Times][13])

## 7. Avaliação de sistemas RAG

A avaliação requer medir **recuperação**, **utilidade do contexto** e **qualidade da geração**:

* **Recuperação:** *Recall@k*, *MRR*, *nDCG*.
* **Geração:** *Exact Match*, *F1* (em QA), **factualidade/faithfulness** (com checadores automáticos ou humanos).
* **Fim-a-fim:** tempo total de resposta, taxa de citações válidas, *user-centric KPIs*.
  Pesquisas recentes consolidam **protocolos e *benchmarks* específicos para RAG** e discutem lacunas de avaliação (e.g., equilíbrio entre qualidade e eficiência). ([arXiv][11])

## 8. Cenários de uso (case patterns)

* **Assistentes corporativos**: bases internas com controle de acesso e trilhas de auditoria.
* **Suporte técnico/jurídico**: respostas com **proveniência** e **atualização**.
* **Pesquisa e relatórios**: *long-form generation* com **citações verificáveis**.
* **Educação e saúde**: respostas conservadoras com *abstention* quando o suporte é insuficiente.

## 9. Diretrizes para adoção em produção

1. **Defina corpus e governança** (fontes confiáveis, PII/LGPD, versionamento).
2. **Comece híbrido** (denso + BM25) e **meça** rigorosamente *recall/precision* do retriever. ([arXiv][3])
3. **Prototipe com FiD/RAG** e evolua para **RETRO** (quando texto longo autoregressivo + base massiva) ou **Self-RAG** (quando controle de factualidade/citação é crítico). ([arXiv][5])
4. **Implemente verificadores** (checar se a resposta é suportada pelas passagens) e **exija citações** em UX. ([arXiv][7])
5. **Monitore e re-indexe** continuamente; use *canaries* antes de realizar *roll-outs* completos. ([arXiv][11])

## 10. Conclusões

RAG consolidou-se como **padrão de mercado** e **fronteira acadêmica** para elevar a **factualidade** e a **rastreabilidade** de LLMs em tarefas intensivas em conhecimento. A evolução recente (FiD, RETRO, Self-RAG) amplia o espaço de projeto entre **eficiência**, **escala** e **controle de qualidade**; pesquisas de 2024–2025 oferecem **taxonomias e protocolos de avaliação** para amadurecer implantações em produção. O futuro imediato aponta para **RAG agentic** (recuperação iterativa, ferramentas, raciocínio) e **RAG multimodal**, com ênfase crescente em **segurança**, **confiabilidade** e **governança de dados**. ([arXiv][5])

---

## Referências (selecionadas)

* **Lewis et al. (2020)**. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS. ([proceedings.neurips.cc][4])
* **Karpukhin et al. (2020)**. *Dense Passage Retrieval for Open-Domain Question Answering*. EMNLP. ([arXiv][3])
* **Guu et al. (2020)**. *REALM: Retrieval-Augmented Language Model Pre-Training*. ICML. ([Proceedings of Machine Learning Research][9])
* **Izacard & Grave (2021/24)**. *Fusion-in-Decoder* e trabalhos correlatos sobre qualidade do contexto. ([arXiv][5])
* **Borgeaud et al. (2022)**. *RETRO: Improving Language Models by Retrieving from Trillions of Tokens*. ICML. ([Proceedings of Machine Learning Research][6])
* **Asai et al. (2023)**. *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*. ([arXiv][7])
* **Gupta et al. (2024)**. *A Comprehensive Survey of Retrieval-Augmented Generation*. ([arXiv][8])
* **Dang et al. (2025)**; **Huang et al. (2023)**; **Sahoo et al. (2024)**. *Surveys* sobre **alucinações** em LLMs e mitigação. ([Frontiers][14])
* **RAG em produção e citação de fontes** (perfil de Patrick Lewis e adoção industrial). ([TIME][10])
* **Avaliação de RAG** (survey 2025). ([arXiv][11])

---

[1]: https://arxiv.org/abs/2002.08909?utm_source=chatgpt.com "REALM: Retrieval-Augmented Language Model Pre-Training"
[2]: https://arxiv.org/abs/2005.11401?utm_source=chatgpt.com "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
[3]: https://arxiv.org/abs/2004.04906?utm_source=chatgpt.com "Dense Passage Retrieval for Open-Domain Question Answering"
[4]: https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf?utm_source=chatgpt.com "Retrieval-Augmented Generation for Knowledge-Intensive ..."
[5]: https://arxiv.org/html/2403.14197v1?utm_source=chatgpt.com "Context Quality Matters in Training Fusion-in-Decoder for ..."
[6]: https://proceedings.mlr.press/v162/borgeaud22a.html?utm_source=chatgpt.com "Improving Language Models by Retrieving from Trillions of ..."
[7]: https://arxiv.org/abs/2310.11511?utm_source=chatgpt.com "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection"
[8]: https://arxiv.org/abs/2410.12837?utm_source=chatgpt.com "[2410.12837] A Comprehensive Survey of Retrieval ..."
[9]: https://proceedings.mlr.press/v119/guu20a/guu20a.pdf?utm_source=chatgpt.com "REALM: Retrieval-Augmented Language Model Pre-Training"
[10]: https://time.com/7012883/patrick-lewis/?utm_source=chatgpt.com "Patrick Lewis"
[11]: https://arxiv.org/html/2504.14891v1?utm_source=chatgpt.com "Retrieval Augmented Generation Evaluation in the Era of ..."
[12]: https://arxiv.org/abs/2311.05232?utm_source=chatgpt.com "A Survey on Hallucination in Large Language Models"
[13]: https://www.ft.com/content/7a4e7eae-f004-486a-987f-4a2e4dbd34fb?utm_source=chatgpt.com "The 'hallucinations' that haunt AI: why chatbots struggle to tell the truth"
[14]: https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2025.1622292/full?utm_source=chatgpt.com "Survey and analysis of hallucinations in large language ..."
