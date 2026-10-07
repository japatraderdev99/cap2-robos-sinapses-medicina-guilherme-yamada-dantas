"""Cria ZIP da entrega local sem ambientes, caches ou materiais da disciplina."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
PASTAS = [".github", ".streamlit", "assets", "config", "document", "notebooks", "scripts", "src", "tests", "extras"]
EXCLUIDOS = {"__pycache__", ".ipynb_checkpoints", ".DS_Store", ".venv", ".cache", ".pytest_cache", ".git", "node_modules", "tmp", "dist"}
ARQUIVOS = ["README.md", "LICENSE", ".gitignore", "requirements.txt", "requirements-lock.txt", "pytest.ini", "app.py"]


def empacotar(saida):
    caminhos = [ROOT / nome for nome in ARQUIVOS]
    for nome in PASTAS:
        caminhos.extend(p for p in (ROOT / nome).rglob("*") if p.is_file()
                        and not any(parte in EXCLUIDOS for parte in p.relative_to(ROOT).parts)
                        and not p.name.startswith(".env") and p.suffix not in {".pyc", ".pyo"})
    manifesto = {}
    saida.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(saida, "w", ZIP_DEFLATED) as pacote:
        for caminho in sorted(caminhos):
            relativo = caminho.relative_to(ROOT).as_posix()
            conteudo = caminho.read_bytes()
            manifesto[relativo] = hashlib.sha256(conteudo).hexdigest()
            pacote.writestr("cardioia-fase2/" + relativo, conteudo)
        pacote.writestr("cardioia-fase2/manifesto-pacote.json", json.dumps(manifesto, indent=2))
    with ZipFile(saida) as pacote:
        assert pacote.testzip() is None
    sha = hashlib.sha256(saida.read_bytes()).hexdigest()
    saida.with_suffix(".zip.sha256").write_text(f"{sha}  {saida.name}\n")
    print(f"Pacote: {saida}\nArquivos: {len(caminhos)}\nSHA256: {sha}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist/CardioIA-Fase2-Guilherme-Yamada-Dantas-RM568506.zip")
    empacotar(parser.parse_args().output.resolve())
