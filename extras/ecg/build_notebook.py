from pathlib import Path
import nbformat as n
from nbclient import NotebookClient
b=Path(__file__).resolve().parent
source=(b/'experiment.py').read_text().replace("BASE = Path(__file__).resolve().parent", "BASE = next(p / 'extras/ecg' for p in [Path.cwd(), *Path.cwd().parents] if (p / 'extras/ecg/experiment.py').exists())").replace("if __name__=='__main__':run()",'')
nb=n.v4.new_notebook(cells=[n.v4.new_markdown_cell('''# CardioIA — MLP de imagens ECG
**Guilherme Yamada Dantas — RM568506**

Experimento acadêmico Ir Além 2. Fonte: PTB-XL 1.0.3, amostra da Fase1 (120 exames), licença CC BY4.0. Não é validação clínica.

## Protocolo definido antes do teste
NORM=0 (normal), CD/HYP/MI/STTC=1 (anormal). O agrupamento não representa apenas arritmias: são superclasses diagnósticas. Removemos o cabeçalho que expunha o diagnóstico, preservamos originais, convertemos para cinza, redimensionamos para264×136 e achatamos. Pacientes não se cruzam entre partições. Cinco folds estratificados agrupados com seed42: fold0 teste, fold1 validação, restantes treino. Os folds oficiais PTBXL são preservados no manifesto para auditoria, mas não adotados nesta pequena subamostra.

Arquitetura e hiperparâmetros fixos; early stopping usa somente validação. Pesos de classe calculados somente no treino. Teste consultado uma vez por execução, limiar0,5, sem seleção pela métrica de teste.

Instale `extras/ecg/requirements.txt` num venv Python3.12; selecione seu kernel. Execute todas as células do início. O código completo está abaixo e também em `extras/ecg/experiment.py`.
'''),n.v4.new_code_cell(source),n.v4.new_markdown_cell('## Executar preparação, treinamento e avaliação'),n.v4.new_code_cell('report = run()'),n.v4.new_code_cell("from IPython.display import display, Image as DisplayImage\ndisplay(DisplayImage(filename=str(BASE/'artifacts/evaluation.png')))"),n.v4.new_markdown_cell('''## Análise crítica
Compare sempre a MLP com o baseline de classe majoritária. A acurácia isolada esconde falhas em normais. A matriz usa linhas reais e colunas previstas [normal, anormal]. `test_predictions.json` registra inclusive os erros.

120 exames não demonstram generalização clínica; apenas cerca de24 casos em teste geram grande incerteza. A seleção original balanceou cinco superclasses e não representa prevalência hospitalar. Redução da resolução pode apagar características sutis. Idade/sexo/laudo não são entradas, mas remover esses campos não prova equidade. Não há avaliação externa, prospectiva, por equipamento, instituição ou subgrupo; nem autorização para diagnóstico ou triagem reais.

Fontes: [PTB-XL1.0.3](https://physionet.org/content/ptb-xl/1.0.3/), [artigo original](https://doi.org/10.1038/s41597-020-0495-6), [Fase1](https://github.com/japatraderdev99/fiap-preparando-terreno-para-inteligencia-cardiologica).''')],metadata={'kernelspec':{'display_name':'Python 3 (ECG)','language':'python','name':'python3'}})
p=b.parents[1]/'notebooks/03_mlp_ecg.ipynb'
n.write(nb,p)
NotebookClient(nb,timeout=600,kernel_name='python3',resources={'metadata':{'path':str(b.parents[1])}}).execute()
n.write(nb,p)
print(p)
