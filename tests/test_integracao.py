"""Revisão independente: contratos entre dados, split e aprendizado."""
from src.classificacao import carregar_dados, separar_grupos, criar_pipeline, prever_frase
from src.extracao import extrair_arquivo


def test_cenarios_nao_cruzam_particoes():
    dados = separar_grupos(carregar_dados())
    assert set(dados.particao) == {'treino', 'validacao', 'teste'}
    assert dados.groupby('grupo').particao.nunique().max() == 1
    assert dados.groupby('cenario').particao.nunique().max() == 1
    assert dados.groupby('frase_id').particao.nunique().max() == 1
    assert all(set(d.situacao) == {'alto risco', 'baixo risco'}
               for _, d in dados.groupby('particao'))


def test_vocabulario_nao_aprende_texto_reservado():
    dados = separar_grupos(carregar_dados())
    treino = dados.loc[dados.particao == 'treino']
    pipeline = criar_pipeline().fit(treino.frase, treino.situacao)
    vocabulario = dict(pipeline.named_steps['tfidf'].vocabulary_)
    reservado = dados.loc[dados.particao == 'teste', 'frase'] + ' sentinelaexclusivaqa'
    pipeline.predict(reservado)
    assert pipeline.named_steps['tfidf'].vocabulary_ == vocabulario
    assert 'sentinelaexclusivaqa' not in vocabulario
    assert prever_frase('sentinelaexclusivaqa', pipeline)['status'] == 'fora_vocabulario'


def test_dez_relatos_integrados_com_mapa():
    resultados = extrair_arquivo()
    assert len(resultados) == 10
    assert all(r['frase'].strip() for r in resultados)
    assert any(r['hipoteses'] for r in resultados)
    assert any(r['status'] == 'sem_correspondencia' for r in resultados)
    assert any(r['negados'] for r in resultados)
