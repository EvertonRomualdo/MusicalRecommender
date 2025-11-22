import pandas as pd
import networkx as nx
from sklearn.preprocessing import MinMaxScaler
from scipy.spatial.distance import cdist
import os

class GraphBuilder:
    """
    Responsável por transformar um CSV de músicas em um Grafo Direcionado (DiGraph).
    Usa K-Nearest Neighbors (K-NN) baseado na Distância Euclidiana.
    """
    
    def __init__(self, csv_path):
        self.csv_path = csv_path
        self.G = nx.DiGraph()
        self.df = None # Guardará o DataFrame carregado
    
    def build_graph(self, k_neighbors=50):
        """
        Constrói o grafo conectando cada música às suas K mais similares.
        
        Args:
            k_neighbors (int): Número de arestas saindo de cada nó (padrão: 50).
        
        Returns:
            nx.DiGraph: O grafo construído.
        """
        print("--- [GRAFO] Iniciando construção do grafo ---")
        
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.csv_path}")
        
        # Carregar Dados
        # Definimos 'id' como índice para facilitar a busca
        self.df = pd.read_csv(self.csv_path)
        if 'id' in self.df.columns:
            self.df.set_index('id', inplace=True)
        
        print(f"-> Carregadas {len(self.df)} músicas.")

        # Seleção de Features Numéricas para o Cálculo
        feature_cols = ['danceability', 'energy', 'valence', 'bpm', 'acousticness', 'instrumentalness']
        
        # Filtra apenas colunas que existem (segurança)
        cols_presentes = [c for c in feature_cols if c in self.df.columns]
        
        if not cols_presentes:
            raise ValueError("O dataset não contém as colunas necessárias para o cálculo!")

        data_numeric = self.df[cols_presentes].dropna()

        # NORMALIZAÇÃO (Min-Max Scaling)
        print("-> Normalizando dados (BPM, Energy, etc)...")
        scaler = MinMaxScaler()
        data_norm = pd.DataFrame(
            scaler.fit_transform(data_numeric),
            columns=data_numeric.columns,
            index=data_numeric.index
        )

        # Calcula a distância euclidiana de TODOS para TODOS
        print("-> Calculando distâncias euclidianas...")
        dist_matrix = cdist(data_norm, data_norm, metric='euclidean')
        
        # Transformamos em DataFrame para facilitar a consulta por ID
        df_dist = pd.DataFrame(dist_matrix, index=data_numeric.index, columns=data_numeric.index)

        #Criação dos Nós e Arestas
        print(f"-> Criando arestas (K={k_neighbors})...")
        
        count = 0
        total = len(data_numeric)
        
        for song_id in data_numeric.index:
            # Adiciona o nó com metadados(Nome e Artista)
            nome = self.df.loc[song_id].get('name', 'Unknown')
            artista = self.df.loc[song_id].get('artist', 'Unknown')
            
            self.G.add_node(song_id, name=nome, artist=artista)
            
            # Pega a linha de distâncias dessa música, ordena (ascendente) e pega os K primeiros
            vizinhos = df_dist.loc[song_id].nsmallest(k_neighbors + 1).iloc[1:]
            
            for vizinho_id, distancia in vizinhos.items():
                # Peso da aresta = Distância (Quanto menor, mais similar)
                self.G.add_edge(song_id, vizinho_id, weight=distancia)
            
            count += 1
            if count % 500 == 0:
                print(f"   Processados {count}/{total} nós...")

        print(f"--- [GRAFO] Concluído! Nós: {self.G.number_of_nodes()}, Arestas: {self.G.number_of_edges()} ---")
        return self.G