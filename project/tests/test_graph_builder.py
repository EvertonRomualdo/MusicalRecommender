# project/tests/test_graph.py
import os
import pandas as pd
import pytest
import networkx as nx
from src.preprocessing.graph_builder import GraphBuilder

def create_sample_csv(tmp_path, subset=None):
    """Cria um CSV de teste temporário com dados de músicas"""
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
    for node in expected_nodes:
        n = node if node in G.nodes else int(node)
        assert n in G.nodes
        assert "name" in G.nodes[n]
        assert "artist" in G.nodes[n]

    for _, _, data in G.edges(data=True):
        assert "weight" in data
        assert data["weight"] >= 0


def test_graph_incorrect(tmp_path):
    """Grafo com algumas músicas removidas"""
    csv_file = create_sample_csv(tmp_path, subset=[1, 2])
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=1)

    expected_present = ["2", "3"]
    expected_missing = ["1", "4"]

    for node in expected_present:
        assert node in G.nodes or int(node) in G.nodes
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
    """Verifica nós em cenários variados"""
    csv_file = create_sample_csv(tmp_path)
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=2)
    nodes_list = list(map(str, G.nodes))
    # Nenhum nó faltando completamente
    assert all(n in nodes_list for n in ["1","2","3","4"])


def test_attributes(tmp_path):
    """Testa atributos de nós"""
    csv_file = create_sample_csv(tmp_path)
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=2)
    for _, data in G.nodes(data=True):
        assert "name" in data and data["name"] != ""
        assert "artist" in data and data["artist"] != ""


def test_edge_weights(tmp_path):
    """Testa pesos das arestas"""
    csv_file = create_sample_csv(tmp_path)
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=2)
    for _, _, data in G.edges(data=True):
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


def test_build_graph_missing_csv(tmp_path):
    """Testa FileNotFoundError se CSV não existir"""
    missing_path = os.path.join(tmp_path, "nao_existe.csv")
    builder = GraphBuilder(missing_path)
    with pytest.raises(FileNotFoundError):
        builder.build_graph()


def test_build_graph_missing_numeric_columns(tmp_path):
    """Testa ValueError se CSV não tiver colunas numéricas"""
    csv_path = os.path.join(tmp_path, "songs.csv")
    with open(csv_path, "w") as f:
        f.write("track_id,track_name,artists\n1,A,B\n2,C,D")
    builder = GraphBuilder(csv_path)
    with pytest.raises(ValueError):
        builder.build_graph()


def test_build_graph_k_greater_than_nodes(tmp_path):
    """Testa k_neighbors maior que número de nós"""
    csv_file = os.path.join(tmp_path, "songs.csv")
    with open(csv_file, "w") as f:
        f.write(
            "track_id,track_name,artists,danceability,energy,valence,tempo,acousticness,instrumentalness\n"
            "1,A,B,0.5,0.6,0.7,120,0.1,0.0\n"
            "2,C,D,0.6,0.5,0.6,130,0.2,0.0\n"
        )
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=5)
    assert len(G.nodes) == 2
    for u, v, data in G.edges(data=True):
        assert "weight" in data
        assert data["weight"] >= 0


def test_save_graph_empty(tmp_path):
    """Testa save_graph em grafo vazio não gera erro"""
    builder = GraphBuilder(tmp_path)
    output_path = os.path.join(tmp_path, "vazio.graphml")
    builder.save_graph(output_path)
    assert not os.path.exists(output_path)


def test_load_graph_missing_file(tmp_path):
    """Testa FileNotFoundError ao carregar grafo inexistente"""
    missing_path = os.path.join(tmp_path, "nao_existe.graphml")
    with pytest.raises(FileNotFoundError):
        GraphBuilder.load_graph(missing_path)


def test_save_and_load_graph(tmp_path):
    """Testa salvar e carregar grafo completo"""
    csv_file = os.path.join(tmp_path, "songs.csv")
    with open(csv_file, "w") as f:
        f.write(
            "track_id,track_name,artists,danceability,energy,valence,tempo,acousticness,instrumentalness\n"
            "1,A,B,0.5,0.6,0.7,120,0.1,0.0\n"
            "2,C,D,0.6,0.5,0.6,130,0.2,0.0\n"
        )
    builder = GraphBuilder(csv_file)
    G = builder.build_graph(k_neighbors=1)

    graph_path = os.path.join(tmp_path, "graph.graphml")
    builder.save_graph(graph_path)
    assert os.path.exists(graph_path)

    G_loaded = GraphBuilder.load_graph(graph_path)
    assert isinstance(G_loaded, nx.DiGraph)
    assert G_loaded.number_of_nodes() == G.number_of_nodes()
    assert G_loaded.number_of_edges() == G.number_of_edges()

def test_build_graph_with_save_path(tmp_path):
    """Testa build_graph usando o parâmetro save_path para salvar automaticamente"""
    csv_file = create_sample_csv(tmp_path)
    builder = GraphBuilder(csv_file)

    save_path = os.path.join(tmp_path, "saved_graph.graphml")
    G = builder.build_graph(k_neighbors=2, save_path=save_path)

    assert isinstance(G, nx.DiGraph)
    assert G.number_of_nodes() == 4

    assert os.path.exists(save_path)


def test_build_graph_k_neighbors_greater_than_nodes(tmp_path):
    """Testa comportamento quando k_neighbors é maior que o número de nós disponíveis"""

    csv_file = create_sample_csv(tmp_path, subset=[0, 1])
    builder = GraphBuilder(csv_file)

    G = builder.build_graph(k_neighbors=5)

    nodes_as_str = set(map(str, G.nodes))
    assert nodes_as_str == {"1", "2"}

    for node in G.nodes:
        assert len(G.edges(node)) == 1
        for _, _, data in G.edges(node, data=True):
            assert "weight" in data
            assert data["weight"] >= 0

