# Roteiro executável — vídeo obrigatório

Guilherme Yamada Dantas · RM 568506. Meta: **3min50s**, com dez segundos de margem. Publicar no YouTube como **não listado** e inserir o link real no README após conferir o vídeo.

## Preparação

1. Executar os comandos de instalação e validação do README antes da gravação.
2. Deixar abertos: README, dez relatos, mapa de conhecimento e os dois notebooks com saídas da execução final.
3. Ajustar zoom para texto legível. Usar somente dados simulados; fechar outras abas e notificações.
4. Anotar a acurácia, baseline, tamanho do teste e um erro a partir da saída real. Não copiar números de versões anteriores.
5. Ensaiar com cronômetro. Se uma execução for longa, mostrar sua saída pronta e dizer que foi previamente executada, sem simular execução ao vivo.

| Tempo | Tela/ação | Fala sugerida |
|---|---|---|
| 0:00–0:20 | README com identificação | “Sou Guilherme Yamada Dantas, RM 568506. Este é o CardioIA da Fase 2: um exercício acadêmico de extração de sintomas e classificação de risco em textos simulados. Não é um sistema validado para atendimento clínico.” |
| 0:20–0:50 | Abrir TXT e mapa CSV | “Os dez relatos informam sintomas, início e impacto na rotina. O mapa associa expressões a hipóteses didáticas. Um sintoma isolado pode ter várias causas; a associação não confirma diagnóstico.” |
| 0:50–1:30 | Executar demonstração de extração conforme README/notebook | “O código lê os arquivos, normaliza o texto e procura expressões. Aqui estão os termos encontrados e as hipóteses. Também verificamos frases negadas e casos sem correspondência. A regra tem limites de contexto, descritos na documentação.” Mostrar um relato, uma negação e um caso sem correspondência. |
| 1:30–2:15 | Notebook de classificação: dados, split e Pipeline | “O CSV contém frases com dois rótulos. Os dados são sintéticos, com origem e critérios registrados. A separação mantém cenários relacionados na mesma partição. O TF-IDF aprende o vocabulário somente no treino; a regressão logística aprende a relação entre vetores e rótulos.” |
| 2:15–3:05 | Saída real de métricas e análise de erros | “Neste teste, com [ler quantidade real] frases, a acurácia foi [ler resultado] e o baseline foi [ler resultado]. A matriz de confusão distingue acertos e erros. Este exemplo mostra [ler um erro real ou uma limitação observada]. Confundir alto risco com baixo risco é uma limitação importante. Esses resultados medem esta amostra sintética, não desempenho em pacientes reais.” |
| 3:05–3:30 | Previsões de dois exemplos e documentação | “Podemos inspecionar previsões para textos de classes distintas, mas o modelo pode falhar com negações, linguagem diferente e casos ausentes do treinamento. Os testes de variações textuais exploram limitações e não comprovam ausência de vieses.” |
| 3:30–3:50 | README e estrutura | “O repositório reúne os dados, códigos, notebooks e instruções para reprodução. Os próximos passos seriam revisão de rótulos por especialistas e avaliação com dados adequados e governança. Esta entrega demonstra os fundamentos e explicita seus limites.” |

Os campos entre colchetes são instruções para a gravação: substituir pela execução final, sem deixar esses campos na fala. Se o teste não apresentar erro, usar um caso adversarial efetivamente executado ou explicar a limitação da base; não inventar um erro.

## Antes de publicar

- Conferir duração no arquivo exportado, legibilidade e áudio/legendas.
- Conferir que as saídas mostradas correspondem à versão entregue.
- Não declarar validação médica, garantia de nota ou superioridade sobre outros modelos.
- Após publicar, testar o link fora da conta proprietária e incluí-lo no README.
- A gravação, a publicação e o envio na plataforma não são realizados por este roteiro.
