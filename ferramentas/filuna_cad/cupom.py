"""Cupom de folga: uma régua de furos e um pino para descobrir, imprimindo, a folga certa da sua impressora."""
from pathlib import Path

import manifold3d as m3d
import numpy as np
import trimesh

FOLGAS = (0.10, 0.15, 0.20, 0.25, 0.30, 0.40)   # mm por lado
PASSO, BORDA, ESPESSURA = 16.0, 8.0, 6.0
PINO_ALTURA, PEGA, PEGA_ALTURA = 10.0, 14.0, 4.0
SEGMENTOS = 96


def _malha(solido):
    m = solido.to_mesh()
    return trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts))


def regua(diametro, folgas=FOLGAS):
    """Placa com um furo por folga, do mais justo para o mais folgado. O canto cortado marca o lado do mais justo."""
    comprimento = BORDA * 2 + PASSO * (len(folgas) - 1)
    largura = diametro + BORDA * 2
    placa = m3d.Manifold.cube([comprimento, largura, ESPESSURA])
    for i, folga in enumerate(folgas):
        raio = diametro / 2 + folga
        furo = m3d.Manifold.cylinder(ESPESSURA + 2, raio, raio, SEGMENTOS).translate([BORDA + PASSO * i, largura / 2, -1])
        placa -= furo
    triangulo = m3d.CrossSection([np.array([[-1.0, -1.0], [5.0, -1.0], [-1.0, 5.0]])])
    return placa - m3d.Manifold.extrude(triangulo, ESPESSURA + 2).translate([0, 0, -1])


def pino(diametro):
    """Pino no diâmetro exato, com uma pega quadrada. A base tem chanfro para a primeira camada não engrossá-lo."""
    raio = diametro / 2
    corpo = m3d.Manifold.cylinder(PINO_ALTURA - 0.5, raio, raio, SEGMENTOS).translate([0, 0, PEGA_ALTURA])
    ponta = m3d.Manifold.cylinder(0.5, raio, raio - 0.5, SEGMENTOS).translate([0, 0, PEGA_ALTURA + PINO_ALTURA - 0.5])
    pega = m3d.Manifold.cube([PEGA, PEGA, PEGA_ALTURA], True).translate([0, 0, PEGA_ALTURA / 2])
    return pega + corpo + ponta


def gerar(pasta, diametro=8.0, folgas=FOLGAS):
    """Grava a régua e o pino em STL e devolve o roteiro do teste."""
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    arquivos = {"regua": pasta / "cupom_regua.stl", "pino": pasta / "cupom_pino.stl"}
    _malha(regua(diametro, folgas)).export(arquivos["regua"])
    _malha(pino(diametro)).export(arquivos["pino"])
    return {
        "arquivos": {k: str(v) for k, v in arquivos.items()},
        "pino_mm": diametro,
        "furos_mm": [round(diametro + 2 * f, 2) for f in folgas],
        "folgas_por_lado_mm": list(folgas),
        "como_usar": [
            "Imprima as duas peças deitadas como estão, no material e na camada da peça final.",
            "O canto cortado da régua marca o furo mais justo; as folgas crescem a partir dele.",
            "Tente o pino em cada furo. O primeiro em que entra com a mão é a sua folga justa.",
            "O primeiro em que entra e gira solto é a sua folga de deslizar.",
            "Use esses dois números como parâmetro de folga nos seus modelos.",
        ],
    }
