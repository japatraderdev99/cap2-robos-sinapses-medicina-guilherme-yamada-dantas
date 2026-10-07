# Ir Além 2 — método, evidências e limites

Guilherme Yamada Dantas — RM568506.

## Resultado executado
A MLP Keras foi treinada e avaliada: **79,17% de acurácia, igual ao baseline majoritário; balanced accuracy 50%**. No limiar pré-fixado 0,5, classificou todos os 24 exames do teste como anormais. Portanto, **não aprendeu uma separação binária útil neste protocolo**. Os cinco casos normais foram falsos positivos. Recall normal 0%, recall anormal 100%; macro-F1 0,4419; ROC-AUC 0,7789. A AUC descreve ranking, não corrige o fracasso no limiar aplicado nem comprova utilidade clínica.

A avaliação atende ao experimento acadêmico com resultados honestos, sem escolher novas sementes, partições, hiperparâmetros ou limiares após observar o teste para produzir uma métrica mais atraente.

## Dados e vazamento
Foram reutilizados 120 PNG únicos da Fase 1, derivados de PTB-XL 1.0.3 (24 por superclasse). NORM foi mapeado para normal; CD/HYP/MI/STTC para anormal. Esses grupos são diagnósticos amplos; “anormal” não equivale exclusivamente a arritmia ou urgência.

Os originais 1320×800 imprimem diagnóstico, idade, sexo e laudo no cabeçalho. Nenhum original é entrada direta do modelo. O recorte fixo `(0,80,1320,760)` remove as duas linhas e preserva os quatro painéis de traçados. Foi inspecionado visualmente um exemplo limpo, junto ao posicionamento fixo do gerador original. Todos os 120 arquivos têm a mesma dimensão e passam pelo mesmo recorte. As imagens são convertidas para cinza, redimensionadas com Lanczos para 264×136, normalizadas como `1-pixel/255` e achatadas em 35.904 entradas. Essa redução pode eliminar morfologia sutil e constitui uma limitação importante.

O paciente e o fold oficial foram recuperados da tabela PTBXL por `ecg_id`, não inferidos por nome. O manifesto preserva hashes e origem. Os 120 rótulos foram conferidos com os códigos SCP dos metadados oficiais e a tabela de superclasses; todos coincidem. A seleção da Fase 1 inclui apenas uma superclasse diagnóstica por exame, validação humana e idade de 1 a 89 anos; portanto, exclui casos multirrótulo e outras faixas etárias, criando viés de seleção. As 120 imagens correspondem a 119 pacientes; os dois exames de um mesmo paciente ficam juntos no teste. Nenhum paciente cruza partições.

## Protocolo e arquitetura
Cinco folds do StratifiedGroupKFold, shuffle=True, seed 42. Fold 0 teste, fold 1 validação, demais treino. Estes são folds experimentais; os folds oficiais PTBXL permanecem no manifesto apenas para auditoria. A amostra pequena e originalmente selecionada por superclasse não permite comparação com benchmarks do dataset completo.

| Partição | Exames | Pacientes | Normal | Anormal |
|---|---:|---:|---:|---:|
| Treino |72|72|14|58|
| Validação |24|24|5|19|
| Teste |24|23|5|19|

MLP pura Keras: entrada 35.904 → Dense 32/ReLU/L2(0,001) → Dropout 0,3 → Dense 16/ReLU → Dense 1/sigmoide. São 1.149.505 parâmetros, muitos para 72 casos de treino. Adam 0,001, binary crossentropy, batch 16, máximo 60 épocas. Pesos calculados só no treino: normal 2,5714, anormal 0,6207. Early stopping pela loss de validação, paciência 8, pesos restaurados da melhor época 7; encerrou na época 15. Teste não participou da seleção de época. TensorFlow 2.21.0/Keras 3.15.1, Python 3.12/macOS ARM64; seeds e operações determinísticas ativadas.

Baseline ajustado exclusivamente pela classe majoritária de treino. A composição total sugere 80% para sempre anormal, mas no teste real são 19/24 = 79,17%.

## Evidências verificáveis

- [Notebook executado](../notebooks/03_mlp_ecg.ipynb), com código completo comentado.
- [Métricas](../extras/ecg/artifacts/metrics.json) e [predições individuais](../extras/ecg/artifacts/test_predictions.json).
- [Manifesto](../extras/ecg/data/manifest.csv), incluindo pacientes, partições e hashes.
- [Figura de avaliação](../extras/ecg/artifacts/evaluation.png).
- [Execução e licenças](../extras/ecg/README.md).

## Limitações e próximos estudos
Não há validação clínica, externa ou prospectiva. A amostra é muito pequena, artificialmente balanceada por cinco superclasses, mas desbalanceada no problema binário. Teste de 24 casos tem grande incerteza e 23 unidades independentes de paciente. As etiquetas simplificadas podem ocultar comorbidades e incerteza. Remover idade/sexo das entradas não prova justiça; não há poder amostral para alegar equidade por subgrupo. Modelagem de sinais originais e conjuntos maiores, partições oficiais e validação externa seriam estudos posteriores com teste novo e protocolo pré-registrado. Não usar em diagnóstico, triagem ou orientação de tratamento.

## Vídeo próprio (até 4 min)

[Vídeo local pronto — 3 min 15 s, 1920×1080](../extras/ecg/video/CardioIA-ECG-demonstracao.mp4). Demonstração em oito quadros com legendas incorporadas e artefatos reais; sem narração. Cobre fonte, recorte, partições, MLP, treino, resultados negativos e reprodução. Duração verificada; todos os quadros inspecionados visualmente. Publicação segue pendente e será feita pelo usuário.

Tempos efetivos do vídeo, conforme o roteiro gerado:

| Tempo | Conteúdo |
|---|---|
| 0:00–0:20 | CardioIA · imagens de ECG |
| 0:20–0:45 | 01 · Origem e rótulos |
| 0:45–1:10 | 02 · Preparação sem o cabeçalho |
| 1:10–1:35 | 03 · Separação por paciente |
| 1:35–2:00 | 04 · MLP Keras: implementação real |
| 2:00–2:25 | 05 · Treinamento e avaliação |
| 2:25–2:50 | 06 · Resultado negativo, registrado |
| 2:50–3:15 | 07 · Reproduzir e interpretar |

Publicação e envio serão feitos pelo usuário; adicionar o link não listado no README após publicar.
