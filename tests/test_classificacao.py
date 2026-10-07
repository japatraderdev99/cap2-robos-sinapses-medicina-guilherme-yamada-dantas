import numpy as np
import pytest
from src.classificacao import carregar_dados, separar_grupos, criar_pipeline, prever_frase, treinar_avaliar


def test_particoes_sem_vazamento():
    df = separar_grupos(carregar_dados())
    assert df.groupby("grupo").particao.nunique().max() == 1
    assert df.groupby("cenario").particao.nunique().max() == 1
    assert df.groupby("frase").particao.nunique().max() == 1
    assert set(df.particao) == {"treino", "validacao", "teste"}
    for _, parte in df.groupby("particao"):
        assert set(parte.situacao) == {"baixo risco", "alto risco"}
    assert df.equals(separar_grupos(carregar_dados()))


def test_tfidf_aprende_apenas_treino():
    p = criar_pipeline().fit(["não sinto sintomatreino", "sinto dor intensa"], ["baixo risco", "alto risco"])
    antes = dict(p.named_steps["tfidf"].vocabulary_)
    p.predict(["palavraexclusivateste"])
    assert "palavraexclusivateste" not in antes
    assert p.named_steps["tfidf"].vocabulary_ == antes
    assert "nao" in antes


def test_rejeita_vazio_e_desconhecido():
    p = criar_pipeline().fit(["sinto dor", "estou bem"], ["alto risco", "baixo risco"])
    for frase in ["", "   ", None]:
        assert prever_frase(frase, p)["status"] == "entrada_vazia"
    assert prever_frase("zzzzqx", p) == {"rotulo": None, "probabilidade_modelo": None, "status": "fora_vocabulario"}
    assert prever_frase("sinto dor", p)["status"] == "ok"


def test_execucao_reproduzivel_e_evidencias(tmp_path):
    a = treinar_avaliar(output_dir=tmp_path / "a")
    b = treinar_avaliar(output_dir=tmp_path / "b")
    assert a["metricas"] == b["metricas"]
    assert a["previsoes"].equals(b["previsoes"])
    treino = a["particoes"].query("particao == 'treino'")
    isolado = criar_pipeline().fit(treino.frase, treino.situacao)
    assert a["pipeline"].named_steps["tfidf"].vocabulary_ == isolado.named_steps["tfidf"].vocabulary_
    np.testing.assert_allclose(a["pipeline"].named_steps["tfidf"].idf_, isolado.named_steps["tfidf"].idf_)
    for nome in ["metricas.json", "particoes.csv", "previsoes_teste.csv", "matriz_confusao.png", "auditoria_equidade.json"]:
        assert (tmp_path / "a" / nome).stat().st_size > 0
    assert a["metricas"]["falsos_negativos_teste"] == int(a["previsoes"].falso_negativo.sum())


def test_detecta_desalinhamento_dos_metadados(tmp_path):
    from pathlib import Path
    import pandas as pd
    origem = Path(__file__).resolve().parents[1] / "assets/dados"
    dados = pd.read_csv(origem / "frases_rotuladas.csv")
    meta = pd.read_csv(origem / "metadados_frases.csv")
    dados.iloc[::-1].to_csv(tmp_path / "frases_rotuladas.csv", index=False)
    meta.to_csv(tmp_path / "metadados_frases.csv", index=False)
    with pytest.raises(ValueError, match="Hashes"):
        carregar_dados(tmp_path)
