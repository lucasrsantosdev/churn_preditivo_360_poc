"""Relatorio offline, sem servidor ou integracoes externas."""
import base64
import html
import json

import pandas as pd

from .config import OUTPUTS, PREDICOES, METRICAS, GRAFICOS


def _img(path):
    if not path.exists():
        return "<p>Grafico nao disponivel.</p>"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img alt="{html.escape(path.stem)}" src="data:image/png;base64,{encoded}">'


def gerar_relatorio():
    metrics = json.loads((METRICAS / "metricas_experimento.json").read_text(encoding="utf-8"))
    df = pd.read_csv(PREDICOES / "previsoes_outubro_2026_SINTETICAS.csv")
    top = df.head(25).copy()
    cols = ["cliente_id", "regiao", "prob_churn_total_30d", "prob_churn_parcial_30d",
            "faixa_priorizacao", "evidencias_pressao", "evidencias_protecao"]
    top["prob_churn_total_30d"] = top["prob_churn_total_30d"].map(lambda x: f"{x:.2%}")
    top["prob_churn_parcial_30d"] = top["prob_churn_parcial_30d"].map(lambda x: f"{x:.2%}")
    linhas = []
    for tupla in top[cols].itertuples(index=False, name=None):
        linhas.append("<tr>" + "".join(f"<td>{html.escape(str(v))}</td>" for v in tupla) + "</tr>")
    colunas = "".join(f"<th>{html.escape(x)}</th>" for x in cols)
    def f(v):
        return "N/D" if v is None else str(v)
    corpo = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>CLARO | Churn Preditivo 360 - POC sintetica</title>
    <style>body{{margin:0;background:#f2f5f8;color:#1d2c40;font:15px Segoe UI,Arial,sans-serif}}
    header{{padding:30px 5%;background:#173556;color:white}}
    h1{{font-size:26px;margin:0 0 8px}}h2{{font-size:20px}}
    main{{padding:24px 5%;max-width:1400px;margin:auto}}
    .alert{{background:#fff8e7;border-left:4px solid #c99428;padding:15px 20px;margin-bottom:22px}}
    .grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px}}
    .card{{background:white;padding:19px 22px;border-radius:12px;box-shadow:0 2px 10px #0001}}
    .metric{{font-size:26px;font-weight:700;margin:6px 0}}.muted{{color:#647287;font-size:13px}}
    img{{max-width:100%;height:auto}}.charts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:18px}}
    .scroll{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:12px}}
    th,td{{text-align:left;padding:10px;border-bottom:1px solid #e4e7eb}}
    th{{background:#f6f8fb;position:sticky;top:0}}footer{{color:#647287;padding:30px 0}}
    </style></head><body><header><h1>CLARO | Customer Journey & Churn Preditivo 360º</h1>
    POC independente • Simulador & modelo experimental • Validação outubro/2026</header><main>
    <section class="alert"><b>ATENÇÃO — DADOS 100% SINTÉTICOS.</b>
    Nenhum registro, indicador externo ou resultado deste painel representa a operação real da Claro.
    Os valores demonstram apenas o funcionamento do pipeline e não comprovam desempenho em produção.</section>
    <div class="grid">
    <div class="card"><div class="muted">Clientes elegíveis em 30/09</div><div class="metric">{len(df):,}</div></div>
    <div class="card"><div class="muted">Churn total observado (sintético)</div><div class="metric">{(df['desfecho_real_SINTETICO_outubro']=='TOTAL').mean():.2%}</div></div>
    <div class="card"><div class="muted">Churn parcial observado (sintético)</div><div class="metric">{(df['desfecho_real_SINTETICO_outubro']=='PARCIAL').mean():.2%}</div></div>
    <div class="card"><div class="muted">Período de validação</div><div class="metric">OUT/26</div><div class="muted">Corte em 30/09/2026</div></div>
    </div><h2>Qualidade do modelo no teste temporal</h2><div class="grid">
    <div class="card"><b>Churn total</b><div class="metric">{f(metrics['total']['teste_outubro']['pr_auc_ap'])}</div>
    <div class="muted">Average precision • {metrics['total']['modelo_escolhido']}</div></div>
    <div class="card"><b>Churn parcial</b><div class="metric">{f(metrics['parcial']['teste_outubro']['pr_auc_ap'])}</div>
    <div class="muted">Average precision • {metrics['parcial']['modelo_escolhido']}</div></div>
    <div class="card"><b>Lift top 5% - total</b><div class="metric">{f(metrics['total']['teste_outubro']['lift_top_5pct'])}×</div>
    <div class="muted">vs. amostra sintética geral</div></div>
    <div class="card"><b>Brier score - total</b><div class="metric">{f(metrics['total']['teste_outubro']['brier'])}</div>
    <div class="muted">Menor é melhor • avaliação sintética</div></div>
    </div><h2>Variáveis associadas ao score e calibração</h2><div class="charts">
    <div class="card">{_img(GRAFICOS/'importancia_total.png')}</div>
    <div class="card">{_img(GRAFICOS/'importancia_parcial.png')}</div>
    <div class="card">{_img(GRAFICOS/'calibracao_total.png')}</div>
    <div class="card">{_img(GRAFICOS/'calibracao_parcial.png')}</div>
    </div><h2>Exemplos de clientes simulados para revisão humana</h2>
    <p class="muted">Ordenados por risco estimado de churn total. Contrapesos explicativos não alteram a probabilidade calibrada.</p>
    <div class="card scroll"><table><thead><tr>{colunas}</tr></thead><tbody>{''.join(linhas)}</tbody></table></div>
    <footer>POC v0.1 • Treino até julho/2026 • Validação agosto/2026 • Teste setembro→outubro/2026.
    Não utilizar como decisão automatizada de retenção. Validações reais e LGPD necessárias antes de implantação.</footer>
    </main></body></html>'''
    path = OUTPUTS / "painel_churn_360_SINTETICO.html"
    path.write_text(corpo, encoding="utf-8")
    return path
