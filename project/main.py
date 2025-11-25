import os
import sys

from src.services.graph_service import GraphService
from src.algorithm.search import dijkstra   # mostrar_grafo ignorado


# Caminho raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def buscar_no_por_nome_parcial(G, termo):
    """
    Busca parcial simples:
    - converte tudo para minúsculo
    - procura substring no nome da música
    - se não encontrar nada, procura no artista
    - se ainda assim não achar, retorna None
    """
    termo = termo.lower()

    candidatos = []

    for node_id, data in G.nodes(data=True):
        nome = data.get("name", "").lower()
        artista = data.get("artist", "").lower()

        if termo in nome or termo in artista:
            candidatos.append((node_id, data))

    if not candidatos:
        return None

    # critério simples: pega o mais curto (nome mais próximo)
    candidatos.sort(key=lambda x: len(x[1].get("name", "")))

    return candidatos[0][0]   # retorna só o 

def formatar_musica(G, node_id):
    """
    Retorna 'NOME — ARTISTA' dado o ID da música.
    Se não existir, retorna o próprio ID.
    """
    data = G.nodes[node_id]
    nome = data.get("name", "??")
    artista = data.get("artist", "??")
    return f"{nome} — {artista}"



def main():
    print("🔄 Carregando grafo, aguarde...")

    service = GraphService(root_dir=BASE_DIR)

    try:
        service.run_full_etl()
        G = service.get_graph(force_rebuild=True)

        print(f"✔ Grafo carregado com {len(G.nodes)} músicas.\n")

        # --------------------------
        # Interface do Usuário (CLI)
        # --------------------------

        while True:
            print("🎵  BUSCA DE MÚSICAS (digite parte do nome ou artista)")
            termo_origem = input(" → Música de ORIGEM: ").strip()

            origem = buscar_no_por_nome_parcial(G, termo_origem)
            if origem is None:
                print("❌ Nenhuma música encontrada! Tente novamente.\n")
                continue

            termo_destino = input(" → Música de DESTINO: ").strip()

            destino = buscar_no_por_nome_parcial(G, termo_destino)
            if destino is None:
                print("❌ Nenhuma música encontrada! Tente novamente.\n")
                continue

            print(f"\nCalculando menor caminho entre:")
            print(f"   Origem : {formatar_musica(G, origem)}")
            print(f"   Destino: {formatar_musica(G, destino)}")



            path, dist = dijkstra(G, origem, destino)

            if path is None:
                print("❌ Nenhum caminho encontrado!\n")
            else:
                print(f"✔ Caminho encontrado ({len(path)} passos):")
                print("\n".join(f" → {formatar_musica(G, node)}" for node in path))
                print(f"🎯 Distância total: {dist:.4f}\n")

            print("-" * 60)
            again = input("Deseja buscar outro caminho? (s/n): ").strip().lower()
            if again != "s":
                break

    except Exception as e:
        print(f"💥 Erro: {e}")


if __name__ == "__main__":
    main()
