"""Modelagem temporal, calibracao de probabilidades e explicabilidade."""
import json
import warnings
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             precision_score, recall_score, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from .config import (GOLD, GRAFICOS, METRICAS, MODELOS, PREDICOES,
                     COLUNAS_FEATURES, DATA_CORTE_TESTE, DATA_VALIDACAO)
from .contrapesos import explicar_contrapesos


def _metricas(y, p):
    y = np.asarray(y, dtype=int)
    p = np.asarray(p, dtype=float)
    n_top = max(1, int(np.ceil(len(p) * 0.05)))
    indices = np.argsort(-p)[:n_top]
    prevalencia = float(y.mean())
    resultado = {
        "n": int(len(y)), "positivos": int(y.sum()),
        "prevalencia_real_sintetica": round(prevalencia, 6),
        "pr_auc_ap": round(float(average_precision_score(y, p)), 6) if y.sum() else None,
        "roc_auc": round(float(roc_auc_score(y, p)), 6) if len(np.unique(y)) == 2 else None,
        "brier": round(float(brier_score_loss(y, p)), 6),
        "precision_top_5pct": round(float(y[indices].mean()), 6),
        "recall_top_5pct": round(float(y[indices].sum() / y.sum()), 6) if y.sum() else None,
        "lift_top_5pct": round(float(y[indices].mean() / prevalencia), 6) if prevalencia else None,
    }
    return resultado


def _logit(p):
    p = np.clip(p, 1e-5, 1 - 1e-5)
    return np.log(p / (1 - p)).reshape(-1, 1)


def _treinar_um_alvo(train, valid, teste, alvo, apelido):
    x_train, y_train = train[COLUNAS_FEATURES], train[alvo].astype(int)
    x_valid, y_valid = valid[COLUNAS_FEATURES], valid[alvo].astype(int)
    x_test, y_test = teste[COLUNAS_FEATURES], teste[alvo].astype(int)
    if len(y_train.unique()) < 2:
        raise ValueError(f"Sem exemplos suficientes para treinar {apelido}")
    baseline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("classificador", LogisticRegression(max_iter=550, class_weight="balanced", random_state=42)),
    ])
    xgb = XGBClassifier(n_estimators=160, max_depth=3, learning_rate=0.055,
                        subsample=0.85, colsample_bytree=0.90, min_child_weight=8,
                        objective="binary:logistic", eval_metric="logloss",
                        tree_method="hist", n_jobs=2, random_state=42)
    baseline.fit(x_train, y_train)
    xgb.fit(x_train, y_train)
    p_base_valid = baseline.predict_proba(x_valid)[:, 1]
    p_xgb_valid = xgb.predict_proba(x_valid)[:, 1]
    ap_base = average_precision_score(y_valid, p_base_valid)
    ap_xgb = average_precision_score(y_valid, p_xgb_valid)
    if ap_xgb >= ap_base:
        escolhido, modelo, pred_valid, nome = "XGBoost", xgb, p_xgb_valid, "XGBoost"
    else:
        escolhido, modelo, pred_valid, nome = "RegressaoLogistica", baseline, p_base_valid, "RegressaoLogistica"

    # Platt sigmoid treinado EXCLUSIVAMENTE no periodo de validacao (agosto).
    # Nao usa labels de outubro para ajustar parametros ou calibrar.
    calibrador = None
    if int(y_valid.sum()) >= 8 and int((1 - y_valid).sum()) >= 8:
        calibrador = LogisticRegression(random_state=42, max_iter=350)
        calibrador.fit(_logit(pred_valid), y_valid)
    bruto_teste = modelo.predict_proba(x_test)[:, 1]
    p_teste = (calibrador.predict_proba(_logit(bruto_teste))[:, 1]
               if calibrador is not None else bruto_teste)
    resultado = {
        "alvo": apelido, "modelo_escolhido": escolhido,
        "criterio_escolha": "maior average precision na validacao agosto/2026",
        "calibracao": "Platt sigmoid / agosto 2026" if calibrador is not None else "nao aplicada (poucos exemplos)",
        "validacao_baseline": _metricas(y_valid, p_base_valid),
        "validacao_xgboost": _metricas(y_valid, p_xgb_valid),
        "teste_outubro": _metricas(y_test, p_teste),
    }
    joblib.dump({"modelo": modelo, "calibrador": calibrador, "features": COLUNAS_FEATURES,
                 "data_treino_limite": "2026-07-31", "data_validacao": DATA_VALIDACAO},
                MODELOS / f"modelo_{apelido}.joblib")
    return p_teste, resultado, modelo, xgb


def _explicar_modelo(modelo, X, apelido):
    """SHAP, ou contribuicao log-odds de regressao logistica padronizada."""
    sample = X.iloc[:min(len(X), 180)].copy()
    origem = ""
    try:
        if isinstance(modelo, XGBClassifier):
            import shap
            exp = shap.TreeExplainer(modelo)
            valores = np.asarray(exp.shap_values(sample))
            origem = "SHAP TreeExplainer, escala de log-odds; NAO causal"
        else:
            scale = modelo.named_steps["scaler"]
            imp = modelo.named_steps["imputer"]
            coef = modelo.named_steps["classificador"].coef_[0]
            valores = scale.transform(imp.transform(sample)) * coef
            origem = "contribuicao linear em log-odds; NAO SHAP"
        if valores.ndim != 2 or valores.shape[1] != len(COLUNAS_FEATURES):
            raise ValueError("Dimensoes inesperadas de explicacao")
        importante = pd.DataFrame({"variavel": COLUNAS_FEATURES,
                                   "media_absoluta_contribuicao": np.abs(valores).mean(axis=0),
                                   "metodo": origem}).sort_values("media_absoluta_contribuicao", ascending=False)
        importante.to_csv(METRICAS / f"importancia_{apelido}.csv", index=False, encoding="utf-8-sig")
        individuais = []
        for i in range(min(15, len(sample))):
            ranks = np.argsort(-np.abs(valores[i]))[:5]
            for idx in ranks:
                individuais.append({"cliente_id": sample.index[i], "variavel": COLUNAS_FEATURES[idx],
                                    "contribuicao_log_odds": float(valores[i, idx]),
                                    "metodo": origem})
        pd.DataFrame(individuais).to_csv(METRICAS / f"explicacoes_individuais_{apelido}.csv",
                                             index=False, encoding="utf-8-sig")
        top = importante.head(12).iloc[::-1]
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(top["variavel"], top["media_absoluta_contribuicao"])
        ax.set_title(f"Importancia de variaveis | churn {apelido} | dados sinteticos")
        ax.set_xlabel("Media da contribuicao absoluta no score (log-odds)")
        fig.tight_layout()
        fig.savefig(GRAFICOS / f"importancia_{apelido}.png", dpi=135)
        plt.close(fig)
        return origem
    except Exception as exc:
        warnings.warn(f"Explicabilidade {apelido} indisponivel: {exc}")
        return f"falha na explicacao: {exc}"


def _plotar_calibracao(y, p, apelido):
    # Decis a partir de p; pode haver decis vazios, especialmente em amostras pequenas.
    d = pd.DataFrame({"y": y, "p": p}).copy()
    d["decil"] = pd.qcut(d["p"].rank(method="first"), q=10, labels=False, duplicates="drop")
    ag = d.groupby("decil")[["y", "p"]].mean()
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1, label="ideal")
    ax.plot(ag["p"], ag["y"], marker="o", label="POC sintetica")
    ax.set(xlabel="Probabilidade prevista (media do grupo)",
           ylabel="Churn observado (media do grupo)",
           title=f"Calibracao | churn {apelido} | outubro/2026")
    ax.legend()
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(GRAFICOS / f"calibracao_{apelido}.png", dpi=135)
    plt.close(fig)


def treinar_e_avaliar():
    for path in (MODELOS, METRICAS, PREDICOES, GRAFICOS):
        path.mkdir(parents=True, exist_ok=True)
    caminho = GOLD / "snapshots_modelagem.csv"
    if not caminho.exists():
        raise FileNotFoundError("Execute primeiro: python -m churn360.cli preparar")
    dados = pd.read_csv(caminho)
    treino = dados[dados["data_corte"] < DATA_VALIDACAO].copy()
    valid = dados[dados["data_corte"] == DATA_VALIDACAO].copy()
    teste = dados[dados["data_corte"] == DATA_CORTE_TESTE].copy()
    if min(len(treino), len(valid), len(teste)) == 0:
        raise ValueError("Janelas de treinamento/validacao/teste incompletas")
    previsoes = teste[["cliente_id", "regiao", "data_corte", "target_tipo_churn"] + COLUNAS_FEATURES].copy()
    previsoes = previsoes.rename(columns={"target_tipo_churn": "desfecho_real_SINTETICO_outubro"})
    metricas = {"dados": "100% SINTETICOS", "aviso": "Nao sao metricas de clientes reais da Claro.",
                "treino_ate": "2026-07-31", "validacao": "2026-08-31",
                "teste_snapshot": DATA_CORTE_TESTE, "teste_desfecho": "outubro/2026",
                "amostras": {"treino": len(treino), "validacao": len(valid), "teste": len(teste)}}
    for alvo, apelido in [("target_churn_total", "total"), ("target_churn_parcial", "parcial")]:
        prob, res, modelo, modelo_xgb = _treinar_um_alvo(treino, valid, teste, alvo, apelido)
        previsoes[f"prob_churn_{apelido}_30d"] = prob
        metricas[apelido] = res
        _plotar_calibracao(teste[alvo].values, prob, apelido)
        # Explicacao para amostra de maior risco, preservando identidade local.
        amostra = teste.assign(_prob=prob).sort_values("_prob", ascending=False).head(180).set_index("cliente_id")
        metodo = _explicar_modelo(modelo, amostra[COLUNAS_FEATURES], apelido)
        metricas[apelido]["explicabilidade"] = metodo
        # Mesmo se a regressao logistica vencer na validacao, manter SHAP
        # do XGBoost de referencia separado, sem atribuir SHAP ao baseline.
        if not isinstance(modelo, XGBClassifier):
            metodo_ref = _explicar_modelo(modelo_xgb, amostra[COLUNAS_FEATURES],
                                         f"{apelido}_xgboost_referencia")
            metricas[apelido]["shap_xgboost_referencia"] = metodo_ref

    # Como sao dois eventos mutuamente exclusivos, evitamos soma > 1.
    # A renormalizacao so e aplicada em linhas que excedem 100%.
    soma = previsoes["prob_churn_total_30d"] + previsoes["prob_churn_parcial_30d"]
    excesso = soma > 1
    if excesso.any():
        previsoes.loc[excesso, "prob_churn_total_30d"] /= soma[excesso]
        previsoes.loc[excesso, "prob_churn_parcial_30d"] /= soma[excesso]
        metricas["nota_probabilidades"] = f"Renormalizadas {int(excesso.sum())} linhas de classe exclusiva."
    else:
        metricas["nota_probabilidades"] = "Nenhuma renormalizacao necessaria."
    previsoes["prob_sem_churn_30d"] = (1 - previsoes["prob_churn_total_30d"] -
                                        previsoes["prob_churn_parcial_30d"]).clip(lower=0)

    previsoes = explicar_contrapesos(previsoes)
    pct = previsoes["prob_churn_total_30d"].rank(pct=True)
    previsoes["faixa_priorizacao"] = np.select(
        [pct >= .95, pct >= .85], ["TOP_5_PCT", "TOP_15_PCT"], default="DEMAIS")
    previsoes["encaminhamento_exploratorio"] = np.select(
        [(previsoes["faixa_priorizacao"] == "TOP_5_PCT") &
         (previsoes["qtd_evidencias_pressao"] > 0),
         (previsoes["faixa_priorizacao"] == "TOP_15_PCT")],
        ["REVISAR_CASO_E_JORNADA_COM_ANALISTA", "AVALIAR_ACOMPANHAMENTO"],
        default="SEM_ACAO_AUTOMATICA")
    previsoes = previsoes.sort_values("prob_churn_total_30d", ascending=False)
    previsoes.to_csv(PREDICOES / "previsoes_outubro_2026_SINTETICAS.csv", index=False, encoding="utf-8-sig")
    (METRICAS / "metricas_experimento.json").write_text(
        json.dumps(metricas, indent=2, ensure_ascii=False), encoding="utf-8")
    return metricas
