import pandas as pd
from churn360.contrapesos import explicar_contrapesos


def test_contrapeso_nao_altera_probabilidade():
    x = pd.DataFrame([{
        "val_divida_net_m0": 400, "valor_mensal_plano": 100,
        "qtd_atrasos_180d": 4, "qtd_reclamacao_180d": 3,
        "qtd_atendimentos_nao_resolvidos_180d": 2,
        "variacao_consumo_3m": -0.5, "incidentes_rede_regiao": 4,
        "qtd_pag_sem_atraso_90d": 0, "taxa_resolucao_180d": 0.2,
        "prob_churn_total_30d": 0.32,
    }])
    y = explicar_contrapesos(x)
    assert y.iloc[0]["qtd_evidencias_pressao"] == 6
    assert y.iloc[0]["prob_churn_total_30d"] == 0.32
    assert "divida_acumulada" in y.iloc[0]["evidencias_pressao"]
