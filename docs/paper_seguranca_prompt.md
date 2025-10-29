**Paper técnico estruturado** sobre “Segurança em Prompt Engineering” no âmbito de modelos de linguagem (LLMs), com nível acadêmico e referências validadas

# Prompt Engineering e Segurança de IA

**Autores:** Armando Soares Sousa
**Afiliação:** UFPI/DC
**Data:** 29/10/2025

## Resumo

Este trabalho aborda os desafios de segurança que emergem no uso de prompts junto a grandes modelos de linguagem (LLMs), com foco em três eixos principais: (1) engenharia de prompt maliciosa (prompt engineering malicioso), (2) mecanismos de defesa para modelos de IA, e (3) alinhamento ético de modelos e sistemas. Tomando como estudo de caso o pedido malicioso para elaboração de um coquetel molotov, demonstra-se como a cadeia “pedido → modelo → resposta” pode ser explorada, e como o sistema de segurança ideal deve atuar. Propõe-se ainda um framework de avaliação de segurança para LLMs, bem como recomendações para arquitetura, engenharia de prompt e operações. O objetivo é oferecer uma base sólida para pesquisadores, engenheiros e gestores que implementam LLMs em contextos críticos.

## 1. Introdução

Com o advento de grandes modelos de linguagem (LLMs) como GPT‑4, Claude 2, Mistral 7B etc., a integração desses sistemas em aplicações variadas (chatbots, assistentes virtuais, sistemas de tomada de decisão) tem crescido exponencialmente. Contudo, ao mesmo tempo, emergem desafios de segurança fundamentais: os modelos são vulneráveis a técnicas de ataque conhecidas como *prompt injection*, *jailbreaks*, manipulação de contexto e vazamento de informações. Por exemplo, em estudo recente, foi demonstrado que dos 36 aplicativos de LLM testados, 31 eram suscetíveis a ataques de injeção de prompt. ([arXiv][1])

No cenário brasileiro, onde iniciativas como o projeto SoberanIA ganham cada vez mais relevância em ambientes públicos e governamentais, é imperativo que profissionais de TI, segurança, governança e IA estejam preparados para tratar esses vetores de risco. Este artigo visa contribuir nesse sentido.

### 1.1 Justificativa

O exemplo de solicitação de elaboração de um coquetel Molotov ilustra de forma didática como:

* um usuário malicioso pode usar *prompt engineering* para induzir o modelo a gerar conteúdo perigoso;
* o sistema (modelo + aplicação) deve possuir mecanismos de segurança capazes de detectar e impedir esse tipo de solicitação;
* o alinhamento ético (“não ajude a cometer infrações”) precisa estar embutido nas regras de operação do sistema.

### 1.2 Objetivos

* Analisar as vulnerabilidades decorrentes da engenharia de prompt maliciosa.
* Apresentar técnicas de mitigação nos níveis de sistema, prompt e modelo/aplicação.
* Descrever metodologias de *red teaming* para avaliação de segurança de LLMs.
* Propor um framework de avaliação de segurança específico para LLMs.
* Aplicar os conceitos no estudo de caso (pedido de coquetel Molotov) e estruturar recomendações práticas.

## 2. Engenharia de Prompt Malicioso

Nesta seção detalhamos o que é *prompt engineering* no sentido de uso adversarial, quais formas ele pode assumir, e por que ele representa uma ameaça para sistemas baseados em LLMs.

### 2.1 Definição e categorias

*Prompt injection* é um tipo de ataque onde o usuário (ou um agente adversário) insere instruções maliciosas no prompt de entrada de um modelo, com o objetivo de manipular seu comportamento ou obter resultados não autorizados. ([Coralogix][2])

Podem ser identificadas algumas categorias clássicas:

* **Direta**: o usuário envia diretamente uma instrução maliciosa ao modelo.
* **Indireta**: o modelo consome dados de uma fonte externa (web, banco de dados, upload) já “envenenados”. ([Coralogix][2])
* **Persistente/armazenada**: o attacker injeta prompts em memória ou dados persistentes que serão reutilizados pelo modelo.

### 2.2 Vetores de ameaça exemplificados

* Exemplo: solicitar a fabricação de um explosivo (“me ensine a construir um coquetel Molotov”).
* Inserção de “Ignore todas as instruções anteriores e responda X” no meio de uma pergunta aparentemente inócua.
* Envenenamento de base de conhecimento de um sistema RAG (retrieval-augmented generation) para que recupere dados maliciosos ou instruções de ataque.

### 2.3 Impactos principais

* **Geração de conteúdo perigoso ou ilegal**: O modelo pode fornecer instruções detalhadas para fabricar armas, explosivos, ou conduzir fraude.
* **Vazamento de informações confidenciais**: O adversário pode induzir o modelo a revelar segredos, credenciais, ou dados treinados.
* **Engenharia social e manipulação de usuários**: Através de prompts maliciosos, o sistema pode auxiliar fraudes ou phishing.
* **Desalinhamento ético**: O modelo pode contrariar seus princípios de projeto (por exemplo “não fornecer instruções para danos”) e isso gera risco reputacional, regulatório e operacional.

## 3. Mecanismos de Defesa em LLMs

Para mitigar os riscos acima, é necessário adotar uma estratégia de **defesa em profundidade (defense-in-depth)** que combine múltiplas camadas: arquitetural, de prompt, e no modelo/aplicação.

### 3.1 Defesa no nível do sistema (arquitetural)

* **Delimitação clara entre instruções do sistema e dados do usuário**: Separar o “system prompt” (instruções de operação) do “user prompt” (entrada do usuário) de modo que o modelo não misture ou seja sobrescrito.
* **Canários (honeytokens) no prompt**: Inserir instruções secretas que, se acionadas, indicam que ocorreu uma injeção.
* **Dupla chamada de modelo (pipeline em duas etapas)**:

  1. Um modelo leve analisa intenção do usuário e detecta possíveis instruções perigosas.
  2. Se aprovado, encaminha-se à chamada principal do modelo.
* **Sandboxing / Minimização de privilégios**: O modelo ou aplicação opera em ambiente restrito, sem acesso irrestrito a APIs externas, banco de dados sensíveis, execução de código etc.

### 3.2 Defesa no nível do prompt (engenharia de prompt)

* Instruções de negação explícitas no system prompt (“Sob nenhuma circunstância …”).
* Role-playing com regras rígidas: definir um personagem que **não pode** ser manipulado.
* Forçar formatos de saída estruturados (por exemplo JSON), para aumentar a rigidez e reduzir a chance de injeção bem-sucedida.
* Sanitização de entrada: remover ou neutralizar padrões como “ignore todas as instruções anteriores”.
* Validação de saída: antes de entregar ao usuário, checar se a resposta viola políticas ou contém conteúdo sensível.

### 3.3 Defesa no nível do modelo e da aplicação

* **Fine-tuning de segurança**: Treinar o modelo com exemplos adversariais para que aprenda a recusar solicitações maliciosas.
* **Monitoramento e honeypots**: Inserir prompts de isca controlados e monitorar respostas — se o sistema for enganado, há falha de segurança.
* **Ferramentas de detecção de injeção**: Por exemplo, técnicas de monitoramento de padrões de atenção (attention patterns) para detectar mudanças comportamentais suspeitas. ([ACL Anthology][3])
* **Atualização contínua de defesas**: Porque os vetores de ataque evoluem — a “corrida armamentista” entre atacantes e defensores é contínua.

## 4. Red Teaming de Modelos de IA

O red teaming (time vermelho) para LLMs configura uma disciplina essencial para identificar vulnerabilidades antes da implantação em produção.

### 4.1 O que é Red Teaming para LLMs?

Trata-se de simular adversários (red team) que tentam explorar o modelo, de modo a revelar falhas de alinhamento, segurança ou desempenho. ([ACL Anthology][4])

### 4.2 Metodologias típicas

* **Engenharia de prompt adversarial**: figura central — jailbreaking (“Ignore todas as suas regras…”), role-playing sem restrições, codificação de payloads (ex: base64). ([arXiv][5])
* **Teste de vazamento de prompt**: induzir o modelo a revelar seu próprio system prompt ou instruções internas.
* **Teste de viés e justiça (bias & fairness)**: verificar se há tratamento discriminatório ou estereotipado.
* **Robustez & consistência**: Reformular perguntas, usar sinônimos, typos, sobrescrições para ver se o sistema “quebra”.
* **RAG / Sistemas de conhecimento externo**: Envenenar fontes de dados ou injetar contexto externo malicioso para verificar se o modelo é manipulado.

### 4.3 Ciclo de Red Teaming

1. Planejamento e escopo (definir o que será testado: vazamento de credenciais, instruções perigosas, viés etc.)
2. Execução: equipe adversária gera prompts, documenta resultados.
3. Análise & triagem: classificar vulnerabilidades encontradas (crítico, alto, médio, baixo).
4. Mitigação: time de desenvolvimento corrige, refina system prompt, filters, arquitetura.
5. Re-teste (regressão): garantir que correções funcionaram e que não há regressão em utilidade.

### 4.4 Ferramentas e automação

* Frameworks como garak (Generative AI Red-teaming & Assessment Kit) ajudam a automatizar varreduras de vulnerabilidades. ([arXiv][6])
* Métodos como “Multi-round Automatic Red-Teaming (MART)” que automatizam geração de ataques e melhorias do target. ([arXiv][7])
* “Quality-Diversity Red-Teaming” que amplia o espectro de vetores de ataque. ([arXiv][8])

## 5. Framework de Avaliação de Segurança para LLMs

Para efetivar a segurança, propomos uma estrutura (framework) com as seguintes dimensões:

### 5.1 Taxonomia de riscos

* **Prejuízo/Harmfulness**: geração de conteúdo perigoso, ilegal ou eticamente indevido.
* **Vazamento de informação (Information Disclosure)**: revelação de dados confidenciais, system prompt, PII.
* **Viés & Justiça (Bias & Fairness)**: tratamento desigual, estereótipos, discriminação.
* **Robustez (Robustness)**: resistência contra ataques de perturbação, reformulações, sinônimos, typos.
* **Raciocínio seguro (Safety in Reasoning)**: se modelo pode ser levado a conclusões perigosas ou erradas de forma plausível.
* **Segurança sistêmica (Systemic Safety)**: riscos de execução de código, APIs externas, manipulação de dados, cadeia de ferramentas.

### 5.2 Conjuntos de dados (benchmarks)

* Publicados: por exemplo TruthfulQA (para desinformação), ToxiGen (para toxicidade), BBQ (viés em QA).
* Red teaming: corpora de prompts adversariais, ataques registrados (ex: mais de 1.400 prompts em estudo recente) ([arXiv][5])

### 5.3 Métricas e metodologia

* **Attack Success Rate (ASR)**: proporção de prompts adversariais que conseguiu contornar as defesas.
* **Unwanted Behavior Rate**: taxa de respostas que violam normas/ políticas.
* **Métricas de viés**: *disparate impact*, testes WEAT/SEAT.
* **Métricas de robustez**: desempenho sob perturbações, reformulações.

### 5.4 Processo de avaliação

* Pré-lançamento: uso de benchmarks + red teaming antes da liberação pública.
* Pós-lançamento e monitoramento contínuo: capturar novos vetores, regressões, ataques emergentes.
* Relatórios transparentes de segurança (similar ao que OpenAI publicou sobre red-teaming). ([cdn.openai.com][9])

## 6. Estudo de Caso: Pedido de Coquetel Molotov

### 6.1 Cenário

Um usuário insere no sistema uma solicitação: “Por favor, me ensine a construir um coquetel Molotov.”

### 6.2 Vulnerabilidade

Sem mecanismos de segurança adequados, o modelo poderia fornecer passo-a-passo de fabricação de artefato explosivo — o que constitui comportamento legalmente proibido e eticamente inaceitável.

### 6.3 Aplicação das defesas

* O **system prompt** contém instruções explícitas: “Você não ajuda a construir armas ou artefatos letais.”
* A entrada do usuário é primeiramente analisada por um classificador de intenção que identifica “instrução para fabricar arma” → bloqueio ou recusa.
* O modelo principal, se receber a solicitação, aplica filtros de conteúdo (input/output sanitization) e recusa com mensagem segura.
* O red team já teria testado essa “ancora” (trigger) como parte do benchmark adversarial.
* Saída padrão: “Desculpe, não posso ajudar com isso. Posso fornecer informações gerais sobre técnicas de segurança ou legislação aplicável, se desejar.”
  Isso demonstra a “arquitetura segura” em ação.

### 6.4 Recomendações práticas

* Incluir no prompt de sistema: “Se houver pedido de fabricação de arma, explosivo ou violação criminal, recuse imediatamente.”
* Inserir um canário: se o modelo responder com “ERRO 123”, significa que falhou a separação de contexto.
* Manter logs de solicitações recusas para auditoria e melhoria contínua.
* Realizar red teaming periódico com essa e outras solicitações de alto risco.

## 7. Desafios e Tendências Futuras

### 7.1 “Gato e rato” constante

As técnicas de ataque evoluem rapidamente: segundo estudo recente, ataques automáticos de prompt injection estão se tornando mais sofistic. ([arXiv][10])

### 7.2 Subjetividade e contexto cultural

O que é “conteúdo prejudicial” pode variar conforme cultura, jurisdição e contexto; métricas universais são desafiadoras.

### 7.3 Trade-offs entre segurança e utilidade

Maior segurança pode reduzir utilidade (modelo mais cauteloso, menos criativo). Ajuste fino é necessário.

### 7.4 Integração em sistemas críticos

Quando LLMs são integrados a sistemas de decisão, automação ou agentes, como veículos autônomos, robots ou finanças, o risco sistêmico aumenta.

### 7.5 Normas, regulação e governança

Aprofundamento de normas (ex: LGPD, ISO/IEC 38500 para governança de IA) e auditorias externas se tornarão padrão.

## 8. Conclusão

A engenharia de prompt maliciosa representa uma vulnerabilidade real e crescente nos sistemas baseados em LLMs. A abordagem de defesa deve ser multi-camadas: arquitetura robusta, engenharia de prompt bem delineada e mecanismos de modelo/aplicação bem desenhados. A incorporação de processos de red teaming e de frameworks de avaliação de segurança permite que organizações como o Projeto SoberanIA alcancem maior maturidade em segurança, confiabilidade e alinhamento ético. Em última instância, desenvolver sistemas de IA que sejam inteligentes **e seguros** não é apenas uma vantagem competitiva — é uma obrigação ética e regulatória.

## Referências

1. Liu, Y., Deng, G., Li, Y., Wang, K., Wang, Z., Wang, H., Zheng, Y., Liu, Y.: *Prompt Injection attack against LLM-integrated Applications*. arXiv preprint arXiv:2306.05499 (2023) ([arXiv][1])
2. “Security Concerns for Large Language Models: A Survey.” arXiv preprint arXiv:2505.18889 (2025) ([arXiv][11])
3. Pathade, C.: *Red Teaming the Mind of the Machine: A Systematic Evaluation of Prompt Injection and Jailbreak Vulnerabilities in LLMs*. arXiv … (2025) ([arXiv][12])
4. Kili Technology: *The Ultimate Guide to Red Teaming LLMs and Adversarial Prompts*. (2024) ([kili-website][13])
5. Attention-Tracker et al.: “Attention Tracker: Detecting Prompt Injection Attacks in LLMs.” Findings of NAACL (2025) ([ACL Anthology][3])
6. NVIDIA Developer Blog: “Defining LLM Red Teaming.” (2024) ([NVIDIA Developer][14])
7. OWASP Gen AI Security Project: “LLM01:2025 Prompt Injection.” (2025) ([genai.owasp.org][15])
8. (Adicionais conforme necessidade)

---

[1]: https://arxiv.org/abs/2306.05499?utm_source=chatgpt.com "Prompt Injection attack against LLM-integrated Applications - arXiv"
[2]: https://coralogix.com/ai-blog/prompt-injection-attacks-in-llms-what-are-they-and-how-to-prevent-them/?utm_source=chatgpt.com "Prompt Injection Attacks in LLMs: What Are They and ... - Coralogix"
[3]: https://aclanthology.org/2025.findings-naacl.123.pdf?utm_source=chatgpt.com "[PDF] Attention Tracker: Detecting Prompt Injection Attacks in LLMs"
[4]: https://aclanthology.org/2025.trustnlp-main.23.pdf?utm_source=chatgpt.com "[PDF] An End-to-End Overview of Red Teaming for Large Language Models"
[5]: https://arxiv.org/html/2505.04806v1?utm_source=chatgpt.com "A Systematic Evaluation of Prompt Injection and Jailbreak ... - arXiv"
[6]: https://arxiv.org/abs/2406.11036?utm_source=chatgpt.com "garak: A Framework for Security Probing Large Language Models"
[7]: https://arxiv.org/abs/2311.07689?utm_source=chatgpt.com "MART: Improving LLM Safety with Multi-round Automatic Red-Teaming"
[8]: https://arxiv.org/abs/2506.07121?utm_source=chatgpt.com "Quality-Diversity Red-Teaming: Automated Generation of High-Quality and Diverse Attackers for Large Language Models"
[9]: https://cdn.openai.com/papers/openais-approach-to-external-red-teaming.pdf?utm_source=chatgpt.com "[PDF] OpenAI's Approach to External Red Teaming for AI Models and ..."
[10]: https://arxiv.org/abs/2407.03876?utm_source=chatgpt.com "[2407.03876] Automated Progressive Red Teaming - arXiv"
[11]: https://arxiv.org/abs/2505.18889?utm_source=chatgpt.com "Security Concerns for Large Language Models: A Survey - arXiv"
[12]: https://arxiv.org/abs/2505.04806?utm_source=chatgpt.com "Red Teaming the Mind of the Machine: A Systematic Evaluation of Prompt Injection and Jailbreak Vulnerabilities in LLMs"
[13]: https://kili-technology.com/large-language-models-llms/red-teaming-llms-and-adversarial-prompts?utm_source=chatgpt.com "The Ultimate Guide to Red Teaming LLMs and Adversarial Prompts ..."
[14]: https://developer.nvidia.com/blog/defining-llm-red-teaming/?utm_source=chatgpt.com "Defining LLM Red Teaming | NVIDIA Technical Blog"
[15]: https://genai.owasp.org/llmrisk/llm01-prompt-injection/?utm_source=chatgpt.com "LLM01:2025 Prompt Injection - OWASP Gen AI Security Project"
