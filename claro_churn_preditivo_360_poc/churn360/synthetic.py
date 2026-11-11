"""Gera dados 100% sinteticos; nenhum registro representa cliente real da Claro."""
import json
import calendar
from collections import defaultdict
from datetime import date

import numpy as np
import pandas as pd

from .config import RAW

REGIOES = ["SP_ABC", "SP_CAPITAL", "SP_CAMPINAS", "SP_BAIXADA", "SP_INTERIOR"]
CANAIS = ["URA_INBOUND", "URA_OUTBOUND", "LOJA_PDV", "APP", "SITE", "VISITA_TECNICA"]
MOTIVOS = ["FATURAMENTO", "ATENDIMENTO", "QUALIDADE_REDE", "ALTERACAO_PLANO", "SUPORTE"]


def _sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -15, 15)))


def _last_day(period):
    return date(period.year, period.month, calendar.monthrange(period.year, period.month)[1])


def _random_date(rng, period, min_day=1, max_day=27):
    last = min(max_day, _last_day(period).day)
    return date(period.year, period.month, int(rng.integers(min_day, last + 1)))


def gerar_dados_sinteticos(n_clientes=1200, seed=42):
    """Gera cadastros, contratos, pagamentos, contatos, consumo, contexto e churn.

    A rotulagem mensal usa somente cancelamentos do mes SEGUINTE a data de corte.
    Varios meses historicos permitem validacao temporal independente de outubro.
    """
    if n_clientes < 300:
        raise ValueError("Use pelo menos 300 clientes sinteticos para esta POC.")
    RAW.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    meses = pd.period_range("2025-01", "2026-10", freq="M")
    clientes = []
    contratos = []
    pagamentos = []
    atendimentos = []
    consumo = []
    rede = []
    contexto = []
    churn = []
    por_cliente = {}
    ativos = defaultdict(list)
    eventos_futuros = defaultdict(list)

    for idx in range(n_clientes):
        cli = f"SYN_C{idx+1:06d}"
        reg = str(rng.choice(REGIOES))
        inicio = date(int(rng.integers(2017, 2025)), int(rng.integers(1, 13)), 1)
        qtd = int(rng.choice([1, 2, 3], p=[0.37, 0.50, 0.13]))
        base_risco = float(rng.normal(0, 0.85))
        base_suporte = float(rng.normal(0, 0.65))
        mensal = 0.0
        for j in range(qtd):
            cid = f"SYN_K{idx+1:06d}_{j+1}"
            produto = "MOVEL" if j == 0 or (qtd > 1 and j == 2) else "FIXA"
            preco = round(float(rng.uniform(52, 155) if produto == "MOVEL" else rng.uniform(90, 265)), 2)
            contratos.append({"contrato_id": cid, "cliente_id": cli, "produto": produto,
                              "data_inicio": inicio, "data_fim": "", "valor_plano": preco})
            ativos[cli].append(len(contratos) - 1)
            mensal += preco
        clientes.append({"cliente_id": cli, "regiao": reg, "data_entrada": inicio,
                         "origem": "100% SINTETICA", "sem_dados_pessoais": True})
        por_cliente[cli] = {"regiao": reg, "base_risco": base_risco,
                            "suporte": base_suporte, "debt": 0.0,
                            "uso_gb": float(rng.uniform(10, 140)), "vivo": True}

    # Fatores externos ficticios, nunca indices observados do mundo real.
    mapa_ext = {}
    for mes in meses:
        for reg in REGIOES:
            press = float(np.clip(rng.normal(0.48, 0.14), 0.05, 0.95))
            clima = float(np.clip(rng.normal(0.28, 0.19), 0, 1))
            concorrencia = float(np.clip(rng.normal(0.35, 0.2), 0, 1))
            falhas = int(rng.poisson(0.5 + 2.8 * clima))
            key = (str(mes), reg)
            mapa_ext[key] = (press, clima, concorrencia, falhas)
            contexto.append({"mes_referencia": str(mes), "regiao": reg,
                             "data_publicacao": date(mes.year, mes.month, 1),
                             "indice_pressao_economica": round(press, 5),
                             "indice_eventos_climaticos": round(clima, 5),
                             "indice_concorrencia": round(concorrencia, 5),
                             "fonte": "SIMULADOR_SEM_DADOS_REAIS"})
            rede.append({"data_evento": _random_date(rng, mes, 2, 25),
                         "mes_referencia": str(mes), "regiao": reg,
                         "incidentes_rede_regiao": falhas,
                         "fonte": "SIMULADOR_SEM_DADOS_REAIS"})

    for mes in meses:
        mstr = str(mes)
        # Churn gerado no mes anterior somente afeta os meses seguintes.
        for evento in eventos_futuros.get(mstr, []):
            cli, tipo, when = evento
            posicoes = ativos[cli]
            if tipo == "TOTAL":
                for pos in posicoes:
                    contratos[pos]["data_fim"] = when
                ativos[cli] = []
                por_cliente[cli]["vivo"] = False
            elif len(posicoes) > 1:
                pos = int(rng.choice(posicoes))
                contratos[pos]["data_fim"] = when
                ativos[cli] = [x for x in posicoes if x != pos]
            churn.append({"cliente_id": cli, "data_evento": when, "tipo_churn": tipo,
                          "origem": "SIMULADO"})

        if mes == meses[-1]:
            # Outubro/2026: somente target; nao construir features de outubro.
            continue

        for cli, estado in por_cliente.items():
            if not estado["vivo"]:
                continue
            reg = estado["regiao"]
            press, clima, concorrencia, falhas = mapa_ext[(mstr, reg)]
            cids = ativos[cli]
            if not cids:
                continue
            mensal = sum(contratos[i]["valor_plano"] for i in cids)
            # Vulnerabilidade latente evolui; seu valor NAO entra nas features.
            estado["base_risco"] = float(0.9 * estado["base_risco"] + 0.1 * rng.normal(0, 0.8))
            atraso_prob = float(_sigmoid(-1.37 + 0.8 * estado["base_risco"] + 0.8 * press))
            atrasou = rng.random() < atraso_prob
            dias_atraso = int(rng.integers(2, 22)) if atrasou else 0
            paid_frac = float(rng.choice([0.0, 0.45, 0.75, 1.0], p=[0.16, 0.18, 0.20, 0.46])) if atrasou else 1.0
            valor_pago = round(mensal * paid_frac, 2)
            estado["debt"] = float(min(3500, max(0, estado["debt"] + mensal - valor_pago
                                                       - (mensal * 0.35 if not atrasou else 0))))
            pagamentos.append({"cliente_id": cli, "data_evento": _random_date(rng, mes, 14, 26),
                               "mes_referencia": mstr, "valor_fatura": round(mensal, 2),
                               "valor_pago": valor_pago, "dias_atraso": dias_atraso,
                               "valor_divida_net": round(estado["debt"], 2),
                               "pagamento_integral": int(paid_frac == 1.0)})
            risco_servico = float(_sigmoid(-1.55 + 0.9 * estado["suporte"] + 0.4 * falhas))
            qtd_contatos = min(6, int(rng.poisson(0.35 + 2.5 * risco_servico)))
            recl = 0
            resolvidos = 0
            for _ in range(qtd_contatos):
                canal = str(rng.choice(CANAIS, p=[0.30, 0.10, 0.12, 0.21, 0.17, 0.10]))
                motivo = str(rng.choice(MOTIVOS))
                reclamacao = int(rng.random() < (0.36 + 0.25 * risco_servico))
                resolvido = int(rng.random() < (0.73 - 0.35 * risco_servico))
                recl += reclamacao
                resolvidos += resolvido
                atendimentos.append({"cliente_id": cli,
                                     "data_evento": _random_date(rng, mes, 1, 26),
                                     "canal": canal, "motivo": motivo,
                                     "reclamacao": reclamacao, "resolvido": resolvido,
                                     "protocolo_sintetico": f"P-{cli}-{mstr}-{_+1}"})
            if rng.random() < 0.055:
                atendimentos.append({"cliente_id": cli,
                                     "data_evento": _random_date(rng, mes, 1, 26),
                                     "canal": "APP", "motivo": "CONSULTA_PLANO",
                                     "reclamacao": 0, "resolvido": 1,
                                     "protocolo_sintetico": f"P-{cli}-{mstr}-APP"})
            migrou = int(rng.random() < (0.035 + 0.05 * risco_servico))
            estado["uso_gb"] = float(max(0.5, estado["uso_gb"] * rng.uniform(0.72, 1.15)))
            if rng.random() < 0.035:
                estado["uso_gb"] *= float(rng.uniform(0.3, 0.6))
            consumo.append({"cliente_id": cli, "data_evento": _last_day(mes),
                            "mes_referencia": mstr, "consumo_gb": round(estado["uso_gb"], 3),
                            "houve_migracao": migrou})

            # Desfecho do proximo mes. Correlacoes sinteticas validam o pipeline,
            # mas nao sao estimativas de comportamento real de clientes.
            if mes == meses[-2] or mes < meses[-2]:
                debt_ratio = min(3, estado["debt"] / max(1, mensal))
                protective = 0.55 * int(not atrasou) + 0.35 * int(qtd_contatos > 0 and resolvidos == qtd_contatos)
                log_odds = (-4.25 + 0.82 * estado["base_risco"]
                            + 0.35 * debt_ratio + 0.25 * min(3, recl)
                            + 0.14 * falhas + 0.32 * concorrencia
                            + 0.42 * risco_servico - protective)
                p_total = float(_sigmoid(log_odds))
                p_parcial = float(_sigmoid(-3.25 + 0.4 * estado["base_risco"]
                                            + 0.3 * recl + 0.3 * concorrencia + 0.12 * falhas)) if len(cids) > 1 else 0.0
                sorteio = float(rng.random())
                tipo = "TOTAL" if sorteio < p_total else ("PARCIAL" if sorteio < p_total + p_parcial else None)
                if tipo is not None:
                    mes_seguinte = mes + 1
                    data_churn = _random_date(rng, mes_seguinte, 3, 26)
                    eventos_futuros[str(mes_seguinte)].append((cli, tipo, data_churn))

    arquivos = {
        "clientes.csv": clientes, "contratos.csv": contratos,
        "pagamentos.csv": pagamentos, "atendimentos.csv": atendimentos,
        "consumo.csv": consumo, "contexto_externo.csv": contexto,
        "rede.csv": rede, "churn_eventos.csv": churn,
    }
    for nome, registros in arquivos.items():
        pd.DataFrame(registros).to_csv(RAW / nome, index=False, encoding="utf-8-sig")
    manifest = {"projeto": "CLARO_CHURN_PREDITIVO_360_POC", "tipo": "100% SINTETICO",
                "seed": seed, "clientes_gerados": n_clientes,
                "meses_gerados": [str(meses[0]), str(meses[-1])],
                "data_corte_teste": "2026-09-30", "target_teste": "outubro/2026",
                "aviso": "As pessoas, indices externos, eventos e churn sao inteiramente ficticios.",
                "linhas_por_arquivo": {k: len(v) for k, v in arquivos.items()}}
    (RAW / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest
