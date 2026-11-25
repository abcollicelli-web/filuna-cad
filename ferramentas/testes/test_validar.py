import numpy as np
import pytest
import trimesh
from PIL import Image

from filuna_cad import comparar, validar


def salvar(malha, pasta, nome):
    caminho = pasta / nome
    malha.export(caminho)
    return caminho


def caixa(x, y, z, origem=(0, 0, 0)):
    m = trimesh.creation.box(extents=(x, y, z))
    m.apply_translation(np.array(origem) + np.array([x, y, z]) / 2)
    return m


def temas(r):
    return {(i["gravidade"], i["tema"]) for i in r["achados"]}


def test_cubo_bom_tira_cem(tmp_path):
    r = validar.validar(salvar(caixa(30, 30, 20), tmp_path, "cubo.stl"))
    assert r["aprovada"] and r["nota"] == 100
    assert r["mesa"]["apoio_mm2"] == pytest.approx(900, abs=1)
    assert r["paredes"]["minima_mm"] == pytest.approx(20, abs=0.1)


def test_malha_aberta_reprova(tmp_path):
    m = caixa(30, 30, 20)
    m.update_faces(np.arange(len(m.faces)) > 1)
    r = validar.validar(salvar(m, tmp_path, "aberta.stl"))
    assert not r["aprovada"] and ("erro", "malha") in temas(r)


def test_parede_fina_reprova(tmp_path):
    r = validar.validar(salvar(caixa(40, 0.5, 30), tmp_path, "fina.stl"))
    assert ("erro", "parede") in temas(r)
    assert r["paredes"]["minima_mm"] == pytest.approx(0.5, abs=0.05)


def test_balanco_em_t_avisa(tmp_path):
    t = trimesh.boolean.union([caixa(10, 10, 30, (15, 0, 0)), caixa(40, 10, 5, (0, 0, 30))], engine="manifold")
    r = validar.validar(salvar(t, tmp_path, "t.stl"))
    assert ("aviso", "balanco") in temas(r)
    assert r["balancos"]["area_mm2"] == pytest.approx(300, abs=2)


def test_peca_maior_que_a_mesa_reprova(tmp_path):
    r = validar.validar(salvar(caixa(300, 30, 20), tmp_path, "grande.stl"), validar.Limites(mesa=(256, 256, 256)))
    assert ("erro", "mesa") in temas(r)


def test_pecas_iguais_e_diferentes(tmp_path):
    a = salvar(caixa(30, 30, 20), tmp_path, "a.stl")
    b = salvar(caixa(30, 30, 10), tmp_path, "b.stl")
    assert comparar.comparar_pecas(a, a)["sobreposicao"] == pytest.approx(1.0)
    assert comparar.comparar_pecas(a, b)["sobreposicao"] == pytest.approx(0.5, abs=0.01)


def test_raio_x_reconhece_a_silhueta(tmp_path):
    peca = salvar(caixa(40, 10, 20), tmp_path, "placa.stl")
    igual = Image.new("RGB", (300, 200), "white")
    igual.paste((0, 0, 0), (50, 50, 250, 150))
    igual.save(tmp_path / "igual.png")
    outra = Image.new("RGB", (300, 300), "white")
    outra.paste((0, 0, 0), (50, 50, 250, 250))
    outra.save(tmp_path / "outra.png")
    assert comparar.raio_x(peca, tmp_path / "igual.png")["semelhanca"] > 0.97
    assert comparar.raio_x(peca, tmp_path / "outra.png")["semelhanca"] < 0.6


def test_orientar_prefere_a_face_sem_balanco(tmp_path):
    from filuna_cad import orientar
    t = trimesh.boolean.union([caixa(10, 10, 30, (15, 0, 0)), caixa(40, 10, 5, (0, 0, 30))], engine="manifold")
    r = orientar.orientar(salvar(t, tmp_path, "t.stl"))
    melhor = r["posicoes"][0]
    assert melhor["balanco_mm2"] == pytest.approx(0, abs=1)
    assert "Y" in melhor["posicao"]
    assert len(r["posicoes"]) == 6


def test_folha_de_vistas_desenha_a_peca(tmp_path):
    from filuna_cad import vistas
    r = vistas.folha(salvar(caixa(40, 20, 10), tmp_path, "c.stl"), tmp_path / "folha.png")
    img = np.asarray(Image.open(tmp_path / "folha.png").convert("L"))
    assert r["medidas_mm"] == [40.0, 20.0, 10.0]
    assert (img > 120).mean() > 0.05


def test_cupom_tem_os_furos_nas_folgas_pedidas(tmp_path):
    from filuna_cad import cupom
    r = cupom.gerar(tmp_path, diametro=8.0)
    assert r["furos_mm"] == [8.2, 8.3, 8.4, 8.5, 8.6, 8.8]
    for arquivo in r["arquivos"].values():
        v = validar.validar(arquivo)
        assert v["aprovada"] and v["nota"] == 100
    regua = trimesh.load(r["arquivos"]["regua"], force="mesh")
    furos = sum(3.14159265 * (d / 2) ** 2 * 6 for d in r["furos_mm"])
    assert regua.volume == pytest.approx(96 * 24 * 6 - furos - 8 * 6, rel=0.01)


def test_chanfro_de_45_graus_nao_conta_como_balanco(tmp_path):
    import manifold3d as m3d
    piao = m3d.Manifold.cylinder(1, 0, 1, 16) + m3d.Manifold.cylinder(1, 1, 0, 16).translate([0, 0, 1])
    s = m3d.Manifold.cube([30, 30, 18]).minkowski_sum(piao).to_mesh()
    m = trimesh.Trimesh(np.asarray(s.vert_properties)[:, :3], np.asarray(s.tri_verts))
    r = validar.validar(salvar(m, tmp_path, "chanfrada.stl"))
    assert r["balancos"]["area_mm2"] == 0 and r["nota"] == 100


def test_raios_em_lotes_dao_o_mesmo_resultado_que_de_uma_vez(tmp_path, monkeypatch):
    """A espessura medida em lotes de raios é igual à medida de uma vez só (o lote existe para limitar a memória)."""
    grande = trimesh.creation.icosphere(subdivisions=5, radius=30)
    caminho = salvar(grande, tmp_path, "esfera.stl")
    em_lote = validar.validar(caminho, validar.Limites(amostras=1200))
    monkeypatch.setattr(validar, "LOTE_RAIOS", 10_000)
    de_uma_vez = validar.validar(caminho, validar.Limites(amostras=1200))
    assert em_lote["paredes"] == de_uma_vez["paredes"]
    assert em_lote["paredes"]["minima_mm"] == pytest.approx(60, abs=1.5)
