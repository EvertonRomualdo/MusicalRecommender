# project/tests/test_graph.py
import os
import pandas as pd
import networkx as nx
from src.preprocessing.graph_builder import GraphBuilder

def create_sample_csv(tmp_path, subset=None):
    """Cria um CSV de teste temporário"""
    data = {
        "track_id": ["1", "2", "3", "4"],
        "track_name": ["SongA", "SongB", "SongC", "SongD"],
        "artists": ["Artist1", "Artist2", "Artist3", "Artist4"],
        "danceability": [0.5, 0.6, 0.7, 0.8],
        "energy": [0.8, 0.7, 0.6, 0.5],
        "valence": [0.3, 0.4, 0.5, 0.6],
        "tempo": [120, 130, 110, 140],
        "acousticness": [0.1, 0.2, 0.3, 0.4],
        "instrumentalness": [0.0, 0.0, 0.1, 0.2]
    }
    df = pd.DataFrame(data)
    if subset:
        df = df.loc[subset]
    csv_file = os.path.join(tmp_path, "songs.csv")
    df.to_csv(csv_file, index=False)
    return csv_file

def test_graph_correct(tmp_path):
    """Grafo construído corretamente"""
    csv_file = create_sample_csv(tmp_path)
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=2)

    expected_nodes = ["1", "2", "3", "4"]
    # Todos os nós esperados existem
    for node in expected_nodes:
        n = node if node in G.nodes else int(node)
        assert n in G.nodes
        assert "name" in G.nodes[n]
        assert "artist" in G.nodes[n]

    # Testa pesos das arestas
    for _, _, data in G.edges(data=True):
        assert "weight" in data
        assert data["weight"] >= 0

def test_graph_incorrect(tmp_path):
    """Simula grafo 'incorreto' removendo 1 nó"""
    # Seleciona apenas as linhas com track_id 2 e 3 (omitindo 1 e 4)
    csv_file = create_sample_csv(tmp_path, subset=[1,2])
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=1)

    # Esperados que estão no CSV
    expected_present = ["2", "3"]
    expected_missing = ["1", "4"]

    # Verifica nós presentes
    for node in expected_present:
        assert node in G.nodes or int(node) in G.nodes

    # Verifica nós ausentes
    for node in expected_missing:
        assert node not in G.nodes and int(node) not in G.nodes

def test_graph_empty(tmp_path):
    """CSV vazio gera grafo nulo"""
    csv_file = os.path.join(tmp_path, "empty.csv")
    pd.DataFrame(columns=["track_id","track_name","artists","danceability",
                          "energy","valence","tempo","acousticness","instrumentalness"]).to_csv(csv_file, index=False)
    builder = GraphBuilder(csv_file)
    try:
        G = builder.build_graph()
        assert len(G.nodes) == 0
    except ValueError:
        pass

def test_graph_one_node(tmp_path):
    """Grafo com apenas um nó"""
    csv_file = create_sample_csv(tmp_path, subset=[0])
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=2)
    assert len(G.nodes) == 1
    for _, data in G.nodes(data=True):
        assert "name" in data
        assert "artist" in data

def test_nodes_missing(tmp_path):
    """Testa cenários de nós faltando"""
    csv_file = create_sample_csv(tmp_path)
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=2)
    nodes_list = list(map(str, G.nodes))

    # Apenas o primeiro nó esperado não existe
    first_missing = "1" not in nodes_list
    # Apenas o último nó esperado não existe
    last_missing = "4" not in nodes_list
    # Nenhum nó esperado existe
    none_missing = all(n not in nodes_list for n in ["1","2","3","4"])

def test_attributes(tmp_path):
    """Testa atributos de nós"""
    csv_file = create_sample_csv(tmp_path)
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=2)
    for _, data in G.nodes(data=True):
        # atributos corretos
        assert "name" in data
        assert "artist" in data
        # valores não vazios
        assert data["name"] != ""
        assert data["artist"] != ""

def test_edge_weights(tmp_path):
    """Testa pesos das arestas"""
    csv_file = create_sample_csv(tmp_path)
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=2)
    for u, v, data in G.edges(data=True):
        assert "weight" in data
        assert data["weight"] >= 0

def test_no_duplicate_nodes(tmp_path):
    """Verifica se não há nós duplicados"""
    csv_file = create_sample_csv(tmp_path)
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=2)
    assert len(set(G.nodes)) == len(G.nodes)

def test_save_and_load(tmp_path):
    """Testa salvar e carregar grafo"""
    csv_file = create_sample_csv(tmp_path)
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=2)
    graph_path = os.path.join(tmp_path, "graph.graphml")
    builder.save_graph(graph_path)
    assert os.path.exists(graph_path)

    G_loaded = GraphBuilder.load_graph(graph_path)
    assert isinstance(G_loaded, nx.DiGraph)
    assert G_loaded.number_of_nodes() == G.number_of_nodes()
    assert G_loaded.number_of_edges() == G.number_of_edges()

if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = tmpdir

        print("Testando grafo construído corretamente...")
        test_graph_correct(tmp_path)
        print("Testando grafo construído incorretamente...")
        test_graph_incorrect(tmp_path)
        print("Testando grafo nulo...")
        test_graph_empty(tmp_path)
        print("Testando grafo com apenas um nó...")
        test_graph_one_node(tmp_path)
        print("Testando atributos e nós faltando...")
        test_nodes_missing(tmp_path)
        test_attributes(tmp_path)
        print("Testando pesos das arestas...")
        test_edge_weights(tmp_path)
        print("Testando duplicidade de nós...")
        test_no_duplicate_nodes(tmp_path)
        print("Testando salvar e carregar grafo...")
        test_save_and_load(tmp_path)
        
        print("Tudo funcionou!")