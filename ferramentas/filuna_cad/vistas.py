"""Folha de vistas de uma peça: perspectiva, frente, lado, cima e um corte no meio, numa imagem só, com as medidas."""
import numpy as np
from PIL import Image, ImageDraw
from shapely.ops import unary_union

from .validar import carregar

LUZ = np.array([0.35, -0.5, 0.8]) / np.linalg.norm([0.35, -0.5, 0.8])
FUNDO, TRACO, CORTE = (24, 26, 32), (235, 235, 235), (240, 170, 60)

# Cada vista é a matriz que leva a peça para (direita, cima, para o observador).
VISTAS = {
    "frente": np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float),
    "lado": np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], float),
    "cima": np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float),
}


def _perspectiva():
    a, b = np.radians(35), np.radians(-40)
    gira_z = np.array([[np.cos(b), -np.sin(b), 0], [np.sin(b), np.cos(b), 0], [0, 0, 1]])
    deita = np.array([[1, 0, 0], [0, np.sin(a), np.cos(a)], [0, -np.cos(a), np.sin(a)]])
    return deita @ gira_z


def _quadro(m, matriz, lado):
    """Desenha a peça sombreada, do fundo para a frente, num quadro de `lado` pixels."""
    v = m.vertices @ matriz.T
    n = m.face_normals @ matriz.T
    tri = v[m.faces]
    mn, tam = v[:, :2].min(axis=0), np.ptp(v[:, :2], axis=0)
    esc = (lado - 24) / max(tam.max(), 1e-9)
    px = (tri[:, :, :2] - mn) * esc + (lado - tam * esc) / 2
    px[:, :, 1] = lado - px[:, :, 1]
    img = Image.new("RGB", (lado, lado), FUNDO)
    pincel = ImageDraw.Draw(img)
    luz = matriz @ LUZ
    for i in np.argsort(tri[:, :, 2].mean(axis=1)):
        if n[i, 2] <= 0:
            continue
        tom = int(70 + 170 * max(0.0, float(n[i] @ luz)))
        pincel.polygon([tuple(p) for p in px[i]], fill=(tom, tom, min(255, tom + 12)))
    return img


def _corte(m, lado):
    """Seção horizontal na meia altura: mostra paredes e vazios que as vistas de fora escondem."""
    z = (m.bounds[0][2] + m.bounds[1][2]) / 2
    img = Image.new("RGB", (lado, lado), FUNDO)
    secao = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if secao is None:
        return img
    plano, _ = secao.to_2D(to_2D=np.eye(4))
    forma = unary_union(plano.polygons_full)
    mn, tam = m.bounds[0][:2], m.extents[:2]
    esc = (lado - 24) / max(tam.max(), 1e-9)
    desloca = (lado - tam * esc) / 2

    def pixels(coords):
        p = (np.asarray(coords)[:, :2] - mn) * esc + desloca
        return [(float(x), float(lado - y)) for x, y in p]

    pincel = ImageDraw.Draw(img)
    for pol in getattr(forma, "geoms", [forma]):
        if pol.is_empty:
            continue
        pincel.polygon(pixels(pol.exterior.coords), fill=CORTE)
        for furo in pol.interiors:
            pincel.polygon(pixels(furo.coords), fill=FUNDO)
    return img


def folha(caminho_peca, saida, lado=420):
    """Grava a folha de vistas e devolve o que ela mostra."""
    m = carregar(caminho_peca)
    quadros = [("perspectiva", _quadro(m, _perspectiva(), lado))]
    quadros += [(nome, _quadro(m, mat, lado)) for nome, mat in VISTAS.items()]
    quadros.append(("corte na meia altura", _corte(m, lado)))
    x, y, z = (round(float(v), 1) for v in m.extents)
    legenda = [f"{x} x {y} x {z} mm", f"largura {x}  altura {z}", f"profundidade {y}  altura {z}", f"largura {x}  profundidade {y}",
               f"Z = {round(float(m.bounds[0][2] + z / 2), 1)} mm"]
    tela = Image.new("RGB", (lado * 3, lado * 2), FUNDO)
    pincel = ImageDraw.Draw(tela)
    for i, (nome, img) in enumerate(quadros):
        cx, cy = (i % 3) * lado, (i // 3) * lado
        tela.paste(img, (cx, cy))
        pincel.text((cx + 10, cy + 8), nome, fill=TRACO)
        pincel.text((cx + 10, cy + lado - 20), legenda[i], fill=TRACO)
    tela.save(saida)
    return {"arquivo": str(saida), "vistas": [n for n, _ in quadros], "medidas_mm": [x, y, z]}
