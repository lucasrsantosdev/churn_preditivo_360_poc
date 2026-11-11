from churn360.config import COLUNAS_FEATURES, DATA_CORTE_TESTE


def test_feature_sem_target_ou_identificador():
    assert len(COLUNAS_FEATURES) == len(set(COLUNAS_FEATURES))
    assert not any("target" in c or "churn" in c or "cliente_id" in c
                   for c in COLUNAS_FEATURES)
    assert DATA_CORTE_TESTE == "2026-09-30"
