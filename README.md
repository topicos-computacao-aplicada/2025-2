# Turma de Computação Aplicada 2025-2 (UFPI)

O objetivo deste curso é capacitar os alunos a conceber, arquitetar e implementar projetos de aplicações de IA Generativa em ambiente de computação em nuvem. Partindo dos fundamentos de Machine Learning, os alunos explorarão modelos generativos de mais recentes (como Large Language Models - LLMs) e seus padrões de aplicação. A disciplina aborda o ciclo de vida básico dessas soluções, priorizando o desenvolvimento, deployment e o monitoramento, de tais aplicações, utilizando serviços de cloud computing para hospedar a solução. Ao final, o aluno terá o embasamento necessário para entender e criar os principais componentes de uma solução de IA generativa robusta e escalável em um ambiente de nuvem.

## Machine Learning

**Machine Learning (Aprendizado de Máquina)** é um subcampo da Inteligência Artificial que confere aos computadores a capacidade de aprender padrões a partir de dados, sem serem explicitamente programados para cada tarefa. Em vez de seguir regras fixas, os algoritmos de ML identificam estruturas e relações em conjuntos de dados históricos para construir um **modelo**. Este modelo treinado é então capaz de generalizar seu conhecimento, realizando previsões, classificações ou tomando decisões inteligentes quando apresentado a informações novas e nunca vistas. Dessa forma, o foco muda da programação tradicional para o "treinamento" de sistemas, permitindo que eles melhorem seu desempenho automaticamente com a experiência fornecida pelos dados.

- [Modelo de Regressão Linear](notebooks/ML_Linear_Regressionn.ipynb)
- [Modelo de Clusterização](notebooks/ML_K_Means.ipynb)
  
## Deep Learning

**Deep Learning (Aprendizado Profundo)** é um subcampo especializado do Machine Learning inspirado na estrutura e função do cérebro humano, conhecida como redes neurais artificiais. O que o caracteriza é o uso de redes com muitas camadas intermediárias (daí o termo "profundo") entre a entrada e a saída de dados. Essas camadas permitem que o modelo aprenda hierarquias de características de forma automatizada e progressivamente mais abstrata. Por exemplo, em uma imagem, as primeiras camadas podem detectar bordas, as seguintes combinam essas bordas em formas, e as camadas finais identificam objetos complexos. Essa capacidade de aprender representações diretamente dos dados brutos (como pixels, texto ou áudio) torna o Deep Learning extremamente poderoso para tarefas complexas, sendo a base para os mais avançados modelos de IA Generativa, reconhecimento de imagem, processamento de linguagem natural e veículos autônomos.

Exemplo de Aplicação de Visão Computacional usando Deep Learning
- [Reconhecimento de imagens de cães e gatos](https://github.com/topicos-computacao-aplicada/2025-2/tree/main/cat_dog)
- [API de Manipulação do modelo cat_dogs_recognition](https://github.com/topicos-computacao-aplicada/2025-2/tree/main/api/api_cat_dog)

## IA Generativa

**IA Generativa** é um ramo da Inteligência Artificial que se concentra na criação de conteúdo novo e original, em vez de apenas analisar ou classificar informações existentes. Diferente de outros sistemas que fazem previsões, seu objetivo é gerar dados semelhantes aos que foi treinado. Utilizando modelos complexos, como Redes Adversariais Generativas (GANs) e Transformers, ela pode produzir textos, imagens, músicas, códigos e vídeos a partir de um comando (prompt). A base desse processo é aprender a distribuição de probabilidade subjacente a um conjunto de dados de treinamento para, então, amostrar novos elementos plausíveis a partir dela. Essa tecnologia é a força motriz por trás de ferramentas como ChatGPT, DALL-E e Midjourney, representando um avanço significativo na capacidade criativa das máquinas e abrindo novas fronteiras para a inovação em diversas indústrias.

- [Exemplo de pipeline de transcrição e tradução de música](notebooks/pipeline_traduz_musica_ingles_para_portugues.ipynb)
- [Exemplo simplificado de Chatbot integrado a API do Google Gemini](https://github.com/topicos-computacao-aplicada/2025-2/tree/main/gemini_chatbot)
- [Exemplo de Chatbot usando o Langchain](https://github.com/topicos-computacao-aplicada/2025-2/tree/main/gemini_chatbot_lm)

### Prompt Engineering

**Prompt Engineering** é a disciplina prática de projetar e refinar instruções (prompts) para guiar modelos de IA Generativa, especialmente modelos de linguagem, na produção de resultados desejados e de alta qualidade. Trata-se de uma forma de comunicação estruturada com a IA, onde a formulação, o contexto, a formatação e a inclusão de exemplos no prompt são cruciais para a precisão e relevância da resposta. Mais do que simplesmente fazer uma pergunta, envolve técnicas como especificar o formato de saída, definir um papel para o modelo (ex: "aja como um especialista"), e iterar com base nos resultados obtidos. Não é programação tradicional, mas uma habilidade fundamental para interagir de forma eficiente e confiável com essas ferramentas, extraindo seu máximo potencial e mitigando problemas como alucinações ou respostas genéricas. É, portanto, uma competência chave para a aplicação prática da IA no mundo real.

- [Fundamentos de Engenharia de Prompt](https://github.com/topicos-computacao-aplicada/2025-2/blob/main/docs/fundamentos_engenharia_prompt_llm.md)
- [Prompt de Sistema e Prompt de Usuário](https://github.com/topicos-computacao-aplicada/2025-2/blob/main/docs/system_prompt_user_prompt.md)
- [Segurança em Prompt Engineering](https://github.com/topicos-computacao-aplicada/2025-2/blob/main/docs/prompt.md)
- [Paper Técnico sobre Segurança de Prompt](https://github.com/topicos-computacao-aplicada/2025-2/blob/main/docs/paper_seguranca_prompt.md)

### RAG (Retrieval-Augmented Generation)

**RAG (Retrieval-Augmented Generation, ou Geração Aumentada por Recuperação)** é uma arquitetura avançada que combina um sistema de recuperação de informações com um modelo de linguagem generativa para melhorar a precisão e a factualidade de suas respostas. A inovação do RAG está em sua execução em duas etapas: primeiro, o sistema recupera documentos ou informações relevantes e atualizadas de uma fonte de conhecimento externa (como uma base de dados corporativa ou a web) com base na consulta do usuário. Em seguida, esse contexto específico e confiável é inserido como parte do prompt para o modelo generativo, que o utiliza para sintetizar uma resposta fundamentada. Essa abordagem mitiga um problema comum em LLMs puros: as "alucinações" ou a geração de informações inventadas. Ao ancorar a geração em fatos verificáveis, o RAG cria sistemas de IA mais confiáveis, contextuais e atualizáveis, sendo essencial para a construção de assistentes inteligentes e chatbots especializados em domínios específicos.

- [Fundamentos sobre RAG](https://github.com/topicos-computacao-aplicada/2025-2/blob/main/docs/rag_paper_tecnico.md)
- [Protótipo de App web com RAG](https://github.com/topicos-computacao-aplicada/2025-2/tree/main/web_rag_pdf)
- [Exemplo de aplicação RAG web](https://github.com/topicos-computacao-aplicada/2025-2/blob/main/docs/exemplo_web_rag.md)

### Agentes de IA

**Agentes de IA** são sistemas autônomos que percebem seu ambiente por meio de entradas (como um prompt, dados ou sensores), tomam decisões para atingir um objetivo específico e executam ações, muitas vezes utilizando ferramentas externas. Diferente de um modelo de IA generativa que apenas responde a uma única solicitação, um agente opera em um ciclo de raciocínio: ele planeja uma sequência de tarefas, pode usar ferramentas como motores de busca, APIs ou código para coletar informações e, então, age com base nesses resultados, iterando até concluir a meta. Esse poder de delegar e orquestrar tarefas complexas – como pesquisar, analisar e resumir um tópico – os torna extremamente versáteis. Eles representam um avanço em direção a uma inteligência mais geral, automatizando fluxos de trabalho complexos e agindo como assistentes proativos, capazes de resolver problemas de forma dinâmica e autoguiada.

- [Agente de Resumos de Arquivos .txt](https://github.com/topicos-computacao-aplicada/2025-2/tree/main/agente_simples)

## LangChain

**LangChain** é um framework de código aberto projetado para simplificar o desenvolvimento de aplicações sofisticadas usando modelos de linguagem grandes (LLMs). Seu principal objetivo é superar as limitações dos LLMs puros, como a falta de contexto atualizado e a incapacidade de interagir com sistemas externos. Para isso, o LangChain fornece componentes modulares que permitem conectar um modelo a fontes de dados externas (**Retrieval**), gerenciar memória entre interações (**Memory**) e encadear sequências de ações complexas por meio de ferramentas (**Agents**). Ele atua como um "cola" entre o modelo de IA, suas fontes de informação (como bancos de dados ou APIs) e a lógica da aplicação. Ao abstrair a complexidade inerente a essas integrações, o LangChain acelera a criação de sistemas poderosos e contextuais, como chatbots especializados, agentes autônomos e aplicações do tipo **RAG**, tornando-se uma ferramenta fundamental no ecossistema de IA Generativa.

- [Fundamentos do framework Langchain](https://github.com/topicos-computacao-aplicada/2025-2/blob/main/docs/relatorio_tecnico_langchain.md)
- [Comparando aplicações com APIs OpenAI/Google Gemini e Langchain](https://colab.research.google.com/drive/15YlPdwFjzYOjB-DuZNheM_CvXPpH8v1B?usp=sharing)
- [Exemplo de uso do Langchain para uma aplicação de IA Generativa](https://github.com/topicos-computacao-aplicada/2025-2/blob/main/docs/my_langchain.md)
- [Exemplo de resumo de pdf](https://github.com/topicos-computacao-aplicada/2025-2/tree/main/pdf_summarizer)


## Site da disciplina

Disponível em https://topicos-computacao-aplicada.github.io/github.io

Em caso de dúvidas entrar em contato com [Armando Soares Sousa](https://www.sigaa.ufpi.br/sigaa/public/docente/portal.jsf?siape=1886865) (responsável pela disciplina).
