"""
CardioIA - Fase 1 | Parte 3 (Visao Computacional)
Geracao reproduzivel do conjunto de imagens de ECG a partir da base PTB-XL.

O que este script faz
---------------------
1. Baixa (se necessario) os metadados da PTB-XL (ptbxl_database.csv / scp_statements.csv)
   diretamente do PhysioNet.
2. Seleciona uma amostra BALANCEADA por superclasse diagnostica
   (NORM, MI, STTC, CD, HYP) - por padrao 24 exames por classe = 120 imagens.
   Sao usados apenas registros com laudo validado por cardiologista
   (validated_by_human == True) e com uma unica superclasse dominante,
   para que o rotulo da imagem seja limpo.
3. Baixa a forma de onda de 12 derivacoes (500 Hz, 10 s) de cada registro.
4. Renderiza cada exame como um traçado clinico padrao de 12 derivacoes
   (grade "papel de ECG" 25 mm/s, 10 mm/mV) e salva em ecg_images/*.png.
5. Escreve dados/visuais/labels.csv com o rotulo de cada imagem
   (superclasse, codigos SCP, idade, sexo, eixo, laudo textual).

Uso
---
    pip install wfdb numpy pandas matplotlib scipy
    python gerar_imagens_ecg.py --por-classe 24

Fonte dos dados
---------------
Wagner et al. (2020) "PTB-XL, a large publicly available electrocardiography
dataset", Scientific Data 7:154. PhysioNet, licenca Creative Commons
Attribution 4.0 (CC BY 4.0). https://physionet.org/content/ptb-xl/
"""
from __future__ import annotations

import argparse
import ast
import os
import ssl
import sys
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

AQUI = Path(__file__).resolve().parent
PN_BASE = "https://physionet.org/files/ptb-xl/1.0.3/"
IMG_DIR = AQUI / "ecg_images"
META_DIR = AQUI / "_ptbxl_meta"          # cache local (fica fora do Git)
SUPERCLASSES = ["NORM", "MI", "STTC", "CD", "HYP"]
SUPER_PT = {
    "NORM": "ECG normal",
    "MI": "Infarto do miocardio",
    "STTC": "Alteracao de ST/T",
    "CD": "Disturbio de conducao",
    "HYP": "Hipertrofia",
}
DERIV_ORDEM = ["I", "II", "III", "AVR", "AVL", "AVF", "V1", "V2", "V3", "V4", "V5", "V6"]

# PhysioNet exige contexto SSL padrao; em alguns Macs o urllib nao acha a CA.
_SSL_CTX = ssl.create_default_context()
try:  # fallback: usa certificados do certifi se disponivel
    import certifi

    _SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    pass


def _baixa(url: str, destino: Path) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists() and destino.stat().st_size > 0:
        return
    print(f"  baixando {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "cardioia-fase1/1.0"})
    try:
        with urllib.request.urlopen(req, context=_SSL_CTX, timeout=60) as r:
            destino.write_bytes(r.read())
    except Exception:
        # ultimo recurso: curl do sistema (traz a store de CA do macOS)
        os.system(f'curl -sL -m 90 "{url}" -o "{destino}"')
    if not destino.exists() or destino.stat().st_size == 0:
        raise RuntimeError(f"falha ao baixar {url}")


def carrega_metadados() -> tuple[pd.DataFrame, pd.DataFrame]:
    _baixa(PN_BASE + "ptbxl_database.csv", META_DIR / "ptbxl_database.csv")
    _baixa(PN_BASE + "scp_statements.csv", META_DIR / "scp_statements.csv")
    db = pd.read_csv(META_DIR / "ptbxl_database.csv", index_col="ecg_id")
    scp = pd.read_csv(META_DIR / "scp_statements.csv", index_col=0)
    return db, scp


def mapeia_superclasse(db: pd.DataFrame, scp: pd.DataFrame) -> pd.DataFrame:
    diag = scp[scp["diagnostic"] == 1.0]

    def supers(codes: str) -> list[str]:
        d = ast.literal_eval(codes)
        return sorted({diag.loc[k, "diagnostic_class"] for k in d if k in diag.index})

    db = db.copy()
    db["superclasses"] = db["scp_codes"].apply(supers)
    db["n_super"] = db["superclasses"].apply(len)
    return db


def seleciona(db: pd.DataFrame, por_classe: int, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    base = db[(db["n_super"] == 1) & (db["validated_by_human"])].copy()
    # PTB-XL anonimiza idades > 89 como 300; descartamos para manter rotulo limpo
    base = base[base["age"].between(1, 89)]
    base["super"] = base["superclasses"].apply(lambda x: x[0])
    escolhidos = []
    for sc in SUPERCLASSES:
        pool = base[base["super"] == sc]
        # metade homens / metade mulheres, espalhando faixas de idade
        alvo = por_classe
        cotas = {0: alvo // 2, 1: alvo - alvo // 2}
        for sexo, q in cotas.items():
            sub = pool[pool["sex"] == sexo].sort_values("age")
            if len(sub) > q:
                idx = np.linspace(0, len(sub) - 1, q).round().astype(int)
                sub = sub.iloc[idx]
            escolhidos.append(sub)
    sel = pd.concat(escolhidos)
    sel = sel[~sel.index.duplicated()]
    return sel.sort_values(["super", "age"])


def _filtra(sig: np.ndarray, fs: int) -> np.ndarray:
    # passa-alta 0.5 Hz (remove deriva de linha de base) + notch simplificado
    b, a = butter(1, 0.5 / (fs / 2), btype="high")
    sig = filtfilt(b, a, sig, axis=0)
    b, a = butter(4, 40 / (fs / 2), btype="low")     # remove ruido muscular/rede
    return filtfilt(b, a, sig, axis=0)


def _grade(ax, xmax: float, ymin: float, ymax: float) -> None:
    ax.set_xlim(0, xmax)
    ax.set_ylim(ymin, ymax)
    for x in np.arange(0, xmax + 1e-9, 0.2):
        ax.axvline(x, color="#e7b3b3", lw=0.5, zorder=0)
    for x in np.arange(0, xmax + 1e-9, 0.04):
        ax.axvline(x, color="#f3d6d6", lw=0.3, zorder=0)
    for y in np.arange(np.floor(ymin), np.ceil(ymax) + 1e-9, 0.5):
        ax.axhline(y, color="#e7b3b3", lw=0.5, zorder=0)
    for y in np.arange(np.floor(ymin), np.ceil(ymax) + 1e-9, 0.1):
        ax.axhline(y, color="#f3d6d6", lw=0.3, zorder=0)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def renderiza(record, meta: pd.Series, destino: Path) -> None:
    fs = int(record.fs)
    sig = record.p_signal.astype(float)
    nome2i = {n.upper(): i for i, n in enumerate(record.sig_name)}
    sig = _filtra(sig, fs)

    fig = plt.figure(figsize=(13.2, 8.0), dpi=100)
    fig.patch.set_facecolor("white")
    grid = fig.add_gridspec(4, 4, hspace=0.15, wspace=0.06,
                            left=0.03, right=0.99, top=0.90, bottom=0.06)

    seg = 2.5                      # 2,5 s por coluna (padrao 3x4)
    n = int(seg * fs)
    cols = [DERIV_ORDEM[0:3], DERIV_ORDEM[3:6], DERIV_ORDEM[6:9], DERIV_ORDEM[9:12]]
    for c, grupo in enumerate(cols):
        for r, dname in enumerate(grupo):
            ax = fig.add_subplot(grid[r, c])
            i = nome2i[dname]
            s = sig[c * n:(c + 1) * n, i]
            t = np.arange(len(s)) / fs
            _grade(ax, seg, -1.6, 1.6)
            ax.plot(t, s, color="#111111", lw=0.8)
            ax.text(0.06, 1.28, dname, fontsize=9, fontweight="bold", va="top")

    # tira de ritmo (derivacao II, 10 s)
    ax = fig.add_subplot(grid[3, :])
    i = nome2i["II"]
    s = sig[:, i]
    t = np.arange(len(s)) / fs
    _grade(ax, len(s) / fs, -1.6, 1.6)
    ax.plot(t, s, color="#111111", lw=0.8)
    ax.text(0.1, 1.3, "II (tira de ritmo)", fontsize=9, fontweight="bold", va="top")

    sexo = "Masculino" if int(meta["sex"]) == 0 else "Feminino"
    idade = "-" if pd.isna(meta["age"]) else f"{int(meta['age'])}"
    laudo = str(meta.get("report", "") or "").strip()
    titulo = (f"PTB-XL ECG #{meta.name}  |  {SUPER_PT[meta['super']]} ({meta['super']})  "
              f"|  idade {idade}  |  sexo {sexo}  |  25 mm/s, 10 mm/mV")
    fig.suptitle(titulo, fontsize=11, fontweight="bold", y=0.965)
    if laudo:
        fig.text(0.03, 0.925, f"Laudo PTB-XL (original, DE/EN): {laudo[:150]}",
                 fontsize=7.5, style="italic", color="#444")

    destino.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destino, dpi=100, facecolor="white")
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--por-classe", type=int, default=24,
                    help="exames por superclasse (padrao 24 -> 120 imagens)")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    try:
        import wfdb
    except ImportError:
        print("ERRO: instale as dependencias -> pip install wfdb scipy matplotlib pandas numpy")
        return 1

    print("1/4  metadados PTB-XL ...")
    db, scp = carrega_metadados()
    db = mapeia_superclasse(db, scp)

    print("2/4  selecionando amostra balanceada ...")
    sel = seleciona(db, args.por_classe, args.seed)
    print(sel["super"].value_counts().to_string())

    print(f"3/4  baixando e renderizando {len(sel)} exames ...")
    linhas = []
    for k, (ecg_id, meta) in enumerate(sel.iterrows(), 1):
        rel = meta["filename_hr"]                         # ex.: records500/00000/00123_hr
        pn_dir = "ptb-xl/1.0.3/" + os.path.dirname(rel)
        base = os.path.basename(rel)
        fname = f"ECG_{ecg_id:05d}_{meta['super']}.png"
        destino = IMG_DIR / fname
        try:
            rec = wfdb.rdrecord(base, pn_dir=pn_dir)
            renderiza(rec, meta, destino)
        except Exception as e:                            # pula registro problematico
            print(f"  [{k}/{len(sel)}] falhou {ecg_id}: {e}")
            continue
        linhas.append({
            "arquivo": f"ecg_images/{fname}",
            "ecg_id": ecg_id,
            "superclasse": meta["super"],
            "superclasse_pt": SUPER_PT[meta["super"]],
            "scp_codes": meta["scp_codes"],
            "idade": meta["age"],
            "sexo": "M" if int(meta["sex"]) == 0 else "F",
            "eixo_cardiaco": meta.get("heart_axis", ""),
            "laudo_ptbxl": str(meta.get("report", "") or "").strip(),
        })
        if k % 10 == 0:
            print(f"  [{k}/{len(sel)}] ok")

    labels = pd.DataFrame(linhas)
    labels.to_csv(AQUI / "labels.csv", index=False)
    print(f"4/4  {len(labels)} imagens em {IMG_DIR}")
    print(f"      rotulos em {AQUI / 'labels.csv'}")

    # copia 2 amostras curadas por classe (10 no total) para a pasta amostras/
    amostras = AQUI / "amostras"
    for f in amostras.glob("*.png"):
        f.unlink()
    for sc in SUPERCLASSES:
        cand = labels[labels["superclasse"] == sc].iloc[[0, len(labels[labels["superclasse"] == sc]) // 2]]
        for _, row in cand.iterrows():
            src = AQUI / row["arquivo"]
            if src.exists():
                (amostras / src.name).write_bytes(src.read_bytes())
    print("      amostras copiadas para amostras/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
