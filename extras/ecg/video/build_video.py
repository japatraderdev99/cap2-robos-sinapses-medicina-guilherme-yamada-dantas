"""Composição didática de artefatos reais; não simula captura de tela."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, textwrap, subprocess
B=Path(__file__).resolve().parent; E=B.parent
F='/System/Library/Fonts/Supplemental/'
def font(size,bold=False):return ImageFont.truetype(F+('Arial Bold.ttf' if bold else 'Arial.ttf'),size)
slides=[
('CardioIA · imagens de ECG', ['Guilherme Yamada Dantas · RM568506','Ir Além 2 — rede MLP com Keras','Experimento acadêmico executado com 120 imagens públicas.','Demonstração em quadros, com legendas; sem narração.','Objetivo: implementar e avaliar, sem alegar validade clínica.'],None,20),
('01 · Origem e rótulos',['PTB-XL 1.0.3 · licença CC BY 4.0 · amostra da Fase 1','120 exames: 24 normais e 96 anormais.','NORM → normal; CD, HYP, MI e STTC → anormal.','O diagnóstico aparece no cabeçalho original: vazamento de resposta.'],E/'data/originals/ECG_17722_CD.png',25),
('02 · Preparação sem o cabeçalho',['Recorte fixo (0, 80, 1320, 760) remove diagnóstico e laudo.','Tons de cinza → 264 × 136 → 1 − pixel/255 → vetor de 35.904 pixels.','Preservamos originais e hashes; nomes e metadados não são atributos.'],E/'data/clean/17722.png',25),
('03 · Separação por paciente',['120 exames pertencem a 119 pacientes. Nenhum paciente cruza partições.','Treino: 72 exames, 14 normais / 58 anormais.','Validação: 24 exames, 5 normais / 19 anormais.','Teste: 24 exames, 5 normais / 19 anormais (23 pacientes).','StratifiedGroupKFold: 5 folds, seed 42; teste 0, validação 1.','Folds experimentais; os folds oficiais ficam no manifesto para auditoria.'],None,25),
('04 · MLP Keras: implementação real',['Trecho da arquitetura usada em experiment.py e no notebook:','Dense(32, activation="relu", kernel_regularizer=l2(.001))','Dropout(.3)','Dense(16, activation="relu")','Dense(1, activation="sigmoid")','Adam(.001) · binary_crossentropy · batch 16','1.149.505 parâmetros; pesos de classe calculados apenas no treino.'],None,25),
('05 · Treinamento e avaliação',['Execução real: 15 épocas; melhores pesos da época 7.','EarlyStopping: val_loss, paciência 8, restore_best_weights=True.','Máximo previsto: 60 épocas; limiar fixo 0,5. Teste não escolheu época.'],E/'artifacts/evaluation.png',25),
('06 · Resultado negativo, registrado',['Acurácia: 79,17% — igual ao baseline que sempre prevê anormal.','Balanced accuracy: 50%. Todos os 24 testes previstos anormais.','Recall normal: 0% (5 falsos positivos). Recall anormal: 100%.','ROC-AUC: 0,7789; ranking não corrige o fracasso no limiar aplicado.','Não houve ajuste de sementes, partições ou limiar após olhar o teste.','Modelo salvo foi recarregado e reproduziu as 24 probabilidades.'],None,25),
('07 · Reproduzir e interpretar',['cd extras/ecg','python3.12 -m venv .venv  →  source .venv/bin/activate','pip install -r requirements.txt  →  python experiment.py','Notebook executado: notebooks/03_mlp_ecg.ipynb','Limites: poucos casos, redução de resolução, viés de seleção.','Sem separação útil neste protocolo. Não usar para decisões médicas.','Fontes: PhysioNet PTB-XL 1.0.3 e repositório da Fase 1.'],None,25)]
manifest=[]
for idx,(title,lines,asset,duration) in enumerate(slides,1):
 im=Image.new('RGB',(1920,1080),'#101e2c');d=ImageDraw.Draw(im)
 d.rectangle((0,0,1920,12),fill='#55dcc1');d.text((75,60),title,font=font(58,True),fill='white')
 y=155
 for line in lines:
  for part in textwrap.wrap(line,90):
   d.text((80,y),part,font=font(34 if asset else 38),fill='#e2edf4');y+=48 if asset else 61
  y+=8
 if asset:
  pic=Image.open(asset).convert('RGB');pic.thumbnail((1720,650 if idx==3 else 610))
  # Fit remaining area without obscuring captions.
  pic.thumbnail((1720,950-y));im.paste(pic,((1920-pic.width)//2,y+12))
 d.text((80,1010),'CARDIOIA  /  Experimento acadêmico · sem uso clínico',font=font(25),fill='#80aaa9')
 d.text((1760,1010),f'{idx:02d} / 08',font=font(25),fill='#80aaa9')
 out=B/f'frame-{idx:02d}.png';im.save(out)
 manifest.append({'frame':out.name,'seconds':duration,'title':title,'captions':lines,'source':str(asset.relative_to(E)) if asset else None})
(B/'roteiro.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(B/'concat.txt').write_text(''.join(f"file 'frame-{i+1:02d}.png'\nduration {s['seconds']}\n" for i,s in enumerate(manifest))+"file 'frame-08.png'\n")
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(B/'concat.txt'),'-vf','fps=15','-c:v','libx264','-preset','fast','-crf','22','-pix_fmt','yuv420p','-t',str(sum(s['seconds'] for s in manifest)),'-movflags','+faststart',str(B/'CardioIA-ECG-demonstracao.mp4')],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
