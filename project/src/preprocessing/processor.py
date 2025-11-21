import pandas as pd
import os

class DataProcessor:
    """
    Responsável por carregar, limpar, filtrar e salvar o dataset musical.
    """

    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path
        
        # Isso evita carregar 120 mil músicas
        self.TARGET_GENRES = [
            'pop', 'rock', 'metal', 'classical', 
            'acoustic', 'piano', 'dance', 'brazil'
        ]
        
        # Quantas músicas por gênero
        self.SAMPLES_PER_GENRE = 300

    def process(self):
        
        print(f"--- [ETL] Iniciando processamento ---")
        
        # Validação
        if not os.path.exists(self.input_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.input_path}")

        # Carregamento
        print("-> Carregando dataset bruto...")
        try:
            df = pd.read_csv(self.input_path)
        except Exception as e:
            raise Exception(f"Erro ao ler CSV: {e}")

        # Filtragem e Amostragem
        df_final = pd.DataFrame()
        
        # Verifica nome da coluna de gênero (segurança)
        col_genre = 'track_genre' if 'track_genre' in df.columns else 'genre'

        print("-> Filtrando gêneros e balanceando dados...")
        for genre in self.TARGET_GENRES:
            # Filtra apenas o gênero atual
            df_genre = df[df[col_genre] == genre]
            
            # Pega uma amostra aleatória se houver dados suficientes
            if len(df_genre) >= self.SAMPLES_PER_GENRE:
                df_genre = df_genre.sample(n=self.SAMPLES_PER_GENRE, random_state=42)
            
            df_final = pd.concat([df_final, df_genre])

        # Limpeza e Renomeação
        column_mapping = {
            'track_id': 'id',
            'track_name': 'name',
            'artists': 'artist',
            'track_genre': 'genre',
            'tempo': 'bpm',  # Você pediu como BPM
            'danceability': 'danceability',
            'energy': 'energy',
            'valence': 'valence',
            'acousticness': 'acousticness',
            'instrumentalness': 'instrumentalness'
        }

        # Renomeia
        df_final = df_final.rename(columns=column_mapping)

        # Seleciona APENAS as colunas desejadas
        cols_to_keep = list(column_mapping.values())
        
        # Garante que só tentamos acessar colunas que existem após renomear
        df_final = df_final[[c for c in cols_to_keep if c in df_final.columns]]

        # Remove duplicatas e valores nulos
        df_final = df_final.drop_duplicates(subset='id').dropna()

        # Salvamento
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        df_final.to_csv(self.output_path, index=False)
        
        print(f"-> Dataset limpo salvo em: {self.output_path}")
        print(f"-> Total de músicas processadas: {len(df_final)}")
        print("--- [ETL] Concluído com sucesso ---")