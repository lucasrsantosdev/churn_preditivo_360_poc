# CLARO | FICHA TÉCNICA E CHECKLIST DE RASTREABILIDADE DO ESTUDO

> **Finalidade:** registrar, acompanhar e contar a história completa de um estudo analítico, validação de hipótese, análise exploratória, experimento ou POC, desde a solicitação até a publicação no Git.
>
> **Instrução de uso:** manter este arquivo na raiz da pasta do estudo, preferencialmente como `FICHA_TECNICA.md`, e atualizar os itens ao longo da execução. Marcar `[x]` somente quando houver evidência ou link correspondente.

---

## 0. Controle do documento

| Campo | Preenchimento |
|---|---|
| ID da solicitação | SOL-0001 |
| Título do estudo | |
| Tipo | Estudo / EDA / Validação de hipótese / POC / Modelo / Outro |
| Área solicitante | |
| Solicitante | |
| Responsável técnico | |
| Participantes | |
| Data da solicitação | AAAA-MM-DD |
| Data de início | AAAA-MM-DD |
| Prazo desejado | AAAA-MM-DD |
| Data de conclusão | AAAA-MM-DD |
| Status atual | Não iniciado / Levantamento / Desenvolvimento / Validação / Concluído / Bloqueado / Cancelado |
| Versão da ficha | 1.0 |
| Última atualização | AAAA-MM-DD |
| Repositório | |
| Pasta de evidências | |

### Histórico de atualizações

| Data | Responsável | Etapa/status | Alteração ou avanço | Evidência/commit |
|---|---|---|---|---|
| | | | | |

---

# PARTE 1 | SOLICITAÇÃO E CONTEXTO

## 1. Cenário e motivação

**O que está acontecendo no negócio e por que surgiu a necessidade?**

> Preencher.

## 2. Problema ou oportunidade

**Qual dor, comportamento, anomalia ou oportunidade precisa ser compreendida?**

> Preencher.

## 3. Pergunta principal

**Qual pergunta o estudo deverá responder?**

> Preencher em formato objetivo e verificável.

### Perguntas secundárias

1. 
2. 
3. 

## 4. Hipóteses

| ID | Hipótese | Evidência esperada | Método de validação | Critério de decisão | Resultado |
|---|---|---|---|---|---|
| H1 | | | | | Pendente / Confirmada / Refutada / Inconclusiva |

> Registrar hipóteses como suposições testáveis, nunca como fatos.

## 5. Escopo

### Dentro do escopo

- 

### Fora do escopo

- 

### Restrições, premissas e dependências

- **Restrições:**
- **Premissas:**
- **Dependências:**
- **Acessos necessários:**

## 6. Resultado esperado

- [ ] Relatório analítico
- [ ] Base consolidada
- [ ] Dashboard ou gráficos
- [ ] Notebook de análise
- [ ] Modelo estatístico ou preditivo
- [ ] POC funcional
- [ ] Apresentação executiva
- [ ] Parecer técnico
- [ ] Outro: 

**Como saberemos que a solicitação foi atendida?**

> Definir critérios objetivos de aceite.

---

# PARTE 2 | PLANO DE INVESTIGAÇÃO

## 7. Bases, fontes e ativos de dados

| ID | Sistema/fonte | Base/tabela/arquivo | Ambiente | Período | Granularidade | Chave de junção | Responsável | Classificação/acesso | Status |
|---|---|---|---|---|---|---|---|---|---|
| D1 | | | Dev/Hml/Prod | | | | | | Pendente/Disponível/Validada |

### Checklist de dados

- [ ] Fontes e tabelas identificadas
- [ ] Permissões de acesso confirmadas
- [ ] Período e recorte definidos
- [ ] Chaves de relacionamento validadas
- [ ] Dicionário de dados localizado ou criado
- [ ] Dados sensíveis identificados e tratados
- [ ] Regras de retenção e compartilhamento verificadas
- [ ] Qualidade inicial avaliada
- [ ] Ausências, duplicidades e inconsistências registradas
- [ ] Versão ou data de extração registrada

## 8. Extrações e consultas

| ID | Finalidade | Tecnologia | Arquivo/query | Fonte/tabela | Parâmetros | Saída gerada | Responsável | Última execução |
|---|---|---|---|---|---|---|---|---|
| Q1 | | SQL/Python/Spark/etc. | `src/...` | | | `data/...` | | |

### Regras para consultas

- [ ] Queries salvas em arquivos versionados
- [ ] Queries comentadas e com finalidade descrita
- [ ] Filtros de período e população explicitados
- [ ] Parâmetros configuráveis, sem valores ocultos
- [ ] Credenciais e segredos fora do código
- [ ] Resultado reproduzível a partir das fontes declaradas
- [ ] Custo e desempenho avaliados quando aplicável

## 9. Preparação e qualidade dos dados

| Regra/checagem | Campo/base | Método | Resultado | Tratamento aplicado | Evidência |
|---|---|---|---|---|---|
| Nulos | | | | | |
| Duplicidades | | | | | |
| Integridade de chaves | | | | | |
| Valores fora do domínio | | | | | |
| Cobertura temporal | | | | | |
| Viés de seleção | | | | | |

### Transformações principais

| Etapa | Entrada | Transformação/regra | Saída | Código responsável |
|---|---|---|---|---|
| T1 | | | | `src/...` |

## 10. Métricas e indicadores

| Métrica | Definição de negócio | Fórmula | Unidade | Fonte | Recorte/dimensão | Validação |
|---|---|---|---|---|---|---|
| | | | | | | |

- [ ] Definições alinhadas com a área solicitante
- [ ] Fórmulas documentadas
- [ ] Denominadores e populações explicitados
- [ ] Regras de arredondamento e tratamento definidas
- [ ] Números reconciliados com fonte de referência, quando houver

## 11. Metodologia analítica

| Item | Definição |
|---|---|
| Abordagem | Descritiva / Diagnóstica / Inferencial / Preditiva / Causal / Experimento |
| Método principal | |
| População e amostra | |
| Variáveis explicativas | |
| Variável-alvo | |
| Segmentações | |
| Estratégia de treino/teste | |
| Baseline | |
| Critério de sucesso | |
| Limitações previstas | |

### Validação de hipótese ou teste estatístico

| Hipótese | Teste/método | H0 | H1 | Nível de significância | Poder/amostra | Resultado | Interpretação |
|---|---|---|---|---|---|---|---|
| H1 | | | | | | | |

### Modelo, quando aplicável

| Item | Registro |
|---|---|
| Algoritmo e versão | |
| Features utilizadas | |
| Hiperparâmetros | |
| Métricas de avaliação | |
| Baseline comparativo | |
| Estratégia de validação | Holdout / Cross-validation / Temporal |
| Artefato do modelo | |
| Seed | |
| Riscos de viés/fairness | |
| Explicabilidade | |

- [ ] Baseline definido
- [ ] Separação entre treino, validação e teste documentada
- [ ] Vazamento de dados verificado
- [ ] Métricas adequadas ao problema selecionadas
- [ ] Robustez por período e segmento avaliada
- [ ] Erros e casos extremos analisados
- [ ] Limitações do modelo registradas

## 12. Ambiente e reprodutibilidade

| Item | Registro |
|---|---|
| Linguagem e versão | Python / R / SQL / Outro |
| Bibliotecas principais | |
| Arquivo de dependências | `requirements.txt`, `pyproject.toml`, `environment.yml` |
| Plataforma de execução | Local / Databricks / Fabric / Outro |
| Kernel/runtime | |
| Configurações | |
| Commit/tag reproduzível | |

### Checklist técnico

- [ ] Estrutura de pastas criada
- [ ] Ambiente e dependências registrados
- [ ] Código modularizado quando necessário
- [ ] Notebooks sem saídas sensíveis
- [ ] Caminhos e parâmetros externalizados
- [ ] Logs e tratamento de erros implementados quando aplicável
- [ ] Execução ponta a ponta testada
- [ ] Dados ou amostra permitida disponíveis para reprodução

---

# PARTE 3 | ACOMPANHAMENTO DA EXECUÇÃO

## 13. Plano de trabalho

| Etapa | Entrega/evidência | Responsável | Início | Prazo | Status | Bloqueio |
|---|---|---|---|---|---|---|
| Entendimento | | | | | | |
| Dados | | | | | | |
| Análise/POC | | | | | | |
| Validação | | | | | | |
| Documentação | | | | | | |
| Publicação | | | | | | |

## 14. Diário de decisões e descobertas

| Data | Tipo | Registro | Impacto no estudo | Responsável | Evidência |
|---|---|---|---|---|---|
| | Decisão/Descoberta/Risco/Bloqueio | | | | |

## 15. Riscos, bloqueios e pendências

| ID | Tipo | Descrição | Impacto | Ação de mitigação | Responsável | Prazo | Status |
|---|---|---|---|---|---|---|---|
| R1 | Risco/Bloqueio/Pendência | | | | | | |

---

# PARTE 4 | RESULTADOS E VALIDAÇÃO

## 16. Descobertas

| ID | Descoberta | Evidência/valor | Hipótese relacionada | Relevância | Link |
|---|---|---|---|---|---|
| F1 | | | H1 | | |

## 17. Resultado das hipóteses

| Hipótese | Resultado | Evidências favoráveis | Evidências contrárias | Limitações | Decisão |
|---|---|---|---|---|---|
| H1 | Confirmada/Refutada/Inconclusiva | | | | |

## 18. Validação técnica e de negócio

| Validação | Critério | Resultado | Validador | Data | Evidência |
|---|---|---|---|---|---|
| Dados | | | | | |
| Método | | | | | |
| Resultado | | | | | |
| Negócio | | | | | |

- [ ] Resultados revisados tecnicamente
- [ ] Resultados validados pela área solicitante
- [ ] Critérios de aceite atendidos
- [ ] Divergências e ressalvas registradas
- [ ] Evidências verificáveis vinculadas
- [ ] Conclusões distinguem correlação, associação e causalidade

## 19. O que os dados nos contaram

**Resumo dos principais resultados:**

> Preencher com números, segmentos, períodos e comparações relevantes.

**O que isso significa para a Claro?**

> Registrar impacto potencial no cliente, operação, receita, eficiência, risco ou experiência.

**Limitações e o que não pode ser concluído:**

> Preencher.

## 20. Recomendação e próximos passos

| Prioridade | Recomendação/ação | Justificativa | Responsável sugerido | Prazo | Dependência |
|---|---|---|---|---|---|
| Alta/Média/Baixa | | | | | |

---

# PARTE 5 | PUBLICAÇÃO E RASTREABILIDADE NO GIT

## 21. Estrutura recomendada do repositório

```text
estudo-ou-poc/
├── README.md
├── FICHA_TECNICA.md
├── requirements.txt ou pyproject.toml
├── config/
├── data/
│   ├── README.md
│   ├── raw/          # não versionar dados restritos
│   ├── interim/
│   └── processed/
├── notebooks/
├── sql/
├── src/
├── tests/
├── outputs/
│   ├── figures/
│   ├── tables/
│   └── reports/
└── docs/
    ├── dicionario_dados.md
    └── evidencias/
```

## 22. Inventário de artefatos

| Tipo | Nome | Caminho/link | Finalidade | Versão/commit | Responsável |
|---|---|---|---|---|---|
| README | | `README.md` | Visão geral e execução | | |
| Ficha | | `FICHA_TECNICA.md` | Rastreabilidade | | |
| Notebook | | `notebooks/...` | | | |
| Query | | `sql/...` | | | |
| Código Python | | `src/...` | | | |
| Base/dataset | | | | | |
| Modelo | | | | | |
| Gráfico/relatório | | `outputs/...` | | | |

## 23. Checklist antes do commit/publicação

### Conteúdo

- [ ] README explica contexto, objetivo e pergunta principal
- [ ] Ficha técnica atualizada
- [ ] Fontes, tabelas e período documentados
- [ ] Queries SQL incluídas e referenciadas
- [ ] Scripts e notebooks Python incluídos e organizados
- [ ] Metodologia, métricas e critérios de validação descritos
- [ ] Resultados e limitações registrados
- [ ] Próximos passos e responsáveis indicados

### Segurança e conformidade

- [ ] Nenhuma credencial, token ou senha no repositório
- [ ] Nenhum dado pessoal ou sensível publicado indevidamente
- [ ] `.gitignore` revisado
- [ ] Arquivos grandes ou bases brutas tratados conforme política aplicável
- [ ] Nomes de clientes e identificadores anonimizados quando necessário
- [ ] Permissões do repositório revisadas

### Qualidade e reprodução

- [ ] Código executa sem dependências não declaradas
- [ ] Ordem de execução documentada
- [ ] Parâmetros e configurações descritos
- [ ] Resultados principais podem ser reproduzidos
- [ ] Links internos funcionam
- [ ] Revisão técnica concluída
- [ ] Aprovação do negócio registrada
- [ ] Commit final e tag/release criados, quando aplicável

## 24. Matriz de rastreabilidade

| Requisito/pergunta | Base/fonte | Query/código | Método | Evidência/resultado | Conclusão/recomendação |
|---|---|---|---|---|---|
| Pergunta principal | D1 | Q1 / `src/...` | | F1 | |
| H1 | | | | | |

> Esta matriz é o índice central do estudo: deve permitir navegar da pergunta até a fonte, o processamento, a evidência e a conclusão.

---

# PARTE 6 | ENCERRAMENTO

## 25. Conclusão executiva

> Resumir em um parágrafo: problema investigado, abordagem, principal resultado, relevância para a Claro e ação recomendada.

## 26. Situação final

| Campo | Registro |
|---|---|
| Situação | Concluído / Parcial / Inconclusivo / Cancelado |
| Critério de aceite atendido? | Sim / Parcial / Não |
| Data de encerramento | |
| Solicitante/validador | |
| Responsável técnico | |
| Link do repositório | |
| Commit/tag final | |
| Link das evidências | |
| Nova demanda necessária? | |

## 27. Aprovações

| Papel | Nome | Decisão | Data | Observação/evidência |
|---|---|---|---|---|
| Responsável técnico | | Aprovado/Pendente | | |
| Solicitante/negócio | | Aprovado/Pendente | | |
| Revisor técnico | | Aprovado/Pendente | | |

---

## Critério de completude da ficha

A ficha é considerada completa quando:

- [ ] A pergunta principal e as hipóteses estão registradas
- [ ] Cada fonte de dados possui identificação e período
- [ ] Cada resultado relevante aponta para query, código ou evidência
- [ ] O método e os critérios de validação estão descritos
- [ ] As hipóteses possuem resultado e justificativa
- [ ] Limitações e riscos estão explícitos
- [ ] O README e o repositório permitem reproduzir ou compreender o estudo
- [ ] A validação técnica e de negócio está registrada
- [ ] A conclusão executiva e os próximos passos foram preenchidos

---

_Claro | Dados & Analytics — Documento de solicitação, acompanhamento e rastreabilidade de estudos, análises e POCs._
