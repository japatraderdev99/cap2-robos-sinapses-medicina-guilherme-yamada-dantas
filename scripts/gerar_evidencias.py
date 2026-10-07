"""Registra execução do núcleo e sondagem linguística, sem ajustar o modelo."""
from pathlib import Path
import hashlib
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
from src.extracao import analisar_frase, extrair_arquivo
from src.classificacao import prever_frase, treinar_avaliar

DESAFIOS = [
    ("afirmacao", "Sinto dor no peito e suor frio."),
    ("negacao", "Não sinto dor no peito e não tenho suor frio."),
    ("afirmacao", "Sinto falta de ar."),
    ("negacao", "Não sinto falta de ar."),
    ("familiar", "Minha mãe teve dor no peito e suor frio; eu estou bem."),
    ("fora_vocabulario", "xyzk qwrtyp"),
]


def main():
    destino = ROOT / "document/evidencias"
    resultado = treinar_avaliar(output_dir=destino)
    extracao = extrair_arquivo()
    (destino / "extracao_relatos.json").write_text(json.dumps(extracao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    desafio = {
        "protocolo": "Sondagem exploratória criada após observar a primeira avaliação. Não integra o teste reservado e não foi usada para treinar ou ajustar o classificador.",
        "interpretacao": "Compara a resposta textual a afirmação, negação e familiar. Não atribui verdade clínica nem calcula acurácia médica. Preservar a palavra não no TF-IDF não garante compreensão de negação.",
        "casos": [{"tipo": tipo, "frase": texto, "modelo": prever_frase(texto, resultado["pipeline"]), "regras": analisar_frase(texto)} for tipo, texto in DESAFIOS],
    }
    (destino / "desafio_linguistico.json").write_text(json.dumps(desafio, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fontes = sorted((ROOT / "assets/dados").glob("*")) + sorted((ROOT / "src").glob("*.py"))
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in fontes if p.is_file()}
    (destino / "manifesto_fontes.json").write_text(json.dumps(hashes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"relatos": len(extracao), "acuracia_teste": resultado["metricas"]["modelo"]["teste"]["acuracia"], "baseline": resultado["metricas"]["baseline"]["teste"]["acuracia"], "desafios": len(desafio["casos"])}, indent=2))


if __name__ == "__main__":
    main()
