import os
import sys


from src.services.graph_service import GraphService

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
    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    main()