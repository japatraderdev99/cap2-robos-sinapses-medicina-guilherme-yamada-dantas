"""Extração educacional por regras; não é diagnóstico nem triagem clínica."""
from pathlib import Path
import argparse
import csv
import json
import re
import unicodedata

DADOS = Path(__file__).resolve().parents[1] / 'assets' / 'dados'
COLUNAS = ['Sintoma 1', 'Sintoma 2', 'Doença Associada']


def normalizar(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto.lower())
                   if unicodedata.category(c) != 'Mn')


def carregar_mapa(path=None):
    with open(path or DADOS / 'mapa_conhecimento.csv', encoding='utf-8-sig', newline='') as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames != COLUNAS:
            raise ValueError(f'Colunas esperadas: {COLUNAS}')
        linhas = list(leitor)
    if not linhas or any(not all(l.get(c, '').strip() for c in COLUNAS) for l in linhas):
        raise ValueError('Mapa vazio ou com campos incompletos')
    return linhas


def analisar_frase(frase, mapa=None):
    """Combina dois sintomas afirmados. Negação tem escopo até pontuação/adversativa.

    Antecedentes familiares são ignorados até mudança explícita de sujeito.
    Não resolve linguagem clínica livre, dupla negação ou temporalidade complexa.
    """
    if not isinstance(frase, str) or not frase.strip():
        raise ValueError('A frase deve ser um texto não vazio')
    mapa = carregar_mapa() if mapa is None else mapa
    termos = list(dict.fromkeys(l[c] for l in mapa for c in COLUNAS[:2]))
    afirmados, negados = set(), set()
    texto = normalizar(frase)
    # A locução de certeza não nega o sintoma que a segue.
    texto = re.sub(r'\bsem duvida\b', '', texto)
    # Mudanças de sujeito/adversativas encerram o escopo; "e" preserva listas negadas.
    partes = re.split(
        r'[.;!?\n]|\b(?:mas|porem|contudo|entretanto)\b|(?=\beu\b)'
        r'|(?=\be\s+(?:sinto|tenho|apresento|estou com)\b)', texto)
    for parte in partes:
        familiar = bool(re.search(r'\b(?:minha mae|meu pai|minha avo|meu avo|meu irmao|minha irma|historico familiar|antecedentes familiares)\b', parte))
        for termo in termos:
            for match in re.finditer(r'(?<!\w)' + re.escape(normalizar(termo)) + r'(?!\w)', parte):
                antes = parte[:match.start()]
                negacao = bool(re.search(r'\b(?:nao|nego|nega|negou|sem|ausencia de|ausente)\b', antes))
                if familiar:
                    continue
                (negados if negacao else afirmados).add(termo)
    sintomas = [t for t in termos if t in afirmados]
    hipoteses = []
    conflito = bool(afirmados & negados)
    for linha in mapa:
        par = [linha['Sintoma 1'], linha['Sintoma 2']]
        if not conflito and all(t in afirmados for t in par):
            hipoteses.append({'doenca': linha['Doença Associada'], 'sintomas': par})
    return {'frase': frase, 'sintomas': sintomas,
            'negados': [t for t in termos if t in negados], 'hipoteses': hipoteses,
            'status': ('contexto_ambiguo' if conflito else
                       'hipotese_encontrada' if hipoteses else 'sem_correspondencia')}


def extrair_arquivo(frases_path=None, mapa_path=None):
    mapa = carregar_mapa(mapa_path)
    linhas = Path(frases_path or DADOS / 'frases_sintomas.txt').read_text(encoding='utf-8').splitlines()
    return [analisar_frase(l.strip(), mapa) for l in linhas if l.strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frases', type=Path)
    parser.add_argument('--mapa', type=Path)
    args = parser.parse_args()
    print(json.dumps(extrair_arquivo(args.frases, args.mapa), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
