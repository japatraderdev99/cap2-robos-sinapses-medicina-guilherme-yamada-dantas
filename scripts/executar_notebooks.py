"""Executa os dois notebooks obrigatórios no ambiente principal, sem kernel global.

O notebook opcional de ECG usa extras/ecg/.venv e seu procedimento próprio.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import sys

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
os.environ.setdefault("IPYTHONDIR", str(ROOT / ".cache/ipython"))
os.environ.setdefault("JUPYTER_RUNTIME_DIR", str(ROOT / ".cache/jupyter"))


def main():
    with TemporaryDirectory(prefix="cardioia-kernel-") as temporario:
        pasta = Path(temporario) / "cardioia"
        pasta.mkdir()
        (pasta / "kernel.json").write_text(json.dumps({
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "CardioIA", "language": "python",
        }), encoding="utf-8")
        for nome in ("01_extracao.ipynb", "02_classificacao_texto.ipynb"):
            caminho = ROOT / "notebooks" / nome
            notebook = nbformat.read(caminho, as_version=4)
            gerenciador = KernelManager(kernel_name="cardioia", kernel_spec_manager=KernelSpecManager(kernel_dirs=[temporario]))
            cliente = NotebookClient(notebook, km=gerenciador, timeout=180, resources={"metadata": {"path": str(ROOT)}})
            try:
                cliente.execute()
            finally:
                if gerenciador.has_kernel:
                    gerenciador.shutdown_kernel(now=True)
            # Metadado portátil para abertura no Jupyter ou Colab.
            notebook.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
            nbformat.validate(notebook)
            nbformat.write(notebook, caminho)
            print(f"Executado: {caminho.name}")


if __name__ == "__main__":
    main()
