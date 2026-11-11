from pathlib import Path

import pandas as pd
import pytest

from churn360.config import GOLD, RAW, DATA_CORTE_TESTE


def test_dataset_gold_se_gerado():
    arq = GOLD / "snapshots_modelagem.csv"
    if not arq.exists():
        pytest.skip("Execute python -m churn360.cli all para o teste de integracao")
    df = pd.read_csv(arq)
    assert df["data_corte"].max() == DATA_CORTE_TESTE
    assert (df["target_churn_total"] + df["target_churn_parcial"] <= 1).all()
    assert (pd.to_datetime(df["janela_inicio_180d"]) ==
            pd.to_datetime(df["data_corte"]) - pd.Timedelta(days=179)).all()
    assert df["cliente_id"].str.startswith("SYN_C").all()
    assert df["origem_dados"].eq("SIMULADA").all()


def test_origem_de_dados_nao_reais():
    manifest = RAW / "manifest.json"
    if not manifest.exists():
        pytest.skip("Execute primeiro o gerador")
    import json
    assert json.loads(manifest.read_text(encoding="utf-8"))["tipo"] == "100% SINTETICO"
