"""RAW -> BRONZE -> SILVER -> GOLD, com isolamento temporal dos alvos."""
import json
import shutil
from datetime import timedelta

import numpy as np
import pandas as pd

from .config import (RAW, BRONZE, SILVER, GOLD, DATA_CORTE_TESTE,
                     COLUNAS_FEATURES)

FONTE_DATAS = {
    "clientes.csv": ["data_entrada"],
    "contratos.csv": ["data_inicio", "data_fim"],
    "pagamentos.csv": ["data_evento"],
    "atendimentos.csv": ["data_evento"],
    "consumo.csv": ["data_evento"],
    "contexto_externo.csv": ["data_publicacao"],
    "rede.csv": ["data_evento"],
    "churn_eventos.csv": ["data_evento"],
}


def _load(csv, root=BRONZE):
    return pd.read_csv(root / csv, parse_dates=FONTE_DATAS[csv], keep_default_na=True)


def _assign_series(base, series, coluna, fill=0):
    if series is None or len(series) == 0:
        base[coluna] = fill
    else:
        base[coluna] = base["cliente_id"].map(series).fillna(fill)


def preparar_camadas():
    if not (RAW / "manifest.json").exists():
        raise FileNotFoundError("Execute primeiro o gerador de dados sinteticos.")
    for caminho in (BRONZE, SILVER, GOLD):
        caminho.mkdir(parents=True, exist_ok=True)

    for arquivo, colunas in FONTE_DATAS.items():
        df = pd.read_csv(RAW / arquivo)
        for nome in colunas:
            df[nome] = pd.to_datetime(df[nome], errors="coerce")
        # Normalizacao sem alterar o RAW. Nao removemos eventos repetidos
        # legitimamente: protocolo e data sao importantes para auditoria.
        df = df.drop_duplicates()
        for nome in colunas:
            df[nome] = df[nome].dt.strftime("%Y-%m-%d")
        df.to_csv(BRONZE / arquivo, index=False, encoding="utf-8-sig")

    clientes = _load("clientes.csv")
    contratos = _load("contratos.csv")
    pagamentos = _load("pagamentos.csv")
    contatos = _load("atendimentos.csv")
    consumo = _load("consumo.csv")
    externo = _load("contexto_externo.csv")
    rede = _load("rede.csv")
    churn = _load("churn_eventos.csv")

    # SILVER: linha de eventos audivel; CHURN nao aparece na jornada para
    # nao tornar a data do cancelamento um preditor do passado.
    eventos = []
    for colunas, origem, tipo in [
        (["cliente_id", "data_evento", "valor_pago", "valor_divida_net"], pagamentos, "PAGAMENTO"),
        (["cliente_id", "data_evento", "canal", "motivo", "resolvido"], contatos, "ATENDIMENTO"),
        (["cliente_id", "data_evento", "consumo_gb", "houve_migracao"], consumo, "CONSUMO"),
    ]:
        ev = origem[colunas].copy()
        ev["tipo_evento"] = tipo
        eventos.append(ev)
    jornada = pd.concat(eventos, ignore_index=True, sort=False).sort_values(["cliente_id", "data_evento"])
    jornada["data_evento"] = jornada["data_evento"].dt.strftime("%Y-%m-%d")
    jornada.to_csv(SILVER / "jornada_eventos.csv", index=False, encoding="utf-8-sig")

    # Snapshots mensais 2025-07..2026-09; janelas EXATAS de 180/90/60 dias.
    cortes = pd.date_range("2025-07-31", DATA_CORTE_TESTE, freq="ME")
    frames = []
    for corte in cortes:
        ini180 = corte - timedelta(days=179)
        ini90 = corte - timedelta(days=89)
        ini60 = corte - timedelta(days=59)
        fim_target = corte + pd.offsets.MonthEnd(1)
        base = clientes.loc[clientes["data_entrada"] <= corte,
                            ["cliente_id", "regiao", "data_entrada"]].copy()
        # Clientes com churn TOTAL anterior ao corte nao sao elegiveis.
        ja_cancelou = set(churn.loc[(churn["data_evento"] <= corte) &
                                       (churn["tipo_churn"] == "TOTAL"), "cliente_id"])
        base = base.loc[~base["cliente_id"].isin(ja_cancelou)].copy()
        if base.empty:
            continue
        base["data_corte"] = corte.strftime("%Y-%m-%d")
        base["tempo_relacionamento_meses"] = ((corte - base["data_entrada"]).dt.days / 30.44).round(1)
        ct = contratos.loc[(contratos["data_inicio"] <= corte) &
                           (contratos["data_fim"].isna() | (contratos["data_fim"] > corte))]
        agc = ct.groupby("cliente_id").agg(qtd_contratos_ativos=("contrato_id", "count"),
                                            valor_mensal_plano=("valor_plano", "sum"))
        base = base.join(agc, on="cliente_id")
        base = base.loc[base["qtd_contratos_ativos"].notna()].copy()

        p = pagamentos.loc[(pagamentos["data_evento"] >= ini180) &
                           (pagamentos["data_evento"] <= corte)].copy()
        p90 = p[p["data_evento"] >= ini90]
        p60 = p[p["data_evento"] >= ini60]
        pagg = p.groupby("cliente_id")
        _assign_series(base, pagg["dias_atraso"].apply(lambda v: (v > 0).sum()), "qtd_atrasos_180d")
        _assign_series(base, pagg["dias_atraso"].max(), "max_dias_atraso_180d")
        _assign_series(base, p60.groupby("cliente_id")["valor_pago"].count(), "qtd_pag_ultimos_60d")
        _assign_series(base, p90.groupby("cliente_id")["dias_atraso"].apply(lambda v: (v == 0).sum()), "qtd_pag_sem_atraso_90d")
        valor_sum = pagg[["valor_pago", "valor_fatura"]].sum()
        percentual = (valor_sum["valor_pago"] / valor_sum["valor_fatura"].clip(lower=1)).clip(0, 1.5)
        _assign_series(base, percentual, "razao_pago_devido_180d")
        latest_p = p.sort_values("data_evento").drop_duplicates("cliente_id", keep="last").set_index("cliente_id")
        _assign_series(base, latest_p["valor_divida_net"], "val_divida_net_m0")
        _assign_series(base, latest_p["valor_pago"], "val_pagamento_net_m0")

        a = contatos.loc[(contatos["data_evento"] >= ini180) &
                         (contatos["data_evento"] <= corte)].copy()
        aa = a.groupby("cliente_id")
        _assign_series(base, aa["reclamacao"].sum(), "qtd_reclamacao_180d")
        _assign_series(base, aa["canal"].apply(lambda v: v.isin(["URA_INBOUND", "URA_OUTBOUND"]).sum()), "qtd_ura_180d")
        _assign_series(base, aa["canal"].apply(lambda v: (v == "VISITA_TECNICA").sum()), "qtd_visita_tecnica_180d")
        _assign_series(base, aa["resolvido"].apply(lambda v: (v == 0).sum()), "qtd_atendimentos_nao_resolvidos_180d")
        _assign_series(base, aa["resolvido"].mean(), "taxa_resolucao_180d", fill=0.5)
        _assign_series(base, aa["canal"].apply(lambda v: v.isin(["APP", "SITE"]).sum()), "qtd_contatos_app_180d")

        c = consumo.loc[(consumo["data_evento"] >= ini180) & (consumo["data_evento"] <= corte)].copy()
        _assign_series(base, c.groupby("cliente_id")["houve_migracao"].sum(), "qtd_migracoes_180d")
        latest_c = c.sort_values("data_evento").drop_duplicates("cliente_id", keep="last").set_index("cliente_id")
        _assign_series(base, latest_c["consumo_gb"], "consumo_gb_ultimo_mes")
        tres = consumo.loc[(consumo["data_evento"] <= corte) &
                           (consumo["data_evento"] >= corte - pd.DateOffset(months=4))]
        hist = tres.sort_values("data_evento").groupby("cliente_id")["consumo_gb"].agg(["first", "last", "count"])
        delta = ((hist["last"] - hist["first"]) / hist["first"].clip(lower=0.1)).clip(-1.0, 3.0)
        delta = delta.where(hist["count"] >= 3, 0.0)
        _assign_series(base, delta, "variacao_consumo_3m")

        # Externos SOMENTE publicados ou registrados ate a data de corte.
        ext = externo.loc[(externo["data_publicacao"] <= corte) &
                          (externo["mes_referencia"] == corte.strftime("%Y-%m"))]
        base = base.merge(ext[["regiao", "indice_pressao_economica",
                               "indice_eventos_climaticos", "indice_concorrencia"]],
                          on="regiao", how="left", validate="many_to_one")
        rd = rede.loc[(rede["data_evento"] <= corte) &
                      (rede["mes_referencia"] == corte.strftime("%Y-%m"))]
        base = base.merge(rd[["regiao", "incidentes_rede_regiao"]], on="regiao", how="left", validate="many_to_one")

        futuros = churn.loc[(churn["data_evento"] > corte) &
                            (churn["data_evento"] <= fim_target), ["cliente_id", "tipo_churn"]]
        t = futuros.drop_duplicates("cliente_id", keep="first").set_index("cliente_id")["tipo_churn"]
        base["target_tipo_churn"] = base["cliente_id"].map(t).fillna("NENHUM")
        base["target_churn_total"] = (base["target_tipo_churn"] == "TOTAL").astype(int)
        base["target_churn_parcial"] = (base["target_tipo_churn"] == "PARCIAL").astype(int)
        base["janela_inicio_180d"] = ini180.strftime("%Y-%m-%d")
        base["janela_fim_target"] = fim_target.strftime("%Y-%m-%d")
        base["origem_dados"] = "SIMULADA"
        for col in COLUNAS_FEATURES:
            if col not in base:
                raise ValueError(f"Feature obrigatoria ausente: {col}")
            base[col] = pd.to_numeric(base[col], errors="coerce").fillna(0)
        frames.append(base.drop(columns=["data_entrada"]))

    gold = pd.concat(frames, ignore_index=True)
    gold = gold.sort_values(["data_corte", "cliente_id"]).reset_index(drop=True)
    if gold["data_corte"].max() != DATA_CORTE_TESTE:
        raise AssertionError("Data de corte final divergente!")
    if (gold["target_churn_total"] + gold["target_churn_parcial"] > 1).any():
        raise AssertionError("Rotulo total e parcial mutuamente exclusivos.")
    gold.to_csv(GOLD / "snapshots_modelagem.csv", index=False, encoding="utf-8-sig")
    gold[gold["data_corte"] == DATA_CORTE_TESTE].to_csv(
        GOLD / "coorte_outubro_2026.csv", index=False, encoding="utf-8-sig")
    detalhes = {
        "data_corte_teste": DATA_CORTE_TESTE,
        "datas_corte_disponiveis": list(gold["data_corte"].unique()),
        "snapshots": len(gold),
        "clientes_coorte_outubro": len(gold[gold["data_corte"] == DATA_CORTE_TESTE]),
        "colunas_features": COLUNAS_FEATURES,
        "garantia_temporal": "Somente eventos <= data_corte; target em mes seguinte."
    }
    (GOLD / "metadados.json").write_text(json.dumps(detalhes, ensure_ascii=False, indent=2), encoding="utf-8")
    return detalhes
