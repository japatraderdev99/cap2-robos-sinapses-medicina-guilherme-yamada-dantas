"""Demonstração local: execute com streamlit run app.py."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import json

import pandas as pd
import streamlit as st

from src.extracao import analisar_frase, extrair_arquivo
from src.classificacao import prever_frase, treinar_avaliar

ROOT = Path(__file__).resolve().parent
DADOS = ROOT / "assets/dados"
st.set_page_config(page_title="CardioIA | Laboratório de relatos", page_icon="🫀", layout="wide")


@st.cache_resource(show_spinner="Preparando o experimento reproduzível…")
def carregar_experimento(assinatura):
    # O hash invalida o cache ao mudar a base; arquivos temporários não alteram
    # as evidências oficiais que acompanham a entrega.
    with TemporaryDirectory(prefix="cardioia-") as pasta:
        resultado = treinar_avaliar(data_dir=DADOS, output_dir=pasta)
        resultado["auditoria"] = json.loads((Path(pasta) / "auditoria_equidade.json").read_text())
    return resultado


def apresentar_regras(resultado):
    st.subheader("O que as regras encontraram")
    st.write("**Sintomas afirmados:** " + (", ".join(resultado["sintomas"]) or "Nenhum reconhecido."))
    if resultado["negados"]:
        st.write("**Expressões negadas:** " + ", ".join(resultado["negados"]))
    if resultado["status"] == "contexto_ambiguo":
        st.warning("Há sintomas afirmados e negados no mesmo relato. As hipóteses foram suspensas; revise o contexto.")
    elif resultado["hipoteses"]:
        for hipotese in resultado["hipoteses"]:
            st.write(f"**Hipótese didática: {hipotese['doenca']}**")
            st.caption("Regra acionada: " + " + ".join(hipotese["sintomas"]))
    else:
        st.info("Nenhuma regra completa corresponde ao relato. Isso não exclui doença.")


def analisar(pipeline):
    st.title("Analisar um relato")
    st.write("Observe como expressões de um texto se tornam regras e uma classificação aprendida.")
    exemplos = ["Escrever outro relato"] + (DADOS / "frases_sintomas.txt").read_text(encoding="utf-8").splitlines()
    escolha = st.selectbox("Carregar exemplo simulado", exemplos, index=1)
    with st.form("relato"):
        texto = st.text_area("Relato fictício", value="" if escolha == exemplos[0] else escolha,
                             height=130, max_chars=2000, key=f"texto_{exemplos.index(escolha)}")
        enviado = st.form_submit_button("Analisar relato", type="primary")
    if not enviado:
        st.caption("Escolha um exemplo ou escreva um relato fictício e selecione Analisar relato.")
        return
    if not texto.strip():
        st.warning("Escreva um relato antes de analisar.")
        return
    regras = analisar_frase(texto)
    previsao = prever_frase(texto, pipeline)
    esquerda, direita = st.columns([1.2, 1], gap="large")
    with esquerda:
        apresentar_regras(regras)
    with direita:
        st.subheader("O que o modelo classificou")
        if previsao["status"] != "ok":
            st.warning("Texto fora do vocabulário aprendido. O modelo não produziu classificação.")
        else:
            st.write(f"**Rótulo experimental: {previsao['rotulo']}**")
            st.caption("“Baixo risco” é uma classe do exercício; não significa que uma pessoa esteja segura.")
            with st.expander("Ver detalhe estatístico"):
                st.write(f"Probabilidade da classe prevista: {previsao['probabilidade_modelo']:.1%}")
                st.write("Valor interno não calibrado. Não é probabilidade de doença nem medida de segurança clínica.")
    st.caption("As regras e o modelo podem discordar: usam mecanismos diferentes e ambos têm limitações.")
    st.download_button("Baixar resultado do exemplo", json.dumps({"regras": regras, "modelo": previsao}, ensure_ascii=False, indent=2),
                       file_name="relato_simulado.json", mime="application/json")


def dez_relatos(pipeline):
    st.title("Dez relatos, passo a passo")
    st.write("As hipóteses abaixo vêm do mapa de conhecimento. O rótulo experimental vem do classificador de texto.")
    for n, item in enumerate(extrair_arquivo(), start=1):
        with st.expander(f"Relato {n} · {item['frase']}", expanded=n == 1):
            apresentar_regras(item)
            pred = prever_frase(item["frase"], pipeline)
            st.write("**Classificação experimental:** " + (pred["rotulo"] or "Sem classificação"))
    st.subheader("Mapa de conhecimento")
    st.dataframe(pd.read_csv(DADOS / "mapa_conhecimento.csv"), hide_index=True, use_container_width=True)


def avaliar(resultado):
    st.title("Avaliação em cenários reservados")
    metricas = resultado["metricas"]
    teste = metricas["modelo"]["teste"]
    st.write("Paráfrases do mesmo cenário permanecem na mesma partição. O vocabulário é aprendido somente no treino.")
    a, b, c = st.columns(3)
    a.metric("Acurácia no teste sintético", f"{teste['acuracia']:.1%}")
    b.metric("Referência majoritária", f"{metricas['baseline']['teste']['acuracia']:.1%}")
    c.metric("Falsos negativos no teste", metricas["falsos_negativos_teste"])
    st.caption("A amostra é pequena e sintética. Estes números não medem desempenho em pacientes reais.")
    st.subheader("Separação dos dados")
    st.dataframe(pd.DataFrame(metricas["contagens"]).T, use_container_width=True)
    st.subheader("Matriz de confusão")
    st.caption("Linhas: rótulo simulado de referência. Colunas: previsão do modelo.")
    st.table(pd.DataFrame(teste["matriz_confusao"], index=teste["ordem_rotulos"], columns=teste["ordem_rotulos"]))
    st.subheader("Métricas por classe")
    tabela = pd.DataFrame({k: teste["por_classe"][k] for k in teste["ordem_rotulos"]}).T
    st.dataframe(tabela, use_container_width=True)
    st.subheader("Erros para estudar")
    erros = resultado["previsoes"].loc[resultado["previsoes"].erro]
    if erros.empty:
        st.info("Nenhum erro neste conjunto específico. Isso não demonstra generalização clínica.")
    else:
        st.dataframe(erros[["frase", "real", "previsto", "falso_negativo"]], hide_index=True, use_container_width=True)
    st.subheader("O teste perfeito não encerra a análise")
    st.write("Nesta sondagem posterior ao teste, compare afirmações e negações. O modelo não foi reajustado com esses exemplos; uma classificação igual pode expor dependência das palavras de sintomas.")
    desafios = ["Sinto dor no peito e suor frio.", "Não sinto dor no peito e não tenho suor frio.",
                "Sinto falta de ar.", "Não sinto falta de ar."]
    st.table(pd.DataFrame([{"Relato": f, "Previsão experimental": prever_frase(f, resultado["pipeline"])["rotulo"]} for f in desafios]))
    st.caption("Sem rótulo clínico validado: a sondagem evidencia comportamento linguístico, não mede acurácia médica.")
    with st.expander("Sondagem de sensibilidade a gênero e idade"):
        st.write(resultado["auditoria"]["natureza"])
        st.json(resultado["auditoria"])
    with st.expander("Protocolo e versões"):
        st.write(metricas["protocolo"])
        st.json(metricas["versoes"])
    st.download_button("Baixar métricas", json.dumps(metricas, ensure_ascii=False, indent=2),
                       file_name="metricas.json", mime="application/json")


st.sidebar.title("CardioIA")
st.sidebar.caption("Laboratório de relatos\n\nFIAP · Fase 2")
pagina = st.sidebar.radio("Explorar", ["Analisar relato", "Dez relatos", "Avaliação", "Sobre o projeto"])
st.sidebar.divider()
st.sidebar.write("Guilherme Yamada Dantas")
st.sidebar.caption("RM 568506")
st.info("Demonstração acadêmica com dados sintéticos. Use apenas relatos fictícios; não utilize o resultado para decisões de saúde.")
try:
    assinatura = hashlib.sha256(b"".join((DADOS / nome).read_bytes() for nome in ["frases_rotuladas.csv", "metadados_frases.csv"])).hexdigest()
    experimento = carregar_experimento(assinatura)
except (FileNotFoundError, ValueError) as erro:
    st.error(f"Não foi possível carregar os dados do projeto: {erro}")
    st.stop()

if pagina == "Analisar relato":
    analisar(experimento["pipeline"])
elif pagina == "Dez relatos":
    dez_relatos(experimento["pipeline"])
elif pagina == "Avaliação":
    avaliar(experimento)
else:
    st.title("Medir antes de confiar")
    st.write("O CardioIA explora duas formas de interpretar relatos: associações explícitas entre sintomas e hipóteses, e aprendizado estatístico com TF-IDF e regressão logística.")
    st.subheader("O que este protótipo permite")
    st.write("Inspecionar regras, repetir um experimento, observar erros e discutir os limites dos dados. Textos digitados são processados pelo servidor local e não são gravados em arquivo pelo aplicativo.")
    st.subheader("O que ainda falta para uma aplicação real")
    st.write("Dados representativos e legitimamente obtidos, supervisão clínica, validação externa e prospectiva, avaliação por subgrupos e definição de governança e responsabilidade. Este experimento não realizou essas etapas.")
    st.subheader("Material de estudo")
    st.write("Os notebooks, a metodologia, os testes e o mapa de conhecimento acompanham o código-fonte. A interface é uma demonstração complementar; o portal React do desafio Ir Além é um trabalho separado.")
