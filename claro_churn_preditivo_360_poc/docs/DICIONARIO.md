# Dicionario — Gold snapshots v0.1

**Unidade de observação:** cliente sintético × último dia de cada mês.

| Campo | Significado | Origem |
|---|---|---|
| `cliente_id` | Chave anonimizada fictícia | Clientes |
| `data_corte` | Data da fotografia, não data do churn | Gold |
| `tempo_relacionamento_meses` | Meses desde entrada | Clientes |
| `qtd_contratos_ativos` | Contratos ativos no corte | Contratos |
| `valor_mensal_plano` | Soma mensal dos planos ativos | Contratos |
| `val_divida_net_m0` | Último saldo da dívida conhecido até o corte | Pagamentos |
| `val_pagamento_net_m0` | Último pagamento conhecido até o corte | Pagamentos |
| `qtd_pag_ultimos_60d` | Registros de pagamento nos últimos 60 dias | Pagamentos |
| `qtd_pag_sem_atraso_90d` | Pagamentos sem atraso nos últimos 90 dias | Pagamentos |
| `qtd_atrasos_180d` | Eventos de pagamento com dias de atraso positivos | Pagamentos |
| `max_dias_atraso_180d` | Maior atraso observado na janela | Pagamentos |
| `razao_pago_devido_180d` | Pago/faturado na janela | Pagamentos |
| `qtd_reclamacao_180d` | Reclamações registradas | Atendimento |
| `qtd_ura_180d` | Interações URA inbound/outbound | Atendimento |
| `qtd_visita_tecnica_180d` | Visitas técnicas | Atendimento |
| `qtd_atendimentos_nao_resolvidos_180d` | Interações sem resolução | Atendimento |
| `taxa_resolucao_180d` | Fração de atendimentos resolvidos; 0,5 sem observação | Atendimento |
| `qtd_migracoes_180d` | Migrações de plano simuladas | Consumo |
| `consumo_gb_ultimo_mes` | Último consumo medido | Consumo |
| `variacao_consumo_3m` | Mudança entre primeiro e último registro em até 4 meses | Consumo |
| `qtd_contatos_app_180d` | Contatos pelo app ou site | Atendimento |
| `indice_pressao_economica` | Indicador contextual **fictício** regional | Externo sintético |
| `indice_eventos_climaticos` | Indicador climático **fictício** regional | Externo sintético |
| `indice_concorrencia` | Proxy competitivo **fictício** regional | Externo sintético |
| `incidentes_rede_regiao` | Incidentes simulados na região/mês | Rede sintética |
| `target_tipo_churn` | `NENHUM`, `TOTAL` ou `PARCIAL` no mês seguinte | Apenas label |
| `target_churn_total` | 1 se houve cancelamento total no mês seguinte | Apenas label |
| `target_churn_parcial` | 1 se houve cancelamento parcial no mês seguinte | Apenas label |
| `evidencias_pressao` | Nomes dos gatilhos de risco operacional (sem causalidade) | Contrapesos |
| `evidencias_protecao` | Sinais de estabilidade/recuperação | Contrapesos |
| `balanco_evidencias_nao_probabilistico` | Contagem de sinais negativos menos protetivos; **não é score de churn** | Contrapesos |

### Fonte e as datas

O simulador gera origens totalmente inventadas com marcadores `SIMULADOR_SEM_DADOS_REAIS`. Eventos posteriores ao corte são reservados exclusivamente à rotulagem e à conferência da POC. Falta de registro é interpretada com regra experimental; em integração real é indispensável distinguir ausente, não aplicável e zero.

### Classes dos notebooks de referência

Classes 1 e 2, `SEG_PURPLE`, e terminologias de contrato/parcial usadas nos prints **não foram automaticamente transportadas**. Este experimento define seu próprio alvo `TOTAL`/`PARCIAL`/`NENHUM`, pendente de alinhamento aos conceitos oficiais da operação.
