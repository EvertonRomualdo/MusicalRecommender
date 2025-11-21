import os
from src.preprocessing.processor import DataProcessor
from src.preprocessing.graph_builder import GraphBuilder

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DATA = os.path.join(BASE_DIR, 'data', 'raw', 'dataset.csv')
PROCESSED_DATA = os.path.join(BASE_DIR, 'data', 'processed', 'songs.csv')


# Main temporario para teste rapido das funções que foram implementadas
def main():
    print("=== SISTEMA DE RECOMENDAÇÃO MUSICAL (DIJKSTRA) ===\n")

    # verifique se ja existe
    if not os.path.exists(PROCESSED_DATA):
        print("Arquivo processado não encontrado. Executando ETL...")
        processor = DataProcessor(RAW_DATA, PROCESSED_DATA)
        try:
            processor.process()
        except Exception as e:
            print(f"Erro fatal no ETL: {e}")
            return
    else:
        print("Dataset processado já existente. Carregando...")

    #Construção do Grafo
    try:
        builder = GraphBuilder(PROCESSED_DATA)
        # K=5 significa que cada música terá 5 opções de transição
        grafo = builder.build_graph(k_neighbors=5)
    except Exception as e:
        print(f"Erro ao criar grafo: {e}")
        return

    #teste de sucesso para validar o grafo gerado
    #util para o desenvolvimento
    print("\n--- TESTE DE CONEXÃO ---")
    
    
    primeiro_id = list(grafo.nodes)[0]
    dados_no = grafo.nodes[primeiro_id]
    
    print(f"Música Origem: {dados_no['name']} - {dados_no['artist']}")
    print("Conecta com:")
    
    # Mostra os vizinhos
    vizinhos = grafo.successors(primeiro_id)
    for vizinho_id in vizinhos:
        dados_vizinho = grafo.nodes[vizinho_id]
        peso = grafo.edges[primeiro_id, vizinho_id]['weight']
        print(f"  -> {dados_vizinho['name']} (Distância: {peso:.4f})")

if __name__ == "__main__":
    main()