"""Evidencias interpretaveis independentes da probabilidade estatistica."""
import pandas as pd


def explicar_contrapesos(df: pd.DataFrame) -> pd.DataFrame:
    """Regras exploratorias sem peso estatistico; nao recalibra o modelo.

    Retorna evidencias de pressao, protecao e um balanco NAO probabilistico.
    """
    saida = df.copy()
    ris = []
    prot = []
    for r in saida.itertuples(index=False):
        negativos = []
        positivos = []
        if r.val_divida_net_m0 > max(150, 1.5 * r.valor_mensal_plano):
            negativos.append("divida_acumulada")
        if r.qtd_atrasos_180d >= 3:
            negativos.append("atrasos_recorrentes")
        if r.qtd_reclamacao_180d >= 3:
            negativos.append("reclamacoes_repetidas")
        if r.qtd_atendimentos_nao_resolvidos_180d >= 2:
            negativos.append("atendimentos_nao_resolvidos")
        if r.variacao_consumo_3m < -0.30:
            negativos.append("queda_de_consumo")
        if r.incidentes_rede_regiao >= 3:
            negativos.append("incidentes_regionais_de_rede")
        if r.qtd_pag_sem_atraso_90d >= 2 and r.qtd_atrasos_180d <= 1:
            positivos.append("pagamentos_recentes_em_dia")
        if r.taxa_resolucao_180d >= 0.85 and r.qtd_reclamacao_180d > 0:
            positivos.append("atendimento_geralmente_resolutivo")
        if r.val_divida_net_m0 < max(50, 0.25 * r.valor_mensal_plano):
            positivos.append("divida_baixa")
        if r.variacao_consumo_3m > -0.05:
            positivos.append("consumo_estavel_ou_em_alta")
        ris.append(negativos)
        prot.append(positivos)
    saida["evidencias_pressao"] = ["; ".join(x) or "nenhuma_regra_acionada" for x in ris]
    saida["evidencias_protecao"] = ["; ".join(x) or "nenhuma_regra_acionada" for x in prot]
    saida["qtd_evidencias_pressao"] = [len(x) for x in ris]
    saida["qtd_evidencias_protecao"] = [len(x) for x in prot]
    saida["balanco_evidencias_nao_probabilistico"] = (
        saida["qtd_evidencias_pressao"] - saida["qtd_evidencias_protecao"]
    )
    return saida
