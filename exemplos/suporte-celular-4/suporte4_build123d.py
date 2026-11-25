"""Suporte de celular "4" em build123d: mesmo perfil dos outros dois, com saída em STEP para editar num CAD."""
import math
from pathlib import Path

import build123d as bd

PASTA = Path(__file__).parent
PROFUNDIDADE, FENDA, FUNDO = 80.0, 11.0, 10.0
CANTO = (70.0, 110.0)
ANGULOS = ((16.0, 55.0), (16.0, 65.0), (52.0, 82.0))


def retangulo(x0, y0, x1, y1):
    return bd.Polygon((x0, y0), (x1, y0), (x1, y1), (x0, y1), align=None)


def fenda(y_sup, graus):
    a = math.radians(graus)
    x = CANTO[0] + (CANTO[1] - y_sup) / math.tan(a)
    base = retangulo(0, -FUNDO / math.sin(a), FENDA, 40)
    return bd.Pos(x, y_sup) * bd.Rot(0, 0, 90 - graus) * base


def suporte():
    quatro = (retangulo(20, 0, 160, 16) + retangulo(50, 0, 70, 110) + retangulo(0, 34, 94, 52)
              + bd.Polygon((0, 34), (22, 34), (70, 92), (70, 110), (50, 110), (0, 52), align=None))
    for y, g in ANGULOS:
        quatro -= fenda(y, g)
    return bd.extrude(quatro, PROFUNDIDADE)


if __name__ == "__main__":
    peca = suporte()
    bd.export_step(peca, str(PASTA / "suporte4_build123d.step"))
    bd.export_stl(peca, str(PASTA / "suporte4_build123d.stl"), tolerance=0.02)
    print(round(peca.volume / 1000, 2), "cm3")
