import pandas as pd
import os

class DataProcessor:
    """
    Processador de Dados ETL.
    Gera dois tipos de artefatos:
    Full Dataset: Todas as músicas limpas com os metadados necessarios
    Graph Dataset: Amostra balanceada (para construção eficiente do grafo).
    """

    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir
        
        # Mapeamento
        self.COLUMN_MAPPING = {
            'track_id': 'id',
            'track_name': 'name',
            'artists': 'artist',
            'track_genre': 'genre',
            'tempo': 'bpm',
            'danceability': 'danceability',
            'energy': 'energy',
            'valence': 'valence',
            'acousticness': 'acousticness',
            'instrumentalness': 'instrumentalness'
        }
        
        # Colunas essenciais que não podem ser nulas
        self.REQUIRED_COLS = list(self.COLUMN_MAPPING.values())

    def _load_and_standardize(self):
        """
        [MÉTODO INTERNO] 
        Carrega o Raw, renomeia colunas e remove nulos/duplicatas.
        Não aplica filtros de gênero nem amostragem.
        """
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Arquivo raw não encontrado: {self.input_path}")

        print("   -> Lendo CSV bruto...")
        
        df = pd.read_csv(self.input_path, low_memory=False)
        
        # Ajuste de nomes de colunas
        if 'genre' in df.columns and 'track_genre' not in df.columns:
            df.rename(columns={'genre': 'track_genre'}, inplace=True)

        # 2Renomear para o padrão
        df.rename(columns=self.COLUMN_MAPPING, inplace=True)

        # Filtra apenas as colunas que existem no DF após renomear
        cols_to_keep = [c for c in self.REQUIRED_COLS if c in df.columns]
        df = df[cols_to_keep]

        # Limpeza Pesada
        initial_len = len(df)
        df = df.dropna() # Remove linhas com qualquer dado faltando
        df = df.drop_duplicates(subset='id') # Garante IDs únicos
        
        print(f"   -> Limpeza: {initial_len} linhas -> {len(df)} linhas válidas.")
        return df

    def process_full_dataset(self, filename='songs_full.csv'):
        """
        Processa e salva TODO o dataset limpo.
        """
        print(f"\n[ETL] Gerando Dataset COMPLETO ({filename})...")
        
        df = self._load_and_standardize()
        
        # Salvar
        os.makedirs(self.output_dir, exist_ok=True)
        full_path = os.path.join(self.output_dir, filename)
        df.to_csv(full_path, index=False)
        
        print(f"   ✔ Arquivo Mestre salvo em: {full_path}")
        return full_path

    def process_graph_dataset(self, filename='songs.csv', samples_per_genre=800):
        """
        Processa e salva apenas uma AMOSTRA balanceada.
        Por padrão usa 800 por genero
        """
        print(f"\n[ETL] Gerando Dataset para GRAFO ({filename})...")
        
        df = self._load_and_standardize()
        
        # Lógica de Amostragem
        target_genres = target_genres = [
            'pop', 'rock', 'metal', 'classical', 'acoustic', 
            'piano', 'dance', 'brazil', 'jazz', 'hip-hop', 
            'electronic', 'reggae'
        ]
        df_final = pd.DataFrame()
        
        print(f"   -> Filtrando gêneros alvo e coletando {samples_per_genre} amostras...")
        
        if 'genre' in df.columns:
            for genre in target_genres:
                # Filtra gênero
                df_genre = df[df['genre'] == genre]
                
                # Pega amostra aleatória
                if len(df_genre) > samples_per_genre:
                    df_genre = df_genre.sample(n=samples_per_genre, random_state=42)
                
                df_final = pd.concat([df_final, df_genre])

        # Salvar
        os.makedirs(self.output_dir, exist_ok=True)
        graph_path = os.path.join(self.output_dir, filename)
        df_final.to_csv(graph_path, index=False)
        
        #relatorio
        print(f"   ✔ Arquivo do Grafo salvo em: {graph_path}")
        print(f"   -> Nós prontos para o grafo: {len(df_final)}")
        return graph_path