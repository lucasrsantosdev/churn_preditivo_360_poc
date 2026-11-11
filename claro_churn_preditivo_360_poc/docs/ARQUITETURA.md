# Arquitetura lógica — POC v0.1

```text
       GERADOR 100% SINTETICO
            |     |      |
    clientes   eventos   externos ficticios
                 |
                 v
    RAW: CSV originais + manifest.json
                 |
                 v
    BRONZE: normalizacao de tipos, datas e duplicidade exata
                 |
                 v
    SILVER: jornada_eventos (pagamento, atendimento, consumo)
                 |
                 v
    GOLD: cliente x data de corte, agregacao temporal exata
          e alvo somente do mes seguinte
                 |
                 v
    Treino <= JUL/2026 | Validacao AGO/2026 | Teste SET/2026
                 |
        +--------+--------+
        |                 |
  Baseline LR        XGBoost
        +--------+--------+
                 |
    Selecao por AP na validacao
                 |
      Platt no conjunto AGO/26
                 |
    +------------+-------------+
    |            |             |
 Prob total   Prob parcial  Evidencias de contrapeso
    |            |             |
    +------------+-------------+
                 |
   CSV | metricas | SHAP | PNG | painel HTML
```

Este Medallion e **logico e local** (pastas de CSV); OCI e uma plataforma de nuvem da Oracle e **nao e** a arquitetura de camadas. Nao ha acesso Oracle, OCI, Glue ou Databricks nesta etapa.

## Contrato minimo para futuras fontes

Todos os eventos exigem `cliente_id` pseudonimizado, `data_evento` (horario e fuso se disponivel), categoria/origem e identificador de evento imutavel. Contratos exigem `contrato_id`, `produto`, `data_inicio` e historico da `data_fim`. Valores financeiros exigem semantica de data de corte, emissao, vencimento, efetivacao e estorno. A localizacao externa fica restrita a agregados regionais. Eventos de churn precisam diferenciar total, parcial e reversao.

## Limitações deliberadas

- O simulador usa uma distribucao arbitraria e assume dados completos.
- Granularidade atual dos snapshots: **mensal**.
- Inclui janela de observacao de 180 dias e tambem historico anterior para obter varios meses de treino.
- Treino usa varias observacoes por cliente; o teste futuro e uma separacao **temporal**, nao um estudo causal.
- A avaliacao de realismo, vieses, estabilidade, drift, policy e seguranca depende de dados autorizados.
- Dois classificadores binarios independentes sao experimentais; em dados reais pode ser preferivel um classificador multinomial calibrado ou modelos de sobrevivencia/risco concorrente.
