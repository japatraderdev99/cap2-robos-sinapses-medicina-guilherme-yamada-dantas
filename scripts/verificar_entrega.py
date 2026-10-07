"""Confere integridade dos artefatos; --final também exige estados de entrega."""
from pathlib import Path
import argparse
import csv
import math
import hashlib
import json
import re
import sys

import nbformat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.classificacao import carregar_dados
from src.extracao import extrair_arquivo

OBRIGATORIOS = [
    "README.md", "requirements.txt", "requirements-lock.txt", "LICENSE", "app.py",
    "src/extracao.py", "src/classificacao.py", "config/entrega.json",
    "notebooks/01_extracao.ipynb", "notebooks/02_classificacao_texto.ipynb",
    "document/metodologia.md", "document/dados-e-ontologia.md", "document/governanca-e-limitacoes.md",
    "document/roteiro-video.md", "document/checklist-entrega.md", "document/revisao-independente.md",
    "document/evidencias/metricas.json", "document/evidencias/previsoes_teste.csv",
    "document/evidencias/particoes.csv", "document/evidencias/extracao_relatos.json",
    "document/evidencias/desafio_linguistico.json", "document/evidencias/manifesto_fontes.json",
]


def verificar_ecg(root=ROOT):
    """Audita evidências salvas sem carregar TensorFlow ou reexecutar treino."""
    root = Path(root)
    base = root / "extras/ecg"
    falhas = []
    try:
        def csv_rows(name):
            with (base / "data" / name).open(newline="", encoding="utf-8") as stream:
                return list(csv.DictReader(stream))

        rows = csv_rows("manifest.csv")
        labels = {r["ecg_id"]: r for r in csv_rows("labels_fase1.csv")}
        metadata = {r["ecg_id"]: r for r in csv_rows("metadata_ptbxl_subset.csv")}
        ids = [r["ecg_id"] for r in rows]
        if len(ids) != 120 or len(set(ids)) != 120 or set(ids) != set(labels) or set(ids) != set(metadata):
            falhas.append("ECG: manifesto deve conter os mesmos 120 registros únicos das fontes")
        patients = {}
        for row in rows:
            key = row["ecg_id"]
            label, meta = labels[key], metadata[key]
            if row["patient_id"] != meta["patient_id"] or row["strat_fold"] != meta["strat_fold"]:
                falhas.append(f"ECG: metadados divergem para {key}")
            if row["superclass"] != label["superclasse"] or int(row["label"]) != int(label["superclasse"] != "NORM"):
                falhas.append(f"ECG: rótulo diverge para {key}")
            patient = float(row["patient_id"])
            if patient in patients and patients[patient] != row["split"]:
                falhas.append(f"ECG: paciente cruza partições: {patient}")
            patients[patient] = row["split"]
            paths = [(base / "data/originals" / Path(label["arquivo"]).name, "source_sha256"),
                     (base / "data/clean" / f"{int(key):05d}.png", "clean_sha256")]
            for path, field in paths:
                if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row[field]:
                    falhas.append(f"ECG: hash divergente ou imagem ausente: {path.name}")
        metrics = json.loads((base / "artifacts/metrics.json").read_text())
        if set(r["split"] for r in rows) != {"train", "validation", "test"}:
            falhas.append("ECG: partições inválidas")
        for split in ("train", "validation", "test"):
            subset = [r for r in rows if r["split"] == split]
            actual = {"n": len(subset), "normal": sum(int(r["label"]) == 0 for r in subset),
                      "anormal": sum(int(r["label"]) == 1 for r in subset),
                      "patients": len(set(float(r["patient_id"]) for r in subset))}
            if actual != metrics["split"][split] or not actual["normal"] or not actual["anormal"]:
                falhas.append(f"ECG: contagem/classes divergem em {split}")
        predictions = json.loads((base / "artifacts/test_predictions.json").read_text())
        test_rows = {r["ecg_id"]: r for r in rows if r["split"] == "test"}
        if len(predictions) != len(test_rows) or {p["ecg_id"] for p in predictions} != set(test_rows):
            falhas.append("ECG: predições não correspondem exatamente ao teste")
        for prediction in predictions:
            prob = prediction["prob_anormal"]
            if (not isinstance(prob, (float, int)) or not math.isfinite(prob) or not 0 <= prob <= 1
                or prediction["label"] != int(test_rows[prediction["ecg_id"]]["label"])
                or prediction["prediction"] != int(prob >= metrics["threshold"])
                or prediction["correct"] != (prediction["label"] == prediction["prediction"])):
                falhas.append(f"ECG: predição inconsistente: {prediction['ecg_id']}")
        from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, roc_auc_score, classification_report
        y = [p["label"] for p in predictions]
        majority = int(sum(int(r["label"]) for r in rows if r["split"] == "train") > metrics["split"]["train"]["n"] / 2)
        for name, pred in [("test", [p["prediction"] for p in predictions]), ("baseline", [majority] * len(y))]:
            recomputed = {"accuracy": accuracy_score(y, pred), "balanced_accuracy": balanced_accuracy_score(y, pred),
                          "confusion_matrix": confusion_matrix(y, pred, labels=[0, 1]).tolist(),
                          "per_class": classification_report(y, pred, labels=[0, 1], target_names=["normal", "anormal"], output_dict=True, zero_division=0)}
            if name == "test":
                recomputed["roc_auc"] = roc_auc_score(y, [p["prob_anormal"] for p in predictions])
            def equal(a, b):
                if isinstance(a, dict):
                    return isinstance(b, dict) and set(a) == set(b) and all(equal(v, b[k]) for k, v in a.items())
                if isinstance(a, list):
                    return a == b
                return isinstance(b, (float, int)) and math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-8)
            if not equal(recomputed, metrics[name]):
                falhas.append(f"ECG: métricas {name} divergem das predições")
        notebook = nbformat.read(root / "notebooks/03_mlp_ecg.ipynb", as_version=4)
        nbformat.validate(notebook)
        cells = [c for c in notebook.cells if c.cell_type == "code" and c.source.strip()]
        if not cells or any(c.execution_count is None or any(o.output_type == "error" for o in c.outputs) for c in cells):
            falhas.append("ECG: notebook não executado integralmente ou contém erro")
        for name in ["artifacts/mlp_ecg.keras", "artifacts/history.json", "requirements.txt", "README.md", "data/LICENSE-PTBXL.txt"]:
            if not (base / name).is_file() or not (base / name).stat().st_size:
                falhas.append(f"ECG: artefato ausente/vazio: {name}")
    except (ValueError, KeyError, OSError, TypeError, ZeroDivisionError) as error:
        falhas.append(f"ECG: evidência inválida: {error}")
    return falhas


def pendencias_ecg(entrega, readme):
    ecg = entrega.get("extras", {}).get("ecg", {})
    pendencias = []
    url = ecg.get("video_youtube")
    if not isinstance(url, str) or not re.fullmatch(r"https://(?:www\.)?(?:youtube\.com/watch\?v=[\w-]+|youtu\.be/[\w-]+)", url):
        pendencias.append("ECG: URL real do vídeo no YouTube")
    elif url not in readme:
        pendencias.append("ECG: link do vídeo no README raiz")
    duration = ecg.get("video_duracao_segundos")
    if isinstance(duration, bool) or not isinstance(duration, (float, int)) or not 0 < duration <= 240:
        pendencias.append("ECG: duração verificada de até quatro minutos")
    if ecg.get("video_nao_listado_verificado") is not True:
        pendencias.append("ECG: visibilidade não listada do vídeo conferida")
    return pendencias


def verificar(final=False, extras=False):
    falhas = [f"Arquivo ausente: {nome}" for nome in OBRIGATORIOS if not (ROOT / nome).is_file()]
    if falhas:
        return falhas, []
    dados = carregar_dados()
    if len(extrair_arquivo()) != 10:
        falhas.append("O TXT deve ter exatamente dez relatos")
    for nome in ["01_extracao.ipynb", "02_classificacao_texto.ipynb"]:
        nb = nbformat.read(ROOT / "notebooks" / nome, as_version=4)
        nbformat.validate(nb)
        for i, cell in enumerate(nb.cells, 1):
            if cell.cell_type == "code" and cell.source.strip():
                if cell.execution_count is None:
                    falhas.append(f"{nome}: célula {i} não executada")
                if any(o.output_type == "error" for o in cell.outputs):
                    falhas.append(f"{nome}: célula {i} contém erro")
    manifesto = json.loads((ROOT / "document/evidencias/manifesto_fontes.json").read_text())
    for nome, esperado in manifesto.items():
        if not (ROOT / nome).exists() or hashlib.sha256((ROOT / nome).read_bytes()).hexdigest() != esperado:
            falhas.append(f"Fonte modificada após evidências: {nome}")
    metricas = json.loads((ROOT / "document/evidencias/metricas.json").read_text())
    total = sum(c["frases"] for c in metricas["contagens"].values())
    if total != len(dados):
        falhas.append("Contagens das evidências divergem do dataset")
    readme = (ROOT / "README.md").read_text()
    for destino in re.findall(r"\]\(([^)]+)\)", readme):
        if not destino.startswith(("https://", "http://", "#")) and not (ROOT / destino.split("#")[0]).exists():
            falhas.append(f"Link local quebrado: {destino}")
    entrega = json.loads((ROOT / "config/entrega.json").read_text())
    if entrega["aluno"] != "Guilherme Yamada Dantas" or entrega["rm"] != "568506":
        falhas.append("Identificação acadêmica incorreta")
    pendencias = []
    if not entrega["publicacao_codigo_verificada"]:
        pendencias.append("Publicação do código no repositório público")
    url = entrega["video_youtube"]
    if not isinstance(url, str) or not re.fullmatch(r"https://(?:www\.)?(?:youtube\.com/watch\?v=[\w-]+|youtu\.be/[\w-]+)", url):
        pendencias.append("URL real do vídeo no YouTube")
    elif url not in readme:
        pendencias.append("Link do vídeo no README")
    duracao = entrega["video_duracao_segundos"]
    if not isinstance(duracao, (int, float)) or not 0 < duracao <= 240:
        pendencias.append("Duração verificada de até quatro minutos")
    if not entrega["video_nao_listado_verificado"]:
        pendencias.append("Visibilidade não listada do vídeo conferida")
    if not entrega["envio_plataforma_confirmado"]:
        pendencias.append("Envio e comprovante na plataforma FIAP")
    if extras:
        falhas.extend(verificar_ecg())
        pendencias.extend(pendencias_ecg(entrega, readme))
    return falhas, pendencias


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--extras", action="store_true", help="Audita também evidências e vídeo do ECG, sem TensorFlow")
    args = parser.parse_args()
    try:
        falhas, pendencias = verificar(args.final, args.extras)
    except (ValueError, KeyError, OSError) as erro:
        falhas, pendencias = [str(erro)], []
    print(json.dumps({"artefatos_locais": "falhou" if falhas else "verificados", "modo_final": args.final,
                      "entrega_final": "pendente" if falhas or pendencias else "registros_completos",
                      "falhas": falhas, "pendencias_entrega": pendencias}, ensure_ascii=False, indent=2))
    sys.exit(bool(falhas or (args.final and pendencias)))
