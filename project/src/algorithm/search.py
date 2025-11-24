import heapq
import networkx as nx
import matplotlib.pyplot as plt


def dijkstra(graph, source, target):
    dist = {node: float('inf') for node in graph.nodes}
    prev = {node: None for node in graph.nodes}
    dist[source] = 0
    pq = [(0, source)]

    while pq:
        current_dist, current_node = heapq.heappop(pq)

        if current_dist > dist[current_node]:
           continue
       
        if current_node == target:
           break

        for neighbor, data in graph[current_node].items():
            weight = data.get('weight', 1.0)
            new_dist = current_dist + weight

            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = current_node
                heapq.heappush(pq, (new_dist, neighbor))

    if dist[target] == float('inf'):
        return None, float('inf')
        
    path = []
    currrent = target
    while currrent is not None:
        path.append(currrent)
        currrent = prev[currrent]

    path.reverse()
    return path, dist[target]

def mostrar_grafo(graph, path=None):
    plt.figure(figsize=(6, 5))

    pos = nx.spring_layout(graph, seed=42)

    # Desenha nós e arestas normais
    nx.draw_networkx_nodes(graph, pos, node_size=700, node_color="#444")
    nx.draw_networkx_edges(graph, pos, width=2, edge_color="#888")
    nx.draw_networkx_labels(graph, pos, font_color="white")

    # ------------------------------
    # Pintar o menor caminho (somente as arestas)
    # ------------------------------
    if path is not None and len(path) > 1:
        caminho_arestas = list(zip(path, path[1:]))

        nx.draw_networkx_edges(
            graph, pos,
            edgelist=caminho_arestas,
            width=4,
            edge_color="red"
        )

        # nós do caminho (vermelhos, como antes)
        nx.draw_networkx_nodes(
            graph, pos,
            nodelist=path,
            node_size=700,
            node_color="red"
        )

    # -----------------------------------
    # AGORA sim desenhar pesos por último
    # -----------------------------------
    edge_labels = nx.get_edge_attributes(graph, "weight")
    nx.draw_networkx_edge_labels(
        graph, pos,
        edge_labels=edge_labels,
        font_color="black",
        font_size=10,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.6)  # opcional: caixinha atrás
    )

    plt.axis("off")
    plt.show()

def main():
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

    source = "A"
    target = "Q"

    path, cost = dijkstra(G, source, target)

    print("Melhor caminho encontrado:", path)
    print("Custo total:", cost)

    mostrar_grafo(G, path)


if __name__ == "__main__":
    main()