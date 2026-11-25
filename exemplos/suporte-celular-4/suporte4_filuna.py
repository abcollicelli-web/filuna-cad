"""Suporte de celular "4" no padrão dos geradores do Filuna: shapely + manifold3d + trimesh, 3MF verificado."""
import json
import math
from pathlib import Path

import manifold3d as m3d
import numpy as np
import trimesh
from shapely import affinity
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

PASTA = Path(__file__).parent
PROFUNDIDADE, FENDA, FUNDO = 80.0, 11.0, 10.0
CANTO = (70.0, 110.0)
ANGULOS = ((16.0, 55.0), (16.0, 65.0), (52.0, 82.0))
COR = "#7C3AED"


def quatro():
    return unary_union([
        box(20, 0, 160, 16),
        box(50, 0, 70, 110),
        box(0, 34, 94, 52),
        Polygon([(0, 34), (22, 34), (70, 92), (70, 110), (50, 110), (0, 52)]),
    ])


def fenda(y_sup, graus):
    a = math.radians(graus)
    x = CANTO[0] + (CANTO[1] - y_sup) / math.tan(a)
    base = box(0, -FUNDO / math.sin(a), FENDA, 40)
    return affinity.translate(affinity.rotate(base, 90 - graus, origin=(0, 0)), x, y_sup)


def perfil():
    return quatro().difference(unary_union([fenda(y, g) for y, g in ANGULOS]))


def solido(poligono):
    contornos = [np.asarray(poligono.exterior.coords)[:-1]] + [np.asarray(i.coords)[:-1] for i in poligono.interiors]
    corpo = m3d.Manifold.extrude(m3d.CrossSection(contornos, m3d.FillRule.EvenOdd), PROFUNDIDADE)
    if corpo.status() != m3d.Error.NoError:
        raise RuntimeError(f"manifold3d recusou o sólido: {corpo.status()}")
    malha = corpo.to_mesh()
    return trimesh.Trimesh(np.asarray(malha.vert_properties)[:, :3], np.asarray(malha.tri_verts), process=True)


def main():
    p = perfil()
    malha = solido(p)
    malha.visual.face_colors = trimesh.visual.color.hex_to_rgba(COR)
    malha.export(PASTA / "suporte4_filuna.stl")
    malha.export(PASTA / "suporte4_filuna.3mf")
    relatorio = {
        "estanque": bool(malha.is_watertight), "volume_consistente": bool(malha.is_volume),
        "euler": int(malha.euler_number), "triangulos": len(malha.faces),
        "volume_cm3": round(malha.volume / 1000, 2), "medidas_mm": [round(v, 2) for v in malha.extents],
        "area_perfil_mm2": round(p.area, 2), "cor": COR,
    }
    (PASTA / "relatorio.json").write_text(json.dumps(relatorio, indent=1), encoding="utf-8")
    print(json.dumps(relatorio))


if __name__ == "__main__":
    main()
