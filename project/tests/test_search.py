# test_graph_algorithms.py
import pytest
import networkx as nx
from src.algorithm.search import dijkstra, mostrar_grafo  # substitua pelo nome do arquivo sem .py

def create_test_graph():
    G = nx.Graph()
    edges = [
        ("A", "B", 2), ("A", "C", 4), ("A", "D", 7),
        ("B", "E", 1), ("B", "F", 5),
        ("C", "F", 3), ("C", "G", 8),
        ("D", "G", 2), ("D", "H", 6),
        ("E", "I", 4), ("E", "J", 3),
        ("F", "J", 7), ("F", "K", 2),
        ("G", "K", 3), ("G", "L", 4),
        ("H", "L", 2), ("H", "M", 5),
        ("I", "N", 6), ("J", "N", 2),
        ("K", "O", 4), ("L", "O", 3),
        ("M", "P", 1), ("N", "P", 5),
        ("O", "Q", 2), ("P", "Q", 3)
    ]
    for u, v, w in edges:
        G.add_edge(u, v, weight=w)
    return G

def test_dijkstra_path_found():
    G = create_test_graph()
    path, cost = dijkstra(G, "A", "Q")
    assert path is not None
    assert cost < float('inf')
    assert path[0] == "A"
    assert path[-1] == "Q"

def test_dijkstra_no_path():
    G = nx.Graph()
    G.add_node("X")
    G.add_node("Y")
    path, cost = dijkstra(G, "X", "Y")
    assert path is None
    assert cost == float('inf')

def test_mostrar_grafo_with_path(monkeypatch):
    G = create_test_graph()
    path, _ = dijkstra(G, "A", "Q")
    # Para evitar abrir a janela de plot durante teste, podemos "monkeypatch" plt.show
    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None)
    mostrar_grafo(G, path)

def test_mostrar_grafo_without_path(monkeypatch):
    G = create_test_graph()
    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None)
    mostrar_grafo(G)

def test_dijkstra_path_and_no_path():
    # Grafo com caminho
    G = nx.Graph()
    G.add_edge("A", "B", weight=1)
    G.add_edge("B", "C", weight=2)
    path, cost = dijkstra(G, "A", "C")
    assert path == ["A", "B", "C"]
    assert cost == 3

    # Grafo sem caminho
    G = nx.Graph()
    G.add_nodes_from(["X", "Y"])
    path, cost = dijkstra(G, "X", "Y")
    assert path is None
    assert cost == float("inf")