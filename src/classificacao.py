"""Classificador acadêmico de relatos sintéticos; não estima risco clínico."""
from pathlib import Path
import hashlib
import json
import platform
import unicodedata

import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
ROTULOS = ["baixo risco", "alto risco"]


def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    return " ".join(texto.lower().split())


def carregar_dados(data_dir=None):
    """Valida o contrato e associa metadados pela ordem documentada."""
    base = Path(data_dir) if data_dir is not None else ROOT / "assets/dados"
    dados = pd.read_csv(base / "frases_rotuladas.csv", keep_default_na=False)
    meta = pd.read_csv(base / "metadados_frases.csv", keep_default_na=False)
    if list(dados.columns) != ["frase", "situacao"]:
        raise ValueError("Dataset deve conter somente frase,situacao, nesta ordem")
    if not {"frase_id", "grupo", "cenario"}.issubset(meta.columns) or len(dados) != len(meta):
        raise ValueError("Metadados incompatíveis com dataset")
    if "frase_sha256" in meta.columns:
        hashes = dados.frase.map(lambda texto: hashlib.sha256(texto.encode("utf-8")).hexdigest())
        if not hashes.equals(meta.frase_sha256):
            raise ValueError("Hashes de frases não correspondem: metadados fora de ordem ou dados alterados")
    if set(dados.situacao) != set(ROTULOS):
        raise ValueError(f"Rótulos devem ser {ROTULOS}")
    if dados.frase.map(_normalizar).eq("").any() or dados.frase.map(_normalizar).duplicated().any():
        raise ValueError("Frases vazias ou duplicadas após normalização")
    if meta.frase_id.duplicated().any() or meta[["frase_id", "grupo", "cenario"]].eq("").any().any():
        raise ValueError("Identificadores inválidos")
    df = pd.concat([meta[["frase_id", "grupo", "cenario"]], dados], axis=1)
    if df.groupby("grupo").situacao.nunique().max() != 1:
        raise ValueError("Cada grupo deve ter um único rótulo")
    if df.groupby("cenario").grupo.nunique().max() != 1:
        raise ValueError("Cada cenário deve pertencer a um único grupo")
    return df


def separar_grupos(dados):
    """60/20/20 por grupo, estratificados pelo rótulo; sem paráfrases cruzadas."""
    grupos = dados.groupby("grupo", sort=True).situacao.first()
    treino, reserva = train_test_split(grupos.index, test_size=.4, stratify=grupos.values, random_state=SEED)
    validacao, teste = train_test_split(reserva, test_size=.5, stratify=grupos.loc[reserva].values, random_state=SEED)
    mapa = {g: nome for nome, ids in [("treino", treino), ("validacao", validacao), ("teste", teste)] for g in ids}
    resultado = dados.copy()
    resultado["particao"] = resultado.grupo.map(mapa)
    return resultado


def criar_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode", lowercase=True, stop_words=None)),
        ("classificador", LogisticRegression(C=1.0, max_iter=1000, random_state=SEED, solver="liblinear")),
    ])


def prever_frase(frase, pipeline):
    """Probabilidade é confiança estatística do modelo, jamais risco médico."""
    if not isinstance(frase, str) or not frase.strip():
        return {"rotulo": None, "probabilidade_modelo": None, "status": "entrada_vazia"}
    if pipeline.named_steps["tfidf"].transform([frase]).nnz == 0:
        return {"rotulo": None, "probabilidade_modelo": None, "status": "fora_vocabulario"}
    p = pipeline.predict_proba([frase])[0]
    indice = int(np.argmax(p))
    return {"rotulo": str(pipeline.classes_[indice]), "probabilidade_modelo": float(p[indice]), "status": "ok"}


def _metricas(real, previsto):
    return {
        "acuracia": float(accuracy_score(real, previsto)),
        "por_classe": classification_report(real, previsto, labels=ROTULOS, output_dict=True, zero_division=0),
        "ordem_rotulos": ROTULOS,
        "matriz_confusao": confusion_matrix(real, previsto, labels=ROTULOS).tolist(),
    }


def auditoria_equidade(pipeline):
    """Sondagem contrafactual pequena; não valida equidade clínica/populacional."""
    pares = []
    sintomas = ["sinto pressão intensa no peito e falta de ar em repouso", "sinto dor leve no braço após exercício e melhora com repouso", "não sinto dor no peito nem falta de ar"]
    for eixo, variantes in [("genero", ["Sou homem", "Sou mulher"]), ("idade", ["Tenho 25 anos", "Tenho 75 anos"])]:
        for relato in sintomas:
            textos = [f"{v}, {relato}." for v in variantes]
            resultados = [prever_frase(t, pipeline) for t in textos]
            pares.append({"eixo": eixo, "frases": textos, "previsoes": resultados, "mudou_rotulo": resultados[0]["rotulo"] != resultados[1]["rotulo"], "diferenca_probabilidade_classe_prevista": abs(resultados[0]["probabilidade_modelo"] - resultados[1]["probabilidade_modelo"])})
    return {"natureza": "Exploratório: 3 pares por eixo, sem inferência sobre equidade ou validade clínica. Idade pode ser clinicamente relevante; esta sondagem mede somente sensibilidade textual.", "pares": pares}


def treinar_avaliar(data_dir=None, output_dir=None):
    base = Path(data_dir) if data_dir is not None else ROOT / "assets/dados"
    dados = carregar_dados(base)
    particoes = separar_grupos(dados)
    conjuntos = {p: particoes.loc[particoes.particao == p] for p in ["treino", "validacao", "teste"]}
    treino = conjuntos["treino"]
    pipeline = criar_pipeline().fit(treino.frase, treino.situacao)
    baseline = DummyClassifier(strategy="most_frequent", random_state=SEED).fit(np.zeros((len(treino), 1)), treino.situacao)
    metricas = {
        "seed": SEED,
        "arquivos_sha256": {nome: hashlib.sha256((base / nome).read_bytes()).hexdigest() for nome in ["frases_rotuladas.csv", "metadados_frases.csv"]},
        "versoes": {"python": platform.python_version(), "sklearn": sklearn.__version__, "pandas": pd.__version__, "numpy": np.__version__},
        "protocolo": "Split estratificado por grupo 60/20/20; TF-IDF ajustado somente em treino; hiperparâmetros pré-fixados; teste não usado para ajuste.",
        "dataset_sha256": hashlib.sha256(dados.to_csv(index=False).encode()).hexdigest(),
        "contagens": {p: {"frases": len(d), "grupos": int(d.grupo.nunique()), "classes": {str(k): int(v) for k, v in d.situacao.value_counts().items()}} for p, d in conjuntos.items()},
        "vocabulario_treino": len(pipeline.named_steps["tfidf"].vocabulary_),
        "modelo": {}, "baseline": {},
    }
    for nome, d in conjuntos.items():
        metricas["modelo"][nome] = _metricas(d.situacao, pipeline.predict(d.frase))
        metricas["baseline"][nome] = _metricas(d.situacao, baseline.predict(np.zeros((len(d), 1))))
    teste = conjuntos["teste"]
    previsoes = teste[["frase_id", "grupo", "frase"]].copy()
    previsoes["real"] = teste.situacao
    previsoes["previsto"] = pipeline.predict(teste.frase)
    previsoes["probabilidade_modelo"] = pipeline.predict_proba(teste.frase).max(axis=1)
    previsoes["erro"] = previsoes.real != previsoes.previsto
    previsoes["falso_negativo"] = previsoes.real.eq("alto risco") & previsoes.previsto.eq("baixo risco")
    metricas["erros_teste"] = previsoes.loc[previsoes.erro].to_dict(orient="records")
    metricas["falsos_negativos_teste"] = int(previsoes.falso_negativo.sum())
    destino = Path(output_dir) if output_dir is not None else ROOT / "document/evidencias"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (destino / "auditoria_equidade.json").write_text(json.dumps(auditoria_equidade(pipeline), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    particoes.to_csv(destino / "particoes.csv", index=False)
    previsoes.to_csv(destino / "previsoes_teste.csv", index=False)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from sklearn.metrics import ConfusionMatrixDisplay
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay(np.array(metricas["modelo"]["teste"]["matriz_confusao"]), display_labels=ROTULOS).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set(title="Teste sintético — grupos inéditos", xlabel="Rótulo previsto", ylabel="Rótulo simulado de referência")
    fig.tight_layout()
    fig.savefig(destino / "matriz_confusao.png", dpi=160)
    plt.close(fig)
    return {"pipeline": pipeline, "metricas": metricas, "particoes": particoes, "previsoes": previsoes}


if __name__ == "__main__":
    resultado = treinar_avaliar()
    print(json.dumps({"acuracia_teste": resultado["metricas"]["modelo"]["teste"]["acuracia"], "baseline_teste": resultado["metricas"]["baseline"]["teste"]["acuracia"], "falsos_negativos": resultado["metricas"]["falsos_negativos_teste"]}, indent=2))
