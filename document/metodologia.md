# Metodologia de classificação

Este experimento acadêmico classifica relatos **sintéticos** nos rótulos didáticos `baixo risco` e `alto risco`. Os rótulos representam decisões de elaboração do dataset, não diagnósticos confirmados. Nenhum resultado demonstra eficácia clínica, segurança para triagem ou generalização para pacientes reais.

## Protocolo fixado antes da avaliação

Cada cenário tem um identificador de grupo compartilhado por suas paráfrases. O arquivo `metadados_frases.csv` acompanha as linhas de `frases_rotuladas.csv` na mesma ordem. O carregador rejeita duplicatas normalizadas, frases vazias, classes inesperadas, grupos com rótulos divergentes e cenários divididos em grupos. O vínculo por ordem precisa ser preservado quando os dados forem editados; a coluna `frase_sha256` do sidecar registra SHA256 do texto literal UTF-8 e o carregador verifica o pareamento. As evidências registram também SHA256 dos bytes de ambos os CSVs.

A divisão usa grupos estratificados por rótulo: aproximadamente 60% treino, 20% validação e 20% teste, semente 42. Um cenário e todas suas paráfrases permanecem em uma única partição. Isso reduz o vazamento por paráfrase direta; semelhanças linguísticas entre cenários ainda podem favorecer o modelo. O teste contém exemplos sintéticos do mesmo processo de autoria, não validação externa.

O pipeline ajusta TF-IDF somente nas frases de treino. Usa unigramas e bigramas, normalização de caixa e acentos, sem remoção de stopwords: `não` permanece representado. Isso **não garante compreensão de negações**, temporalidade ou contexto clínico. A regressão logística usa `C=1`, solver `liblinear`, máximo de 1.000 iterações e semente 42. Esses parâmetros são fixos; não há busca nem ajuste com o teste. A validação é reportada para transparência, sem selecionar hiperparâmetros nesta versão. O classificador `DummyClassifier(strategy='most_frequent')`, ajustado ao treino, é o baseline majoritário.

## Resultados e erros auditáveis

`python -m src.classificacao` treina, avalia e grava os resultados reais em `document/evidencias/`. `metricas.json` contém versões, hash do dataset com metadados, contagens por partição, acurácia, precisão, recall, F1, matriz de confusão, baseline e todos os erros de teste. `particoes.csv` permite conferir a separação. `previsoes_teste.csv` contém cada relato, rótulo de referência, previsão, probabilidade da classe prevista, indicador de erro e falso negativo. `matriz_confusao.png` mostra linhas reais e colunas previstas, na ordem baixo risco/alto risco.

Um falso negativo é um exemplo sintético rotulado alto risco e previsto baixo risco. Esses casos são explicitamente contados e preservados para discussão. Não serão ocultados para melhorar a aparência das métricas. A contagem não estima eventos adversos reais. Mudanças motivadas pelos erros do teste exigiriam declarar reutilização do teste e obter um novo conjunto independente antes de alegar avaliação final inédita.

A probabilidade retornada por `prever_frase` é a probabilidade estatística da classe prevista dentro do modelo, **não probabilidade de doença ou risco clínico**; não foi calibrada. Texto vazio e texto sem qualquer termo do vocabulário são recusados. A presença de termos conhecidos também não garante que uma entrada pertença ao domínio; não existe detector clínico de casos fora da distribuição.

## Sondagem contrafactual

`auditoria_equidade.json` compara três pares de relatos com mudança de gênero textual e, separadamente, três pares com mudança de idade. Apresenta previsões e mudanças, sem afirmar ausência de viés. A sondagem é muito pequena, não contém desfechos clínicos e não mede equidade populacional. Idade pode alterar risco clínico de forma legítima; aqui somente se observa sensibilidade textual. Diferença entre probabilidades das classes previstas deve ser lida junto com os rótulos, pois as classes podem mudar.

## Reprodução e limites

Os testes verificam disjunção de grupos/cenários, determinismo, rejeição de entradas e que vocabulário e IDF equivalem ao ajuste isolado no treino. As versões executadas constam das métricas. Reproduzir os números requer os mesmos dados, versão das bibliotecas e protocolo. O hash registrado inclui dados e metadados serializados; não é o hash dos bytes de um único CSV.

O uso útil desta etapa é pedagógico: demonstrar um processo rastreável de extração, aprendizado e avaliação. Uma aplicação médica exigiria coleta e governança apropriadas, especialistas, validação externa prospectiva e avaliação de segurança que não fazem parte desta entrega.

Referência técnica: [Scikit-learn — prevenção de vazamento de dados com pipelines](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

## Resultado da primeira execução

A execução inicial com o protocolo acima obteve **32 acertos em 32 relatos de teste**, distribuídos em 8 grupos inéditos (4 por classe), contra 50% do baseline. Foram observados zero falsos positivos e zero falsos negativos nesse conjunto. Logo, não há erro de teste a exemplificar nesta execução; o CSV preserva todas as previsões e permite conferir isso. O treino contém 96 frases/24 grupos e a validação 32 frases/8 grupos. Os valores da execução reproduzida e as versões vigentes sempre devem ser consultados no JSON.

Esse resultado perfeito evidencia também a facilidade do corpus sintético e a possibilidade de padrões de escrita comuns aos autores. Não significa 100% de acerto em relatos reais. Os 32 relatos não são 32 observações independentes, pois há quatro paráfrases por grupo; não calculamos um intervalo binomial que fingisse independência. Não foi alterado o split nem ajustado o modelo para obter esse resultado.
