"""Casos observáveis de extração e regressões de linguagem."""
import unittest
from src.extracao import analisar_frase, extrair_arquivo


class TestExtracao(unittest.TestCase):
    def test_acentos_caixa(self):
        r = analisar_frase('FALTA DE AR e INCHACO NAS PERNAS desde ontem.')
        self.assertTrue(any('Insuficiência' in h['doenca'] for h in r['hipoteses']))

    def test_lista_negada(self):
        r = analisar_frase('Não tenho dor no peito nem suor frio.')
        self.assertEqual(r['hipoteses'], [])
        self.assertEqual(set(r['negados']), {'dor no peito', 'suor frio'})

    def test_adversativa_reinicia_escopo(self):
        r = analisar_frase('Não tenho cansaço, mas sinto dor no peito e suor frio.')
        self.assertEqual(len(r['hipoteses']), 1)

    def test_nova_afirmacao_apos_negacao_nao_relacionada(self):
        r = analisar_frase('Não dormi bem e sinto dor no peito e falta de ar.')
        self.assertEqual(set(r['sintomas']), {'dor no peito', 'falta de ar'})
        self.assertEqual(len(r['hipoteses']), 1)

    def test_familiar_nao_e_paciente(self):
        r = analisar_frase('Minha mãe teve dor no peito e suor frio; eu tenho cansaço.')
        self.assertEqual(r['sintomas'], ['cansaço'])
        self.assertEqual(r['hipoteses'], [])

    def test_mudanca_sujeito(self):
        r = analisar_frase('Meu pai teve cansaço e eu tenho dor no peito e suor frio.')
        self.assertNotIn('cansaço', r['sintomas'])
        self.assertEqual(len(r['hipoteses']), 1)

    def test_primeira_pessoa_encerra_contexto_familiar(self):
        r = analisar_frase('Minha mãe está bem e sinto dor no peito e suor frio.')
        self.assertEqual(len(r['hipoteses']), 1)

    def test_locucao_sem_duvida_nao_nega(self):
        r = analisar_frase('Sem dúvida sinto dor no peito e suor frio.')
        self.assertEqual(r['negados'], [])
        self.assertEqual(len(r['hipoteses']), 1)

    def test_palavra_inteira(self):
        r = analisar_frase('Sinto suor friozinho e dor no peito.')
        self.assertNotIn('suor frio', r['sintomas'])
        self.assertEqual(r['hipoteses'], [])

    def test_multiplas_hipoteses(self):
        r = analisar_frase('Tenho dor no peito, falta de ar e inchaço nas pernas.')
        self.assertEqual(len({h['doenca'] for h in r['hipoteses']}), 2)

    def test_sem_regra_nao_significa_saudavel(self):
        r = analisar_frase('Sinto uma forte dor na cabeça desde ontem.')
        self.assertEqual(r['status'], 'sem_correspondencia')
        self.assertNotIn('risco', r)

    def test_persistem_mencoes_opostas(self):
        r = analisar_frase('Ontem não tinha dor no peito. Hoje sinto dor no peito e suor frio.')
        self.assertIn('dor no peito', r['sintomas'])
        self.assertIn('dor no peito', r['negados'])
        self.assertEqual(r['status'], 'contexto_ambiguo')
        self.assertEqual(r['hipoteses'], [])

    def test_contradicao_nao_ganha_hipotese(self):
        r = analisar_frase('Sinto dor no peito e suor frio. Não sinto dor no peito.')
        self.assertEqual(r['status'], 'contexto_ambiguo')
        self.assertEqual(r['hipoteses'], [])

    def test_dez_relatos(self):
        r = extrair_arquivo()
        self.assertEqual(len(r), 10)
        self.assertTrue(any(x['hipoteses'] for x in r))
        self.assertTrue(any(not x['hipoteses'] for x in r))

    def test_vazio(self):
        with self.assertRaises(ValueError):
            analisar_frase(' ')


if __name__ == '__main__':
    unittest.main()
