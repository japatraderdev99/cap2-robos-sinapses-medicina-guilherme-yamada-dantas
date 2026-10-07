# Governança e limites de uso

Guilherme Yamada Dantas — RM 568506.

O núcleo da Fase 2 usa somente textos sintéticos elaborados para demonstrar aprendizado e extração. Não contém dados de pacientes. Os rótulos não vêm de avaliação médica; reproduzem critérios didáticos documentados em `dados-e-ontologia.md`.

## Uso pretendido

Estudar regras, representação vetorial, classificação, avaliação e falhas linguísticas. A aplicação serve para apresentação acadêmica local. Não é destinada a atendimento, diagnóstico, priorização de pacientes ou escolha de tratamento.

## Riscos observados

O classificador responde a sintomas negados como se fossem afirmados em exemplos exploratórios. A extração reconhece apenas expressões cadastradas e algumas construções de negação/sujeito. Um texto fora do vocabulário é recusado, mas textos com palavras conhecidas ainda podem estar fora da distribuição. Probabilidades não foram calibradas e não são estimativas de risco médico.

A base balanceada não representa prevalência populacional. O estilo de autoria é recorrente; quatro paráfrases do mesmo cenário são correlacionadas. Dividir por grupos reduz um tipo de vazamento, mas não cria validação externa. Não inferir aplicabilidade a diferentes regiões, idades, gêneros, condições ou formas de relatar sintomas.

## Transparência e privacidade

Registrar versões, partições, hashes, previsões e erros permite revisar o experimento. Textos digitados na demonstração não são salvos em arquivo pelo aplicativo; o resultado permanece na sessão e pode ser baixado voluntariamente. O servidor é local, sem chamadas a modelos externos. Não inserir informações reais de pacientes.

O arquivo de metadados contém identificadores fictícios de frases, não de pessoas. Nenhuma relação de idade/gênero foi empregada para representar uma população. As sondagens contrafactuais medem sensibilidade textual e não comprovam equidade.

## Passos necessários para investigar utilidade médica

1. Definir uma pergunta clínica e um uso delimitado com profissionais responsáveis.
2. Obter dados adequados, com base de uso legítima, proteção e documentação da origem.
3. Desenvolver protocolo de anotação, revisão clínica e avaliação dos desacordos.
4. Reservar avaliação externa por paciente/instituição e testar calibração, erros e subgrupos.
5. Estabelecer supervisão, monitoramento e avaliação prospectiva antes de qualquer uso assistencial.

Estas etapas não foram realizadas no projeto acadêmico. Nenhuma alegação de benefício clínico ou de conformidade regulatória resulta dos testes apresentados.
