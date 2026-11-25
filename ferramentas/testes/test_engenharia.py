"""Testes dos módulos de engenharia: cada um com uma peça de resposta conhecida."""
import importlib.util
import shutil

import pytest
import trimesh

from filuna_cad import conferir, fabricar, robo


def _tem(modulo):
    return importlib.util.find_spec(modulo) is not None


@pytest.fixture
def caixa(tmp_path):
    caminho = tmp_path / "caixa.stl"
    trimesh.creation.box((40, 30, 20)).export(caminho)
    return caminho


@pytest.fixture
def rebaixo(tmp_path):
    """Bloco com um vazio fechado por dentro: nenhuma ferramenta e nenhum molde alcança."""
    fora = trimesh.creation.box((40, 40, 40))
    dentro = trimesh.creation.box((10, 10, 10))
    dentro.invert()
    caminho = tmp_path / "rebaixo.stl"
    trimesh.util.concatenate([fora, dentro]).export(caminho)
    return caminho


def test_conferir_stl_fechado(caixa):
    r = conferir.conferir(caixa)
    assert r["aprovada"] and r["medidas_mm"] == [40.0, 30.0, 20.0]


def test_conferir_stl_aberto(tmp_path):
    m = trimesh.creation.box((10, 10, 10))
    m.update_faces(list(range(len(m.faces) - 2)))
    caminho = tmp_path / "aberta.stl"
    m.export(caminho)
    r = conferir.conferir(caminho)
    assert not r["aprovada"] and r["achados"][0]["tema"] == "malha"


@pytest.mark.skipif(not _tem("ezdxf"), reason="ezdxf não instalado")
def test_conferir_dxf_contorno_aberto(tmp_path):
    import ezdxf

    doc = ezdxf.new(units=4)
    doc.modelspace().add_lwpolyline([(0, 0), (50, 0), (50, 30)])
    caminho = tmp_path / "corte.dxf"
    doc.saveas(caminho)
    r = conferir.conferir(caminho)
    assert r["unidade"] == "mm" and r["polilinhas_abertas"] == 1


def test_cnc_caixa_duas_fixacoes(caixa):
    r = fabricar.usinagem(caixa)
    assert r["area_sem_alcance_mm2"] == 0 and len(r["fixacoes"]) <= 2


def test_cnc_e_injecao_acham_o_vazio(rebaixo):
    assert fabricar.usinagem(rebaixo)["area_sem_alcance_mm2"] > 300
    assert fabricar.injecao(rebaixo)["area_presa_mm2"] > 300


def test_chapa_espessura(tmp_path):
    caminho = tmp_path / "chapa.stl"
    trimesh.creation.box((60, 40, 2)).export(caminho)
    r = fabricar.chapa(caminho)
    assert r["espessura_uniforme"] and r["espessura_mm"] == pytest.approx(2.0, abs=0.05)
    assert r["area_planificada_cm2"] == pytest.approx(24.0, abs=0.1)


def test_urdf_com_erros(tmp_path):
    caminho = tmp_path / "r.urdf"
    caminho.write_text("""<robot name="r"><link name="a"/><link name="b"/><link name="c"/>
      <joint name="j" type="revolute"><parent link="a"/><child link="b"/><axis xyz="0 0 0"/>
      <limit lower="1" upper="-1"/></joint></robot>""")
    temas = {a["tema"] for a in robo.conferir(caminho)["achados"]}
    assert {"eixo", "limite", "arvore"} <= temas


@pytest.mark.skipif(not _tem("mujoco"), reason="mujoco não instalado")
def test_mjcf_simula(tmp_path):
    caminho = tmp_path / "p.xml"
    caminho.write_text('<mujoco><worldbody><body pos="0 0 1"><joint type="hinge" axis="0 1 0"/>'
                       '<geom type="capsule" fromto="0 0 0 0.3 0 0" size="0.02" mass="0.2"/></body></worldbody></mujoco>')
    r = robo.conferir(caminho)
    assert r["compila"] and r["estavel"]


@pytest.mark.skipif(not (shutil.which("ccx") and _tem("gmsh")), reason="CalculiX ou gmsh não instalados")
def test_simular_viga_bate_com_a_conta(tmp_path):
    from filuna_cad import simular

    caminho = tmp_path / "viga.stl"
    trimesh.creation.box((100, 10, 10)).export(caminho)
    r = simular.simular(caminho, simular.Caso("xmin", "xmax", (0, 0, -10), "aco", 2.5))
    # Viga engastada: flecha F L³ / 3EI = 0,0195 mm e tensão M c / I = 6 MPa na raiz.
    assert r["deslocamento_max_mm"] == pytest.approx(0.0195, rel=0.08)
    assert r["tensao_max_mpa"] == pytest.approx(6.0, rel=0.25)


@pytest.mark.skipif(not _tem("matplotlib"), reason="matplotlib não instalado")
def test_desenho_acha_furo(tmp_path):
    from filuna_cad import desenho

    placa = trimesh.creation.box((60, 40, 6))
    furo = trimesh.creation.cylinder(radius=3, height=20, sections=48)
    caminho = tmp_path / "placa.stl"
    placa.difference(furo).export(caminho)
    r = desenho.desenhar(caminho, tmp_path / "placa.pdf")
    assert (tmp_path / "placa.pdf").stat().st_size > 5000
    assert [f["diametro_mm"] for f in r["furos"]] == [pytest.approx(6.0, abs=0.05)]
