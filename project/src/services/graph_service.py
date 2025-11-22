import os
import networkx as nx
from project.src.preprocessing.graph_builder import GraphBuilder
from project.src.preprocessing.processor import DataProcessor


class GraphService:
    """
    Fachada para usar o modulo preprocessing de forma simples.
    Permite rodar o ETL completo e construir/obter o grafo
    """

    def __init__(self, root_dir: str):
        """
        Inicializa o serviço definindo a estrutura de arquivos do projeto.

        Args:
            root_dir (str): Caminho absoluto da raiz do projeto ('/project').
        """
        # --- 1. Definição Centralizada de Caminhos ---
        self.dirs = {
            'raw': os.path.join(root_dir, 'data', 'raw'),
            'processed': os.path.join(root_dir, 'data', 'processed')
        }

        #dicionario de arquivos para facilitar uso
        self.files = {
            'input_raw': os.path.join(self.dirs['raw'], 'dataset.csv'),
            'dataset_full': 'songs_full.csv',  # Nome do arquivo processado full
            'dataset_graph': 'songs.csv',  # Nome do arquivo de amostra pro grafo
            'graph_obj': os.path.join(self.dirs['processed'], 'graph.graphml')  # Arquivo do grafo salvo
        }

        # cache para não ser necessário sempre buscar do disco
        self._graph_cache = None

    def run_full_etl(self, samples_per_genre=1250) -> bool:
        """
        Executa o pipeline completo de dados:
        1. Gera a base completa (songs_full.csv)
        2. Gera a base amostral (songs.csv)
        """
        print("[Service] Iniciando Pipeline ETL...")

        if not os.path.exists(self.files['input_raw']):
            raise FileNotFoundError(f"Dataset bruto não encontrado em: {self.files['input_raw']}")

        try:
            # Instancia o processador apontando para a pasta de saída
            processor = DataProcessor(
                input_path=self.files['input_raw'],
                output_dir=self.dirs['processed']
            )


            print("   -> Processando dataset completa...")
            processor.process_full_dataset(filename=self.files['dataset_full'])


            print(f"   -> Processando amostra para grafo ({samples_per_genre}/gênero)...")
            processor.process_graph_dataset(
                filename=self.files['dataset_graph'],
                samples_per_genre=samples_per_genre
            )

            # Limpa o cache do grafo, pois os dados mudaram
            self._graph_cache = None
            print("[Service] ETL concluído com sucesso.")
            return True

        except Exception as e:
            print(f"[Service] Erro crítico no ETL: {e}")
            return False

    def get_graph(self, k_neighbors=50, force_rebuild=False) -> nx.DiGraph:
        """
        Retorna o grafo buildado e pronto para uso
        usa o dataset com amostra balanceada.

        :param k_neighbors: Numero de vizinhos para cada nó
        :param force_rebuild: se True, força a reconstrução do grafo do zero
        :return: um nx.DiGraph
        """

        # tenta usar o cache
        if self._graph_cache is not None and not force_rebuild:
            return self._graph_cache

        # tenta carregar do disco
        if os.path.exists(self.files['graph_obj']) and not force_rebuild:
            print("[Service] Carregando grafo salvo do disco...")
            try:
                self._graph_cache = GraphBuilder.load_graph(self.files['graph_obj'])
                return self._graph_cache
            except Exception as e:
                print(f"[Service] Erro ao carregar grafo salvo ({e}). Recriando...")

        # constrói do zero caso as outras opções falhem
        print("[Service] Construindo novo grafo a partir do CSV...")
        path_csv_graph = os.path.join(self.dirs['processed'], self.files['dataset_graph'])

        if not os.path.exists(path_csv_graph):
            raise FileNotFoundError("CSV do grafo não encontrado. Execute 'run_full_etl()' primeiro.")

        builder = GraphBuilder(csv_path=path_csv_graph)

        # Constrói e já salva automaticamente no caminho definido no __init__
        self._graph_cache = builder.build_graph(
            k_neighbors=k_neighbors,
            save_path=self.files['graph_obj']
        )

        return self._graph_cache