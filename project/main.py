import os
import sys
import time
from src.preprocessing.processor import DataProcessor
from src.preprocessing.graph_builder import GraphBuilder

# --- CONFIGURAÇÃO DE AMBIENTE ---
# Adiciona o diretório atual ao path para encontrar o pacote 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
    


# --- CONFIGURAÇÃO DE CAMINHOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'dataset.csv')
PROCESSED_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'songs.csv')
FILE_GRAPH_OBJ = 'graph.graphml'

# --- UTILITÁRIOS DE UI ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input(f"\n{Colors.WARNING}Pressione ENTER para continuar...{Colors.END}")

# --- FUNÇÕES DO SISTEMA ---
# Cada função aqui representa uma ação do menu.
# No futuro, crie novas funções aqui (ex: run_dijkstra)

def run_etl():
    """Executa o processamento de dados (DataProcessor)"""
    print(f"{Colors.HEADER}=== [ETL] PROCESSAMENTO DE DADOS ==={Colors.END}")
    
    if not os.path.exists(RAW_PATH):
        print(f"{Colors.FAIL}[ERRO] Arquivo raw não encontrado em: {RAW_PATH}{Colors.END}")
        return

    try:
        # Note que agora passamos o DIRETÓRIO de saída, não o arquivo
        processor = DataProcessor(input_path=RAW_PATH, output_dir=os.path.dirname(PROCESSED_PATH))
        
        # 1. Gera o "Lagão" de dados (Todas as músicas)
        processor.process_full_dataset(filename='songs_full.csv')
        
        # 2. Gera o "Tanque" de dados (Amostra para o Grafo) - MANTÉM O ANTIGO
        # Ajuste 'songs.csv' para o nome que seu GraphBuilder espera
        processor.process_graph_dataset(filename='songs.csv')
        
        print(f"\n{Colors.GREEN}✔ ETL Concluído com sucesso!{Colors.END}")
        
    except Exception as e:
        print(f"\n{Colors.FAIL}✖ Falha no processamento: {e}{Colors.END}")
        import traceback
        traceback.print_exc() # Isso ajuda a ver onde errou se der bug

def run_build_graph():
    """Constrói o grafo e mostra estatísticas (GraphBuilder)"""
    print(f"{Colors.HEADER}=== [GRAFO] CONSTRUÇÃO E ANÁLISE ==={Colors.END}")

    if not os.path.exists(PROCESSED_PATH):
        print(f"{Colors.WARNING}[AVISO] Dataset processado não encontrado.{Colors.END}")
        print("Execute a opção de ETL primeiro.")
        return

    # Definimos onde o arquivo GraphML será salvo
    path_graph_output = os.path.join(os.path.dirname(PROCESSED_PATH), FILE_GRAPH_OBJ)

    # Verifica se já existe para oferecer carregamento rápido
    if os.path.exists(path_graph_output):
        print(f"{Colors.BLUE}Encontrei um grafo salvo em disco!{Colors.END}")
        opt = input("Deseja carregar o existente (S) ou recriar (N)? ").strip().lower()
        if opt == 's':
            try:
                # Carregamento Rápido
                G = GraphBuilder.load_graph(path_graph_output)
                print(f"\n{Colors.GREEN}✔ Grafo Carregado do Disco!{Colors.END}")
                return  # Sai da função pois já temos o grafo
            except Exception as e:
                print(f"Erro ao carregar: {e}. Vamos recriar...")

    try:
        print("Carregando dados e montando arestas...")
        builder = GraphBuilder(PROCESSED_PATH)

        # AQUI ESTÁ A MUDANÇA: Passamos o save_path
        G = builder.build_graph(k_neighbors=5, save_path=path_graph_output)

        print(f"\n{Colors.GREEN}✔ Grafo Construído e Salvo em: {FILE_GRAPH_OBJ}{Colors.END}")
        print(f"   -> Total de Nós (Músicas): {G.number_of_nodes()}")
        print(f"   -> Total de Arestas (Conexões): {G.number_of_edges()}")

    except Exception as e:
        print(f"\n{Colors.FAIL}✖ Erro ao criar grafo: {e}{Colors.END}")

def run_algorithm_placeholder():
    """Placeholder para quando seu colega entregar o algoritmo"""
    print(f"{Colors.BLUE}=== ALGORITMO DE RECOMENDAÇÃO ==={Colors.END}")
    print("Esta funcionalidade será implementada na próxima sprint.")
    print("Aqui você chamará: DijkstraRecommender(grafo).find_path(...)")

def exit_app():
    """Encerra o programa"""
    print("\nSaindo... Até a próxima! 🎵")
    sys.exit(0)

# --- DEFINIÇÃO DO MENU ---
# Para adicionar uma nova opção, basta adicionar uma linha neste dicionário.
# Chave: O que o usuário digita.
# Valor: (Descrição para o menu, Função a ser executada).
MENU_OPTIONS = {
    "1": ("Processar Dataset (ETL)", run_etl),
    "2": ("Construir Grafo (Teste)", run_build_graph),
    "3": ("Buscar Recomendação (Em Breve)", run_algorithm_placeholder),
    "0": ("Sair", exit_app)
}

# --- LOOP PRINCIPAL ---
def main():
    while True:
        clear_screen()
        print(f"{Colors.BOLD}{Colors.BLUE}========================================{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}      SPOTIFY RECOMMENDER - CLI         {Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}========================================{Colors.END}")
        
        # Gera o menu dinamicamente baseado no dicionário
        for key, (desc, _) in MENU_OPTIONS.items():
            print(f"[{key}] {desc}")
            
        choice = input(f"\n{Colors.BOLD}Escolha uma opção: {Colors.END}").strip()

        if choice in MENU_OPTIONS:
            description, func = MENU_OPTIONS[choice]
            clear_screen()
            func() # Executa a função associada
            pause()
        else:
            print(f"\n{Colors.FAIL}Opção inválida! Tente novamente.{Colors.END}")
            time.sleep(1)

if __name__ == "__main__":
    # Garante que as pastas existam
    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
    main()