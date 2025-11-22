import pandas as pd
import os


class DataProcessor:
    """
    Processador de Dados ETL.
    """

    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir

        # Define as colunas exatas que queremos manter do original
        # Certifique-se que seu CSV tem EXATAMENTE esses nomes
        self.REQUIRED_COLS = [
            'track_id',
            'track_name',
            'artists',
            'track_genre',
            'tempo',  # Antes era renomeado para 'bpm'
            'danceability',
            'energy',
            'valence',
            'acousticness',
            'instrumentalness'
        ]

    def _load_and_filter(self):
        """
        [INTERNO] Carrega, seleciona colunas e remove duplicatas/nulos.
        """
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Arquivo raw não encontrado: {self.input_path}")

        print("   -> Lendo CSV bruto...")
        df = pd.read_csv(self.input_path, low_memory=False)


        # 1. Filtrar apenas as colunas essenciais
        # Verifica quais colunas da lista existem no dataframe
        cols_to_keep = [c for c in self.REQUIRED_COLS if c in df.columns]

        if len(cols_to_keep) < len(self.REQUIRED_COLS):
            missing = set(self.REQUIRED_COLS) - set(cols_to_keep)
            print(f"   [AVISO] Colunas faltando no CSV original: {missing}")

        df = df[cols_to_keep]

        # 2. Limpeza
        initial_len = len(df)
        df = df.dropna()

        # Remove duplicatas baseadas no ID original (track_id)
        if 'track_id' in df.columns:
            df = df.drop_duplicates(subset='track_id')

        print(f"   -> Limpeza: {initial_len} linhas -> {len(df)} linhas válidas.")
        return df

    def process_full_dataset(self, filename='songs_full.csv'):
        """Processa e salva TODO o dataset limpo."""
        print(f"\n[ETL] Gerando Dataset COMPLETO ({filename})...")

        df = self._load_and_filter()

        os.makedirs(self.output_dir, exist_ok=True)
        full_path = os.path.join(self.output_dir, filename)
        df.to_csv(full_path, index=False)

        print(f"   ✔ Arquivo Mestre salvo em: {full_path}")
        return full_path

    def process_graph_dataset(self, filename='songs.csv', samples_per_genre=800):
        """Processa e salva uma AMOSTRA balanceada por gênero."""
        print(f"\n[ETL] Gerando Dataset para GRAFO ({filename})...")

        df = self._load_and_filter()

        target_genres = [
            'pop', 'rock', 'metal', 'classical', 'acoustic',
            'piano', 'dance', 'brazil', 'jazz', 'hip-hop',
            'electronic', 'reggae'
        ]

        df_final = pd.DataFrame()
        print(f"   -> Filtrando gêneros alvo e coletando até {samples_per_genre} amostras...")

        # Verifica se temos a coluna de gênero para filtrar
        col_genre = 'track_genre' if 'track_genre' in df.columns else None

        if col_genre:
            for genre in target_genres:
                df_genre = df[df[col_genre] == genre]

                if len(df_genre) > samples_per_genre:
                    df_genre = df_genre.sample(n=samples_per_genre, random_state=42)

                df_final = pd.concat([df_final, df_genre])
        else:
            print("   [!] Coluna de gênero não encontrada. Fazendo amostragem simples.")
            df_final = df.sample(n=min(len(df), samples_per_genre * 12), random_state=42)

        os.makedirs(self.output_dir, exist_ok=True)
        graph_path = os.path.join(self.output_dir, filename)
        df_final.to_csv(graph_path, index=False)

        print(f"   ✔ Arquivo do Grafo salvo em: {graph_path}")
        print(f"   -> Nós prontos para o grafo: {len(df_final)}")
        return graph_path