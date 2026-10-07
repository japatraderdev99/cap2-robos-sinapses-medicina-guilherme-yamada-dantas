# Revisão independente do núcleo obrigatório

Revisão técnica em 6 de outubro de 2026. Aluno: Guilherme Yamada Dantas, RM 568506. Este relatório distingue execução acadêmica de validade clínica e de conclusão da entrega.

## Evidências reproduzidas

O revisor leu o enunciado local e o plano de entrega e inspecionou os módulos de extração e classificação e os quatro arquivos de dados. Executou `treinar_avaliar(output_dir='/private/tmp/cardioia-qa-evidence')` separadamente da geração oficial de resultados e `python -m pytest -q` no ambiente `.venv` do projeto.

- Dez relatos completos lidos e processados pelo módulo de extração; presença de sintoma, início e efeito na rotina conferida por leitura.
- 160 frases em 40 grupos; treino: 96 frases/24 grupos, validação: 32/8, teste: 32/8. Cada partição tem metade das frases em cada classe.
- Acurácia no teste sintético: 1,0; baseline: 0,5; zero falsos negativos nessa amostra. Não há suporte para extrapolar esses números a pacientes.
- Os três testes independentes em `tests/test_integracao.py` verificaram disjunção de grupos/cenários, presença das duas classes, impossibilidade de aprender um termo exclusivo da avaliação e integração das dez frases.
- A suíte completa na revisão final passou: **26 testes**, incluindo testes funcionais da interface. Foram emitidos 14 avisos de depreciação de dependências do Matplotlib/Pyparsing, sem falhas.

Essa execução usou o ambiente preparado pela coordenação, não um clone limpo nem instalação independente. Inspecionei os dois notebooks salvos: quatro e sete células de código, respectivamente, com contadores consecutivos desde 1 e nenhuma saída de erro. Sua execução foi feita pela coordenação; esta inspeção confirma os registros salvos. Os números do README coincidem com metricas.json: treino 100%, validação 75%, teste 100% e baseline de teste 50%. Inspeção visual da interface e reprodução em clone limpo exigem evidência própria; os testes funcionais não as substituem.

## Achados e limites observados

**Diversidade sintética limitada.** Quatro paráfrases de cada cenário usam estruturas repetidas. O split conserva cada cenário em uma partição, mas todas as partições vêm do mesmo processo de autoria. A acurácia perfeita pode refletir a facilidade e regularidade dessa base. Não alterar rótulos ou selecionar exemplos após ver o teste para preservar uma métrica alta.

**Negação não é compreendida pelo classificador.** Na execução independente, `Não sinto dor no peito e não tenho suor frio.` recebeu `alto risco`, com probabilidade do modelo de aproximadamente 0,763; `Não sinto falta de ar.` recebeu `alto risco`, aproximadamente 0,699. São sondagens de comportamento textual, não falsos positivos clínicos com referência validada. Preservar “não” no vocabulário não resolve a limitação. Esses exemplos servem à demonstração honesta no vídeo.

**Extração corrigida durante a revisão.** Inicialmente `Não dormi bem e sinto dor no peito e suor frio.` teve seus sintomas negados indevidamente. A correção do responsável passou a reiniciar o contexto em uma nova afirmação explícita, e a nova execução retornou ambos os sintomas afirmados. `Minha mãe está bem e sinto dor no peito e suor frio.` também passou a reconhecer a afirmação do paciente.

**Correções finais revalidadas.** `Sem dúvida sinto dor no peito e suor frio.` agora reconhece os sintomas afirmados. Em `Sinto dor no peito e suor frio. Não sinto dor no peito agora.`, o extrator agora retorna `contexto_ambiguo`, preserva as listas afirmada e negada e suprime hipóteses. Essa abordagem expõe a contradição sem tentar resolver temporalidade. As regressões foram executadas novamente pelo revisor; permanece uma gramática simples, não compreensão clínica de linguagem livre.

**Vínculo dos metadados.** Dados e metadados precisam manter alinhamento. O contrato inclui hash de frase para detectar reordenação indevida; qualquer edição exige conferir novamente esse contrato e as partições.

## Conclusão limitada ao escopo revisado

O núcleo de dados, regras e classificação executou e seus testes passaram. As ressalvas são materiais e devem aparecer na documentação e apresentação. Esta revisão não certifica segurança médica, ausência de viés ou aprovação docente.

Repositório público atualizado, vídeo não listado com até quatro minutos e envio na plataforma são etapas separadas e **não foram comprovados por esta revisão**. React e MLP são extras fora do núcleo revisado.
