# Checklist da entrega obrigatória

Guilherme Yamada Dantas · RM 568506

Esta lista acompanha a atividade Fase 2 — Diagnóstico Automatizado. As marcas dependem de evidência: arquivo existente, execução local, publicação e envio são estados distintos. A nota é atribuída pelo professor, não pelo checklist.

| Critério | Pontos | Evidência a conferir |
|---|---:|---|
| Relatos e mapa organizados | 2 | TXT com exatamente dez relatos completos; mapa CSV com `Sintoma 1`, `Sintoma 2`, `Doença Associada` |
| Extração funcional | 2 | Código lê arquivos, identifica expressões e apresenta hipóteses justificadas |
| Dataset correto | 1 | CSV `frase,situacao`, origem simulada e rótulos válidos |
| Classificador treinado/testado | 2 | Notebook TF-IDF + classificação + acurácia e análise de erros |
| Documentação e GitHub público | 1 | README, instruções reproduzíveis e todos os arquivos no repositório público |
| Vídeo no YouTube não listado | 2 | Demonstração completa de até quatro minutos, link funcional no README |

Pesos transcritos do plano de entrega baseado na captura da rubrica. Os extras React e MLP não substituem o obrigatório.

## Conferência técnica

- [x] TXT tem exatamente dez linhas não vazias; cada relato informa sintomas, início e impacto na rotina.
- [x] Mapa e base rotulada têm as colunas exigidas, sem vazios ou rótulos inesperados.
- [x] Extração diferencia sintomas afirmados, negados e contexto familiar, dentro das limitações documentadas.
- [x] Extração explica ambiguidade e ausência de correspondência.
- [x] Dados são simulados e não incluem dados identificáveis de pacientes reais.
- [x] Duplicatas e cenários relacionados não cruzam treino e teste.
- [x] TF-IDF é ajustado exclusivamente no treino, dentro de Pipeline.
- [x] Acurácia, baseline, matriz de confusão e métricas por classe vêm de execução real.
- [x] Erros de alto risco e limitações da amostra sintética estão discutidos.
- [x] Notebooks executam do início ao fim com kernel reiniciado.
- [x] Os comandos do README e os testes executam em ambiente preparado do zero.
- [x] README identifica somente Guilherme Yamada Dantas, RM 568506, como integrante acadêmico.

O relatório `revisao-independente.md` registra o que foi efetivamente executado e eventuais restrições da revisão. Não marcar itens apenas porque o autor os declarou concluídos.

Notebooks salvos inspecionados: contadores consecutivos e nenhuma saída de erro. A coordenação confirmou a execução integral e a reprodução com um segundo ambiente virtual em cópia extraída do ZIP; veja `verificacao-pacote.md`.

## Publicação e submissão — conferência humana final

- [ ] Guilherme consegue explicar a associação de sintomas, o TF-IDF, o split, o modelo e seus erros.
- [x] Código publicado no repositório público; visibilidade e commit conferidos pela API do GitHub.
- [x] Vídeo local gravado, cenas revisadas e duração medida: 144 segundos, menor que 4:00.
- [x] Vídeo publicado como **não listado** no YouTube; três páginas conferidas em 07/10/2026.
- [x] Links reais dos três vídeos incluídos nos READMEs; títulos, reprodução e visibilidade conferidos.
- [ ] Acesso em sessão anônima conferido pelo aluno.
- [x] O pacote local contém somente arquivos selecionados do projeto, sem e-books, Fast Tests ou credenciais.
- [x] Prazo e formato conferidos na FIAP: 07/10/2026 às 23h59; até 20 anexos de no máximo 256 MB cada.
- [ ] Arquivo/link correto enviado pela plataforma; comprovante guardado.

Até essas verificações, publicação, vídeo e submissão permanecem pendentes. Não inserir URL fictícia para preencher requisito.


## Conferência completa dos extras — 07/10/2026

| Parte | Requisito | Evidência local | Estado |
|---|---|---|---|
| Portal | React + Vite, Context API, JWT fake e rotas protegidas | Projeto separado `cardioia-portal`, README e testes | Implementado e testado |
| Portal | Pacientes JSON, agenda com useState/useReducer, painel | src/data, src/services, src/contexts e src/pages | Fluxos exercitados no navegador |
| Portal | CSS Modules e responsividade | Painel e formulário conferidos em 390×844; capturas no projeto | Conferido em amostra de telas |
| Portal | Instalação, componente, integrante e RM | README, lockfile, Node documentado | Conferido |
| ECG | Dataset público, imagens e licença | extras/ecg/data e manifesto | 120 imagens e hashes conferidos |
| ECG | Pré-processamento e MLP Keras | extras/ecg/experiment.py e notebook 03 | Executado, sem vazamento de paciente entre conjuntos |
| ECG | Treino, teste e avaliação | Métricas, matriz, histórico e 24 predições | Resultado negativo documentado; sem meta mínima de acurácia no enunciado |
| Ambos | Repositórios públicos e vídeos não listados | Código publicado e três URLs YouTube nos READMEs | Publicados e conferidos em sessão autenticada |

O vídeo do portal cobre o Ir Além 1; não substitui a demonstração obrigatória de NLP nem a do ECG. A nota depende da avaliação docente e da entrega completa, incluindo publicação. Nenhum checklist garante nota máxima.

## Preparação para explicar o trabalho

- **Regras versus aprendizado:** o mapa relaciona expressões explicitamente; o classificador aprende associações do corpus rotulado.
- **Por que TF-IDF dentro do Pipeline?** Para que vocabulário e pesos sejam aprendidos somente no treino.
- **Por que separar por cenário/paciente?** Para não avaliar paráfrases ou exames de uma mesma pessoa como se fossem novos exemplos independentes.
- **Por que não comemorar 100% no texto?** O corpus sintético é pequeno e repetitivo; validação de 75% e falha com negação mostram limites.
- **Por que 79,17% no ECG não é suficiente?** A classe majoritária tem essa mesma proporção; todos os casos normais foram classificados como anormais.
- **O portal autentica de verdade?** Não; JWT e login são didáticos. A proteção de rotas é de interface, sem servidor seguro.
- **O que faltaria para uso médico?** Dados apropriados, especialistas, validação externa, avaliação por subgrupo e protocolo de segurança — não realizados aqui.
