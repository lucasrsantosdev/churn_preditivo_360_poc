import argparse
import json

from .synthetic import gerar_dados_sinteticos
from .pipeline import preparar_camadas
from .model import treinar_e_avaliar
from .report import gerar_relatorio


def main():
    ap = argparse.ArgumentParser(description="CLARO Churn 360 - POC 100% sintetica")
    ap.add_argument("etapa", choices=["gerar", "preparar", "treinar", "relatorio", "all"],
                    help="Etapa da execucao (all executa toda a POC)")
    ap.add_argument("--clientes", type=int, default=1200, help="Clientes simulados (minimo 300)")
    ap.add_argument("--seed", type=int, default=42, help="Semente de reproducao")
    args = ap.parse_args()
    if args.etapa in ("gerar", "all"):
        info = gerar_dados_sinteticos(args.clientes, args.seed)
        print("[RAW] Gerados clientes sinteticos:", info["clientes_gerados"])
    if args.etapa in ("preparar", "all"):
        info = preparar_camadas()
        print("[GOLD] Snapshots:", info["snapshots"],
              "| Coorte de outubro:", info["clientes_coorte_outubro"])
    if args.etapa in ("treinar", "all"):
        info = treinar_e_avaliar()
        print("[ML] Treino/validacao/teste:", info["amostras"])
        for alvo in ("total", "parcial"):
            r = info[alvo]
            print(f"[ML] {alvo} | {r['modelo_escolhido']} | PR-AUC teste: {r['teste_outubro']['pr_auc_ap']}")
    if args.etapa in ("relatorio", "all"):
        print("[PAINEL]", gerar_relatorio())
    print("CONCLUIDO - todos os dados utilizados nesta POC sao sinteticos.")


if __name__ == "__main__":
    main()
