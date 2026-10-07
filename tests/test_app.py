from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_demo_analisa_relato_e_exibe_evidencias():
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    assert not at.exception
    at.button[0].click().run()
    assert not at.exception
    conteudo = " ".join(x.value for x in at.markdown)
    assert "Sintomas afirmados" in conteudo
    assert "Rótulo experimental" in conteudo


def test_demo_rejeita_vazio_e_vocabulario_desconhecido():
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    at.text_area[0].set_value("   ")
    at.button[0].click().run()
    assert any("Escreva um relato" in w.value for w in at.warning)
    at.text_area[0].set_value("xyzk qwrtyp")
    at.button[0].click().run()
    assert any("fora do vocabulário" in w.value for w in at.warning)
    assert not at.exception


def test_demo_avaliacao_e_dez_relatos():
    at = AppTest.from_file(str(APP), default_timeout=30).run()
    at.radio[0].set_value("Avaliação").run()
    assert not at.exception
    assert len(at.metric) == 3
    at.radio[0].set_value("Dez relatos").run()
    assert not at.exception
    assert len(at.expander) == 10
