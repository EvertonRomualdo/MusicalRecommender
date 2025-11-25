import os
import sys

from src.services.graph_service import GraphService
from src.algorithm.search import dijkstra

# Caminho raiz do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def buscar_musicas(G, termo):
    """
    Busca músicas que contém o termo no nome ou artista.
    Retorna lista de (node_id, data, score) ordenada por relevância.
    """
    if not termo:
        return []
    
    termo = termo.lower()
    candidatos = []

    for node_id, data in G.nodes(data=True):
        nome = data.get("name", "").lower()
        artista = data.get("artist", "").lower()
        
        score = 0
        
        # Pontuação por tipo de match
        if termo == nome:
            score = 1000  # Match exato no nome
        elif termo == artista:
            score = 900   # Match exato no artista
        elif nome.startswith(termo):
            score = 500   # Começa com o termo
        elif artista.startswith(termo):
            score = 400   # Artista começa com o termo
        elif termo in nome:
            score = 100   # Contém o termo no nome
        elif termo in artista:
            score = 50    # Contém o termo no artista
        
        if score > 0:
            # Penaliza nomes muito longos (preferência por matches mais específicos)
            score -= len(nome) * 0.1
            candidatos.append((node_id, data, score))

    # Ordena por pontuação (maior primeiro)
    candidatos.sort(key=lambda x: x[2], reverse=True)
    
    return candidatos


def formatar_musica(G, node_id):
    """
    Retorna 'NOME — ARTISTA' dado o ID da música.
    """
    if node_id not in G.nodes:
        return f"[ID desconhecido: {node_id}]"
    
    data = G.nodes[node_id]
    nome = data.get("name") or "Nome desconhecido"
    artista = data.get("artist") or "Artista desconhecido"
    
    return f"{nome} — {artista}"


def listar_e_selecionar_musica(G, tipo, termo_inicial=None):
    """
    Interface interativa para buscar e selecionar uma música.
    
    Args:
        G: grafo de músicas
        tipo: "ORIGEM" ou "DESTINO" (para mensagens)
        termo_inicial: termo de busca opcional
    
    Returns:
        node_id da música selecionada ou None se cancelado
    """
    while True:
        # Se não há termo inicial, solicita
        if termo_inicial is None:
            print(f"\n🎵  Buscar música de {tipo}")
            print("    (Digite parte do nome ou artista, ou 'sair' para cancelar)")
            termo = input(" → Busca: ").strip()
            
            if termo.lower() in ['sair', 'cancelar', 'exit']:
                return None
        else:
            termo = termo_inicial
            termo_inicial = None  # Usa apenas uma vez
        
        if not termo:
            print("⚠️  Digite algo para buscar!")
            continue
        
        # Busca músicas
        resultados = buscar_musicas(G, termo)
        
        if not resultados:
            print(f"❌ Nenhuma música encontrada com '{termo}'")
            print("    Tente outro termo de busca.\n")
            continue
        
        # Limita a 20 resultados para não poluir a tela
        resultados_exibir = resultados[:20]
        
        # Exibe resultados
        print(f"\n📋 Encontradas {len(resultados)} música(s) - Mostrando top {len(resultados_exibir)}:\n")
        
        for i, (node_id, data, score) in enumerate(resultados_exibir, 1):
            nome = data.get("name", "??")
            artista = data.get("artist", "??")
            print(f"  {i:2d}. {nome} — {artista}")
        
        # Solicita seleção
        print(f"\n  0. Buscar novamente")
        print(f"  S. Sair/Cancelar")
        
        selecao = input(f"\n → Selecione o número da música de {tipo}: ").strip()
        
        # Trata cancelamento
        if selecao.lower() in ['s', 'sair', 'cancelar', 'exit']:
            return None
        
        # Trata nova busca
        if selecao == '0':
            continue
        
        # Tenta converter para número
        try:
            idx = int(selecao)
            if 1 <= idx <= len(resultados_exibir):
                node_id = resultados_exibir[idx - 1][0]
                musica_selecionada = formatar_musica(G, node_id)
                print(f"\n✔ Selecionado: {musica_selecionada}")
                return node_id
            else:
                print(f"❌ Número inválido! Digite entre 1 e {len(resultados_exibir)}")
        except ValueError:
            print("❌ Digite um número válido!")


def processar_busca_caminho(G, origem, destino):
    """Processa e exibe o resultado da busca de caminho"""
    print("\n" + "="*70)
    print(f"🔍 Calculando menor caminho entre:")
    print(f"   Origem : {formatar_musica(G, origem)}")
    print(f"   Destino: {formatar_musica(G, destino)}")
    print("="*70)
    
    if origem == destino:
        print("⚠️  Origem e destino são a mesma música!\n")
        return

    try:
        path, dist = dijkstra(G, origem, destino)

        if path is None:
            print("\n❌ Nenhum caminho encontrado entre essas músicas!")
            print("   As músicas podem estar em componentes desconexos do grafo.\n")
        else:
            print(f"\n✔ Caminho encontrado! ({len(path)} músicas, {len(path)-1} transições)\n")
            
            for i, node in enumerate(path, 1):
                prefixo = "🎯" if i == len(path) else "🎵" if i == 1 else "  "
                print(f"  {prefixo} {i:2d}. {formatar_musica(G, node)}")
            
            print(f"\n🎯 Distância total: {dist:.4f}")
            print("="*70 + "\n")
    
    except Exception as e:
        print(f"❌ Erro ao calcular caminho: {e}\n")


def menu_principal():
    """Exibe menu principal"""
    print("\n" + "="*70)
    print("🎵  SISTEMA DE BUSCA DE CAMINHOS ENTRE MÚSICAS")
    print("="*70)
    print("\n  1. Buscar caminho entre duas músicas")
    print("  0. Sair")
    
    return input("\n → Escolha uma opção: ").strip()


def executar_interface(G):
    """Interface principal do sistema"""
        
    while True:
        opcao = menu_principal()
        
        if opcao == '1':
            # Buscar caminho
            print("\n" + "─"*70)
            origem = listar_e_selecionar_musica(G, "ORIGEM")
            
            if origem is None:
                print("❌ Busca cancelada.\n")
                continue
            
            print("\n" + "─"*70)
            destino = listar_e_selecionar_musica(G, "DESTINO")
            
            if destino is None:
                print("❌ Busca cancelada.\n")
                continue
            
            processar_busca_caminho(G, origem, destino)
            
            input("\n[Pressione ENTER para continuar]")
        
        elif opcao == '0':
            print("\n👋 Até logo!\n")
            break
        
        else:
            print("❌ Opção inválida!")


def main():
    print("🔄 Carregando grafo, aguarde...")

    service = GraphService(root_dir=BASE_DIR)

    try:
        service.run_full_etl()
        G = service.get_graph(force_rebuild=True)

        if not G or len(G.nodes) == 0:
            print("❌ Grafo vazio! Verifique os dados de entrada.")
            return

        print(f"✔ Grafo carregado com sucesso!")

        # Inicia interface
        executar_interface(G)

    except FileNotFoundError as e:
        print(f"💥 Arquivo não encontrado: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando...")
    except Exception as e:
        print(f"💥 Erro inesperado: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()