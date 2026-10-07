# Verificação do pacote local

Verificação da coordenação em 6 de outubro de 2026, após a revisão independente.

## Reprodução em pasta limpa

O código, dados, notebooks e documentação foram empacotados por `scripts/empacotar.py`, extraídos em uma nova pasta temporária e executados com um novo ambiente virtual Python 3.11.11. Foram instaladas as 81 dependências do `requirements-lock.txt` usando o cache da instalação anterior. Não foram reutilizados módulos ou arquivos do ambiente virtual original.

- `python -m pytest -q`: **26 testes passaram**, com 14 avisos de depreciação de dependências Matplotlib/Pyparsing.
- `python scripts/gerar_evidencias.py`: dez relatos processados e métricas regeneradas.
- Comparação dos objetos de `metricas.json`: idênticos entre a pasta original e a extraída.
- `python scripts/executar_notebooks.py`: ambos os notebooks executados integralmente com um kernel limpo por arquivo e encerramento explícito.
- `python scripts/verificar_entrega.py`: artefatos locais verificados; publicação, vídeo no YouTube e envio continuam separados.

Essa conferência cobre código e dados da versão local. Adições posteriores de vídeo, capturas e relatórios não alteram o pipeline; o pacote final é novamente conferido por hashes. A instalação usa o cache de downloads e não constitui um teste de acesso ao PyPI em outra máquina. A execução remota da CI ainda não ocorreu.

## Interface

Fluxos de relato, entrada vazia, vocabulário desconhecido, dez relatos e avaliação foram cobertos pelos testes da aplicação. A coordenação inspecionou no navegador a demonstração em 1280 pixels de largura e a entrada em 390 pixels. As capturas estão em `document/evidencias/demo-*.png`.

A inspeção em 390 pixels não detectou elementos de texto, títulos ou tabelas além da largura da janela na tela analisada. A conferência é uma amostra de telas e interações; não equivale a auditoria de acessibilidade completa nem a testes em aparelhos físicos.

## Estado da entrega

Arquivos locais e execução foram verificados. Publicação do código, visibilidade e link do vídeo no YouTube, conferência do prazo e envio na plataforma não são inferidos desses resultados. O modo `--final` foi executado e retornou código 1 pelas pendências externas, como esperado. Ele continuará apontando essas pendências enquanto os registros correspondentes não forem confirmados; o modo local passou.


## Revisão final ampliada — 07/10/2026

- **33 testes aprovados**, 14 avisos de depreciação de dependências, nenhuma falha. Inclui sete casos de auditoria ECG que detectam imagens adulteradas, paciente cruzando conjuntos, métricas inconsistentes, predições inválidas e notebook incompleto.
- `python scripts/verificar_entrega.py --extras`: núcleo e ECG verificados sem falhas locais. Publicação e YouTube permanecem pendências explícitas.
- Notebook ECG preservado: três células executadas sem erro; 120 imagens, 119 pacientes e zero interseção entre partições. Métricas recalculadas a partir das predições pelo verificador, sem novo treino.
- Portal separado: sete testes, build e formatação passaram. Fluxos também foram exercitados no navegador real, inclusive sessão, busca, agenda, recarga, cancelamento e bloqueio após logout.
- Prazo e formulário conferidos na FIAP: 07/10/2026 às 23h59, até 20 anexos de 256 MB por arquivo. Nenhuma submissão foi realizada.

A reprodução em ambiente novo descrita acima é do núcleo original; não é alegada como nova reprodução isolada de todos os extras. A rotina CI do portal foi adicionada, mas sua execução remota continua não verificada. A gravação nativa do portal foi localizada, revisada e finalizada com legendas: 159,833333 segundos. O original e a composição anterior foram preservados. O núcleo mantém seu vídeo de 207,96 segundos; ECG mantém composição didática de 195 segundos. Todos abaixo de quatro minutos.
