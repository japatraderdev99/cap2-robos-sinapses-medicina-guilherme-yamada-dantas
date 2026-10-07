# Demonstração local do CardioIA

A interface serve à exploração acadêmica de textos simulados e à apresentação dos resultados. Não é um portal de atendimento nem substitui o desafio opcional em React.

## Direção visual

Paleta: branco `#FFFFFF` como superfície de leitura, azul petróleo `#183347` para texto, verde azulado `#176C78` para ações, azul claro `#EDF4F6` para áreas de apoio e âmbar `#9A5800` para ressalvas. Usar tipografia sans serif nativa, títulos de 28 a 36 px, corpo de 16 px e números tabulares nos resultados.

O principal elemento é o relato, apresentado à esquerda das evidências textuais. A navegação separa exploração, dez relatos e avaliação. A avaliação reúne matriz de confusão, exemplos de erro e resultados por classe; não transforma acurácia em promessa clínica.

```text
CardioIA                       navegação lateral
Analisar um relato
Contexto de uso acadêmico
[Exemplo simulado                          ]
[Texto editável                           ]
[Analisar relato]
Sintomas e regras           Classificação aprendida
Expressões identificadas    Rótulo e limites
```

A revisão do desenho removeu indicadores decorativos e gráficos sem dados: a identidade aparece na cor e na hierarquia do relato. Os componentes nativos mantêm teclado, foco e adaptação à largura da tela. Nenhum recurso visual externo é necessário.
