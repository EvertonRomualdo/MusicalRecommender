import os
import sys


from src.services.graph_service import GraphService
from src.algorithm.search import dijkstra, mostrar_grafo #transferir mostrar_grafo para ui depois

# Caminho raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#7364

def main():
    # Instancia o serviço
    service = GraphService(root_dir=BASE_DIR)
    

    try:
        print("Solicitando grafo ao serviço...")
        service.run_full_etl()
        G = service.get_graph(force_rebuild=True)

        print(f"Sucesso! Grafo obtido com {len(G.nodes)} nós.")

        origem = "0VjIjW4GlUZAMYd2vXMi3b"   
        destino = "57jOEZtoLQK4zF2x55bdkp"    

        print(f"\nCalculando menor caminho entre {origem} → {destino} ...")
        path, dist = dijkstra(G, origem, destino)

        if path is None:
            print("Nenhum caminho encontrado!")
        else:
            print(f"\nCaminho encontrado ({len(path)} passos):")
            print(path)
            print(f"\nDistância total: {dist:.4f}")

            mostrar_grafo(G, path=path)

    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    main()