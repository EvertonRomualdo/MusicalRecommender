# project/tests/test_graph_service.py
import os
import pytest
import networkx as nx
from unittest.mock import patch, MagicMock
from src.services.graph_service import GraphService


def test_service_initialization(tmp_path):
    root = tmp_path
    service = GraphService(str(root))

    assert "raw" in service.dirs
    assert "processed" in service.dirs
    assert service.files["graph_obj"].endswith("graph.graphml")


@patch("src.services.graph_service.DataProcessor")
def test_run_full_etl_success(mock_dp, tmp_path):
    root = tmp_path
    service = GraphService(str(root))

    os.makedirs(service.dirs["raw"], exist_ok=True)
    with open(service.files['input_raw'], "w") as f:
        f.write("id,name\n1,A")

    instance = mock_dp.return_value

    result = service.run_full_etl(samples_per_genre=100)

    assert result is True
    instance.process_full_dataset.assert_called_once()
    instance.process_graph_dataset.assert_called_once()


def test_run_full_etl_missing_file(tmp_path):
    service = GraphService(str(tmp_path))
    with pytest.raises(FileNotFoundError):
        service.run_full_etl()


@patch("src.services.graph_service.GraphBuilder")
def test_get_graph_from_cache(mock_builder, tmp_path):
    service = GraphService(str(tmp_path))

    dummy_graph = nx.DiGraph()
    service._graph_cache = dummy_graph

    g = service.get_graph()

    assert g is dummy_graph
    mock_builder.load_graph.assert_not_called()


@patch("src.services.graph_service.GraphBuilder")
def test_get_graph_load_from_disk(mock_builder, tmp_path):
    service = GraphService(str(tmp_path))

    os.makedirs(service.dirs["processed"], exist_ok=True)
    with open(service.files["graph_obj"], "w") as f:
        f.write("<graphml>fake</graphml>")

    dummy_graph = nx.DiGraph()
    mock_builder.load_graph.return_value = dummy_graph

    g = service.get_graph()
    assert g is dummy_graph
    mock_builder.load_graph.assert_called_once()


@patch("src.services.graph_service.GraphBuilder")
def test_get_graph_build_new(mock_builder, tmp_path):
    service = GraphService(str(tmp_path))

    os.makedirs(service.dirs["processed"], exist_ok=True)
    csv_path = os.path.join(service.dirs["processed"], service.files["dataset_graph"])
    with open(csv_path, "w") as f:
        f.write("track_id,track_name,artists\n1,A,B")

    dummy_graph = nx.DiGraph()
    instance = mock_builder.return_value
    instance.build_graph.return_value = dummy_graph

    g = service.get_graph(k_neighbors=20)

    assert g is dummy_graph
    instance.build_graph.assert_called_once()


def test_get_graph_missing_csv(tmp_path):
    service = GraphService(str(tmp_path))
    with pytest.raises(FileNotFoundError):
        service.get_graph()

@patch("src.services.graph_service.GraphBuilder")
def test_force_rebuild(mock_builder, tmp_path):
    service = GraphService(str(tmp_path))

    os.makedirs(service.dirs["processed"], exist_ok=True)
    csv_path = os.path.join(service.dirs["processed"], service.files["dataset_graph"])
    with open(csv_path, "w") as f:
        f.write("track_id,track_name,artists\n1,A,B")

    service._graph_cache = nx.DiGraph()

    dummy_graph = nx.DiGraph()
    instance = mock_builder.return_value
    instance.build_graph.return_value = dummy_graph

    g = service.get_graph(force_rebuild=True)

    assert g is dummy_graph
    instance.build_graph.assert_called_once()


@patch("src.services.graph_service.GraphBuilder")
def test_load_graph_failure_builds_new(mock_builder, tmp_path):
    service = GraphService(str(tmp_path))

    os.makedirs(service.dirs["processed"], exist_ok=True)
    with open(service.files["graph_obj"], "w") as f:
        f.write("invalid")

    mock_builder.load_graph.side_effect = Exception("erro")

    csv_graph = os.path.join(service.dirs["processed"], service.files["dataset_graph"])
    with open(csv_graph, "w") as f:
        f.write("track_id,track_name,artists\n1,A,B")

    dummy_graph = nx.DiGraph()
    instance = mock_builder.return_value
    instance.build_graph.return_value = dummy_graph

    g = service.get_graph()

    assert g is dummy_graph
    instance.build_graph.assert_called_once()

def test_graph_service_corrupted_graph(tmp_path, monkeypatch):
    """
    Testa o caminho em que o graph_service tenta carregar o grafo salvo,
    mas o arquivo está corrompido e load_graph levanta erro.
    Isso cobre as linhas 71-73 do graph_service.
    """

    root = tmp_path
    raw_dir = root / "data" / "raw"
    processed_dir = root / "data" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    csv_path = raw_dir / "dataset.csv"
    csv_path.write_text(
        "track_id,track_name,artists,danceability,energy,valence,tempo,acousticness,instrumentalness\n"
        "1,A,B,0.5,0.6,0.7,120,0.1,0.0\n"
        "2,C,D,0.6,0.5,0.6,130,0.2,0.0\n"
    )

    from src.services.graph_service import GraphService
    service = GraphService(str(root))
    service.run_full_etl(samples_per_genre=1)

    corrupted_graph_path = processed_dir / "graph.graphml"
    corrupted_graph_path.write_text("isso não é um grafo válido")

    def fake_load_graph(path):
        raise ValueError("arquivo inválido")

    monkeypatch.setattr(
        "src.preprocessing.graph_builder.GraphBuilder.load_graph",
        fake_load_graph
    )

    G = service.get_graph(k_neighbors=1, force_rebuild=False)

    assert G is not None
    assert G.number_of_nodes() > 0

@patch("src.services.graph_service.DataProcessor")
def test_run_full_etl_raises_exception(mock_dp, tmp_path):
    """
    Testa o caminho em que o ETL levanta uma exceção e retorna False.
    Isso cobre o bloco 'except Exception as e' dentro de run_full_etl.
    """
    service = GraphService(str(tmp_path))

    os.makedirs(service.dirs["raw"], exist_ok=True)
    with open(service.files["input_raw"], "w") as f:
        f.write("track_id,track_name\n1,A")

    instance = mock_dp.return_value
    instance.process_full_dataset.side_effect = Exception("erro crítico")

    result = service.run_full_etl(samples_per_genre=10)

    assert result is False
    instance.process_full_dataset.assert_called_once()
