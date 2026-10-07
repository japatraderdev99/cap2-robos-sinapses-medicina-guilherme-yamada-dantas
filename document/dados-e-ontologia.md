# Dados sintéticos e ontologia didática

Todos os relatos foram escritos para este exercício com apoio de IA em 6 de outubro de 2026. Não há pacientes reais, prontuários, identificadores pessoais ou exames nesses arquivos. O aluno deve revisar e compreender os exemplos e suas limitações antes da entrega.

## Arquivos e contrato

- `assets/dados/frases_sintomas.txt`: dez relatos independentes, um por linha, contendo sintomas, início e efeito na rotina. Não fazem parte do treino.
- `assets/dados/mapa_conhecimento.csv`: quatro associações com as colunas exigidas `Sintoma 1,Sintoma 2,Doença Associada`.
- `assets/dados/frases_rotuladas.csv`: 160 textos, com as colunas `frase,situacao`, 80 exemplos de `baixo risco` e 80 de `alto risco`.
- `assets/dados/metadados_frases.csv`: 160 linhas correspondentes, na mesma ordem, com `frase_id,grupo,cenario,frase_sha256`. Os IDs vão de f001 a f160. Há 40 grupos g01 a g40, com quatro paráfrases por cenário e um único rótulo por grupo. Nunca ordenar apenas um desses dois arquivos. O SHA256 do texto literal UTF-8 permite detectar desalinhamento entre arquivos; o carregador deve conferir ordem e hash antes da modelagem.

O rótulo é uma convenção de simulação: relatos com sintomas leves, resolução e rotina preservada receberam `baixo risco`; relatos com dor torácica persistente, falta de ar importante, desmaio ou limitação acentuada receberam `alto risco`. **Esses rótulos não foram atribuídos por médicos nem validados em pacientes e não estimam risco clínico.** As classes não representam prevalência real. Um texto de baixo risco não oferece garantia de segurança.

Há vinte cenários por classe. Cada cenário foi reescrito em quatro estruturas linguísticas iguais para ambas as classes, evitando que uma estrutura exclusiva entregue o rótulo. Essa construção ainda reduz a diversidade de linguagem. A separação por grupo evita colocar paráfrases do mesmo cenário no treino e no teste; não elimina o parentesco entre cenários nem demonstra generalização para relatos reais. Não ajustar os dados após observar o teste para aumentar artificialmente a pontuação.

## Referências e uso restrito das associações

O [NHLBI/NIH descreve sintomas de infarto](https://www.nhlbi.nih.gov/health/heart-attack/symptoms), incluindo desconforto torácico, falta de ar e suor frio. O [NHLBI/NIH descreve sintomas de insuficiência cardíaca](https://www.nhlbi.nih.gov/health/heart-failure/symptoms), incluindo falta de ar, fadiga e edema. Consulta realizada pela coordenação em 6 de outubro de 2026.

Essas páginas sustentam a presença de sintomas no vocabulário. **Não sustentam a regra de que dois sintomas determinam uma doença.** As conjunções do CSV são simplificações pedagógicas do autor, sem sensibilidade, especificidade ou valor preditivo conhecidos. Sintomas podem ocorrer em muitas outras condições. A ferramenta não faz diagnóstico, recomendações terapêuticas ou triagem e não deve orientar decisões médicas.

## Funcionamento da extração

`carregar_mapa(path=None)` valida o cabeçalho e campos obrigatórios. `analisar_frase(frase,mapa=None)` retorna `frase`, `sintomas`, `negados`, `hipoteses` e `status`. Cada hipótese contém `doenca` e os dois `sintomas` que acionaram a regra. Os estados possíveis são `hipotese_encontrada`, `sem_correspondencia` e `contexto_ambiguo`. `extrair_arquivo(frases_path=None,mapa_path=None)` processa as linhas não vazias. Os caminhos padrão são calculados a partir de `__file__`.

Caixa e acentos são normalizados; expressões precisam ter limites de palavra. Acentos originais permanecem na apresentação. O sistema procura termos exatos, não sinônimos: “dispneia” não é automaticamente convertido em “falta de ar”. Negação básica abrange listas até pontuação ou adversativas. Uma mudança explícita para “eu” ou uma nova oração com “e sinto/tenho/apresento/estou com” reinicia o contexto. A locução “sem dúvida” não é considerada negação. Antecedentes de familiares explicitamente listados são ignorados na cláusula, sem serem confundidos com sintomas negados. Todas as regras satisfeitas são retornadas; nenhuma prioridade diagnóstica é inventada.

Limitações conhecidas: escopo de negação pode ficar amplo demais; vírgulas não encerram a negação. Dupla negação, hipótese, citação, familiares não previstos, temporalidade e pronomes implícitos não são resolvidos. Se um sintoma aparecer afirmado e negado em trechos diferentes, ele aparece nas duas listas, o status será `contexto_ambiguo` e todas as hipóteses serão suprimidas. Essa abstenção conservadora não tenta resolver ordem temporal, mesmo quando o relato menciona ontem e hoje. A ontologia é pequena: ausência de correspondência significa apenas ausência de regra acionada. Não significa ausência de doença.

## Verificação reproduzível

Na raiz do repositório, executar `python -m unittest discover -s tests -p test_extracao.py` e `python -m src.extracao`. Os testes incluem negação coordenada, limites de palavra, familiares, mudança de sujeito, múltiplas hipóteses, ausência de regra e dez relatos. O modelo de linguagem e as associações permanecem dependentes de revisão humana, mesmo quando os testes passam.
