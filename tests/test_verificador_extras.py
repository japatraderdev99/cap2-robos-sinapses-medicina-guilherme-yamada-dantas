"""Falhas de proveniência e avaliação devem bloquear a auditoria do extra."""
import csv
import json
import shutil
from pathlib import Path

import pytest

from scripts.verificar_entrega import ROOT, pendencias_ecg, verificar_ecg


@pytest.fixture
def pacote(tmp_path):
    # Cópia real isolada: nunca modifica evidências científicas entregues.
    base = tmp_path / 'extras/ecg'
    base.mkdir(parents=True)
    for folder in ['data', 'artifacts']:
        shutil.copytree(ROOT / 'extras/ecg' / folder, base / folder)
    for name in ['README.md', 'requirements.txt']:
        shutil.copyfile(ROOT / 'extras/ecg' / name, base / name)
    (tmp_path / 'notebooks').mkdir()
    shutil.copyfile(ROOT / 'notebooks/03_mlp_ecg.ipynb', tmp_path / 'notebooks/03_mlp_ecg.ipynb')
    return tmp_path


def alterar_csv(path, change):
    with path.open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    change(rows)
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def test_evidencias_reais_consistentes():
    assert verificar_ecg(ROOT) == []


def test_imagem_adulterada_detectada(pacote):
    image = next((pacote / 'extras/ecg/data/clean').glob('*.png'))
    image.write_bytes(image.read_bytes() + b'alteracao')
    assert any('hash divergente' in x for x in verificar_ecg(pacote))


def test_paciente_cruzando_particoes_detectado(pacote):
    path = pacote / 'extras/ecg/data/manifest.csv'
    def mutate(rows):
        a = next(r for r in rows if r['split'] == 'train')
        b = next(r for r in rows if r['split'] == 'test')
        b['patient_id'] = a['patient_id']
    alterar_csv(path, mutate)
    assert any('paciente cruza' in x for x in verificar_ecg(pacote))


def test_metrica_inflada_detectada(pacote):
    path = pacote / 'extras/ecg/artifacts/metrics.json'
    data = json.loads(path.read_text())
    data['test']['accuracy'] = 1.0
    path.write_text(json.dumps(data))
    assert any('métricas test divergem' in x for x in verificar_ecg(pacote))


def test_predicao_de_treino_no_teste_detectada(pacote):
    with (pacote / 'extras/ecg/data/manifest.csv').open() as stream:
        train = next(r for r in csv.DictReader(stream) if r['split'] == 'train')
    path = pacote / 'extras/ecg/artifacts/test_predictions.json'
    data = json.loads(path.read_text())
    data[0]['ecg_id'] = train['ecg_id']
    path.write_text(json.dumps(data))
    assert any('exatamente ao teste' in x for x in verificar_ecg(pacote))


def test_notebook_nao_executado_detectado(pacote):
    path = pacote / 'notebooks/03_mlp_ecg.ipynb'
    data = json.loads(path.read_text())
    next(c for c in data['cells'] if c['cell_type'] == 'code')['execution_count'] = None
    path.write_text(json.dumps(data))
    assert any('notebook não executado' in x for x in verificar_ecg(pacote))


def test_video_requer_url_link_duracao_e_visibilidade():
    ecg = {'video_youtube': 'https://youtu.be/abcdefghijk', 'video_duracao_segundos': 195,
           'video_nao_listado_verificado': True}
    config = {'extras': {'ecg': ecg}}
    assert pendencias_ecg(config, ecg['video_youtube']) == []
    assert any('README' in x for x in pendencias_ecg(config, ''))
    ecg['video_nao_listado_verificado'] = False
    ecg['video_duracao_segundos'] = 241
    assert len(pendencias_ecg(config, ecg['video_youtube'])) == 2
    assert len(pendencias_ecg({}, '')) == 3
