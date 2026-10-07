# CardioIA — MLP de ECG (Ir Além 2)
Guilherme Yamada Dantas — RM568506.

Experimento acadêmico com Keras/TensorFlow e imagens públicas PTB-XL. Não utilizar para decisões médicas. Veja [metodologia e resultados](../../document/ecg.md) e [notebook executado](../../notebooks/03_mlp_ecg.ipynb).

## Executar
Python 3.12, ambiente isolado do núcleo. A primeira instalação requer internet; os dados necessários já estão incluídos.

```bash
cd extras/ecg
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python experiment.py
```

`python build_notebook.py` recria e executa o notebook completo, atualizando os artefatos. A execução precisa permitir portas locais para o kernel Jupyter. Para abrir interativamente, selecione um kernel do mesmo venv. `requirements-lock.txt` registra o ambiente macOS ARM64 usado, enquanto `requirements.txt` contém as dependências diretas.

## Conteúdo

- `data/originals`: 120 PNG da Fase 1, imutáveis; contêm diagnóstico no cabeçalho e **não entram diretamente no modelo**.
- `data/clean`: cópias sem cabeçalho, cinza; geradas por `prepare()`.
- `data/manifest.csv`: hash original/limpo, classe, paciente, fold oficial e partição experimental.
- `data/metadata_ptbxl_subset.csv`: recuperação de paciente/fold/SCP original por ecg_id; somente 120 registros relevantes.
- `data/provenance.json`: origem e hash do CSV oficial completo.
- `artifacts`: modelo Keras, métricas, predições individuais, curva e matriz.

Os rótulos, nomes de arquivos, paciente, laudo, idade e sexo são usados somente para organização/auditoria, nunca como atributos da MLP. Não há aumento de dados nem cópias de `amostras/` contabilizadas.

## Licença e atribuição
Dados e imagens derivadas: CC BY 4.0, conforme `data/LICENSE-PTBXL.txt`. As cópias foram cortadas, convertidas para cinza e redimensionadas na entrada do modelo. O código de renderização original está preservado para auditoria.

Wagner et al. (2022), PTB-XL v1.0.3, PhysioNet, https://doi.org/10.13026/kfzx-aw45.
Wagner et al. (2020), Scientific Data, https://doi.org/10.1038/s41597-020-0495-6.
Fase 1: https://github.com/japatraderdev99/fiap-preparando-terreno-para-inteligencia-cardiologica, commit `9da4cfc021ed48dee1bda8456f643200302566ca`.

## Vídeo e publicação
[Assistir à demonstração local (3 min 15 s, 1080p)](video/CardioIA-ECG-demonstracao.mp4). Composição didática com imagens, código, resultados reais e legendas; sem narração. Oito quadros revisados visualmente; duração medida com ffprobe. [Roteiro](video/roteiro.json) e [metadados](video/metadata.json).

Vídeo publicado: [ECG e rede neural MLP — YouTube, não listado](https://www.youtube.com/watch?v=1bPnMXL78pU), 3min15s. Título, reprodução e selo “Não listado” conferidos em 07/10/2026. O link também está no README principal. O envio na FIAP será feito pelo aluno.
