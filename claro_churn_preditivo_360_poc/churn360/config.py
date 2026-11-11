from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW = DATA_DIR / "raw"
BRONZE = DATA_DIR / "bronze"
SILVER = DATA_DIR / "silver"
GOLD = DATA_DIR / "gold"
OUTPUTS = BASE_DIR / "outputs"
PREDICOES = OUTPUTS / "previsoes"
MODELOS = OUTPUTS / "modelos"
METRICAS = OUTPUTS / "metricas"
GRAFICOS = OUTPUTS / "graficos"

# Cortes do experimento predefinidos (nenhum dado de outubro pode ser feature)
DATA_CORTE_TESTE = "2026-09-30"
INICIO_JANELA_TESTE = "2026-04-04"  # 180 dias inclusivos ate 30/09/2026
INICIO_FEATURES = "2025-07-31"
FIM_FEATURES = "2026-09-30"
DATA_VALIDACAO = "2026-08-31"

COLUNAS_FEATURES = [
    "tempo_relacionamento_meses", "qtd_contratos_ativos", "valor_mensal_plano",
    "val_divida_net_m0", "val_pagamento_net_m0", "qtd_pag_ultimos_60d",
    "qtd_pag_sem_atraso_90d", "qtd_atrasos_180d", "max_dias_atraso_180d",
    "razao_pago_devido_180d", "qtd_reclamacao_180d", "qtd_ura_180d",
    "qtd_visita_tecnica_180d", "qtd_atendimentos_nao_resolvidos_180d",
    "taxa_resolucao_180d", "qtd_migracoes_180d", "consumo_gb_ultimo_mes",
    "variacao_consumo_3m", "qtd_contatos_app_180d",
    "indice_pressao_economica", "indice_eventos_climaticos",
    "indice_concorrencia", "incidentes_rede_regiao",
]
