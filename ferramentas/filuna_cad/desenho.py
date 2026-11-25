"""Folha de desenho técnico em PDF, A3 deitada, 1º diedro (o usado no Brasil): frente, vista de cima, vista lateral
esquerda e perspectiva, com cotas gerais, diâmetro dos furos e legenda.

Arestas visíveis em traço contínuo e escondidas em tracejado, decididas por raios na malha. Serve para conferir,
orçar e mandar fazer; não substitui o desenho de fabricação com tolerâncias, que é de quem projeta.
"""
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np

from .validar import carregar
from .vistas import FUNDO, _perspectiva, _quadro

FOLHA = (420.0, 297.0)
MARGEM = 10.0
ESCALAS = (10, 5, 2, 1, 1 / 2, 1 / 5, 1 / 10, 1 / 20, 1 / 50)
ANGULO_ARESTA = np.radians(20)
# (direita, cima, para quem olha) de cada vista, no 1º diedro.
VISTAS = {
    "frente": np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float),
    "cima": np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float),
    "lateral esquerda": np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], float),
}


@dataclass
class Legenda:
    titulo: str = "Peça"
    material: str = "-"
    autor: str = "-"


def _arestas(m, olhar):
    """Arestas de quina, de contorno (silhueta) e de borda, vistas de `olhar`."""
    frente = m.face_normals @ olhar > 0
    par = m.face_adjacency
    quina = m.face_adjacency_angles > ANGULO_ARESTA
    silhueta = frente[par[:, 0]] != frente[par[:, 1]]
    arestas = m.face_adjacency_edges[quina | silhueta]
    normal = m.face_normals[par[quina | silhueta]].sum(axis=1)
    return arestas, normal / np.maximum(np.linalg.norm(normal, axis=1, keepdims=True), 1e-9)


def _visiveis(m, pontos, normais, olhar):
    """Cada ponto de aresta é visível se o raio até quem olha não bate na peça."""
    passo = 1e-3 * float(m.scale)
    inicio = pontos + olhar * passo + normais * passo
    return ~m.ray.intersects_any(inicio, np.tile(olhar, (len(pontos), 1)))


def _tracos(m, matriz, pedacos=8):
    """Segmentos 2D (em mm do modelo) visíveis e escondidos de uma vista."""
    olhar = matriz[2]
    arestas, normais = _arestas(m, olhar)
    a, b = m.vertices[arestas[:, 0]], m.vertices[arestas[:, 1]]
    t = (np.arange(pedacos) + 0.5) / pedacos
    meio = a[:, None] + (b - a)[:, None] * t[None, :, None]
    vis = _visiveis(m, meio.reshape(-1, 3), np.repeat(normais, pedacos, axis=0), olhar).reshape(-1, pedacos)
    ini = a[:, None] + (b - a)[:, None] * (t - 0.5 / pedacos)[None, :, None]
    fim = a[:, None] + (b - a)[:, None] * (t + 0.5 / pedacos)[None, :, None]
    seg = np.stack([ini, fim], axis=2).reshape(-1, 2, 3) @ matriz[:2].T
    vis = vis.reshape(-1)
    return seg[vis], seg[~vis]


def _furos(m):
    """Furos redondos vistos de cima: centro e diâmetro, achados em cortes horizontais."""
    achados = []
    for f in np.linspace(0.03, 0.97, 12):
        z = m.bounds[0][2] + f * m.extents[2]
        secao = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if secao is None:
            continue
        plano, _ = secao.to_2D(to_2D=np.eye(4))
        for pol in plano.polygons_full:
            for furo in pol.interiors:
                xy = np.asarray(furo.coords)[:-1, :2]
                centro = xy.mean(axis=0)
                raios = np.linalg.norm(xy - centro, axis=1)
                repetido = any(np.hypot(centro[0] - a[0], centro[1] - a[1]) < 0.5 for a in achados)
                if len(xy) >= 8 and raios.std() < 0.02 * raios.mean() and not repetido:
                    achados.append((round(float(centro[0]), 2), round(float(centro[1]), 2), round(float(2 * raios.mean()), 2)))
    return sorted(achados)


def _escala(m, celula):
    tamanho = np.array([m.extents[0] + m.extents[1], m.extents[2] + m.extents[1]])
    return next((e for e in ESCALAS if (tamanho * e <= celula).all()), ESCALAS[-1])


def _rotulo(e):
    return f"{int(e)}:1" if e >= 1 else f"1:{round(1 / e)}"


class _Folha:
    """Desenha em mm de papel: traços, cotas e textos."""

    def __init__(self, ax):
        self.ax = ax

    def segmentos(self, seg, origem, escala, largura, tracejado=False):
        from matplotlib.collections import LineCollection

        if len(seg):
            self.ax.add_collection(LineCollection(seg * escala + origem, colors="black", linewidths=largura,
                                                  linestyles=(0, (3, 1.5)) if tracejado else "solid"))

    def cota(self, p, q, afasta, texto):
        """Cota com linhas de chamada, seta nas duas pontas e o valor no meio."""
        p, q = np.asarray(p, float), np.asarray(q, float)
        direcao = (q - p) / max(np.linalg.norm(q - p), 1e-9)
        normal = np.array([-direcao[1], direcao[0]]) * afasta
        for ponto in (p, q):
            self.ax.plot(*zip(ponto + normal * 0.1, ponto + normal * 1.15), color="black", lw=0.25)
        self.ax.annotate("", xy=q + normal, xytext=p + normal, arrowprops={"arrowstyle": "<->", "lw": 0.35, "shrinkA": 0, "shrinkB": 0})
        meio = (p + q) / 2 + normal * 1.35
        angulo = np.degrees(np.arctan2(direcao[1], direcao[0]))
        self.ax.text(*meio, texto, ha="center", va="center", fontsize=7, rotation=angulo if abs(angulo) < 95 else angulo - 180)

    def texto(self, x, y, s, tamanho=7, **kw):
        self.ax.text(x, y, s, fontsize=tamanho, **kw)


def _vista(folha, m, nome, origem, escala):
    """Desenha uma vista com o canto de baixo à esquerda em `origem` e devolve o retângulo que ela ocupa."""
    matriz = VISTAS[nome]
    visivel, escondida = _tracos(m, matriz)
    canto = (m.bounds @ matriz[:2].T).min(axis=0)
    deslocar = np.asarray(origem) - canto * escala
    folha.segmentos(visivel, deslocar, escala, 0.5)
    folha.segmentos(escondida, deslocar, escala, 0.25, tracejado=True)
    tam = np.abs(m.extents @ np.abs(matriz[:2].T)) * escala
    folha.texto(origem[0], origem[1] - 7, nome.upper(), 8, weight="bold")
    return np.asarray(origem, float), tam


def _cotar(folha, vistas, m, furos, escala):
    from matplotlib.patches import Circle

    (o_f, t_f), (o_c, t_c), (o_l, t_l) = vistas["frente"], vistas["cima"], vistas["lateral esquerda"]
    x, y, z = (round(float(v), 2) for v in m.extents)
    folha.cota(o_f + [0, t_f[1]], o_f + t_f, 6, f"{x}")
    folha.cota(o_f, o_f + [0, t_f[1]], 6, f"{z}")
    folha.cota(o_l + [0, t_l[1]], o_l + t_l, 6, f"{y}")
    canto = m.bounds[0][:2]
    for cx, cy, d in furos:
        p = o_c + (np.array([cx, cy]) - canto) * escala
        folha.ax.add_patch(Circle(p, d * escala / 2, fill=False, lw=0.2, ls=":"))
        folha.ax.annotate(f"Ø{d}", xy=p + d * escala / 2 * np.array([0.7, 0.7]), xytext=p + [8, 8], fontsize=7,
                          arrowprops={"arrowstyle": "-", "lw": 0.3})


def _legenda(folha, legenda, escala, m):
    from matplotlib.patches import Rectangle

    x0, y0, w, h = FOLHA[0] - MARGEM - 180, MARGEM, 180, 32
    ax = folha.ax
    ax.add_patch(Rectangle((x0, y0), w, h, fill=False, lw=0.6))
    for yy in (y0 + 11, y0 + 21):
        ax.plot([x0, x0 + w], [yy, yy], color="black", lw=0.3)
    ax.plot([x0 + 110, x0 + 110], [y0, y0 + 21], color="black", lw=0.3)
    folha.texto(x0 + 3, y0 + 24.5, legenda.titulo, 11, weight="bold")
    folha.texto(x0 + 3, y0 + 14, f"Material: {legenda.material}")
    folha.texto(x0 + 3, y0 + 4, f"Medidas em mm  |  {' x '.join(str(round(float(v), 1)) for v in m.extents)}")
    folha.texto(x0 + 113, y0 + 14, f"Escala {_rotulo(escala)}  |  1º diedro")
    folha.texto(x0 + 113, y0 + 4, f"{legenda.autor}  |  {date.today():%d/%m/%Y}")


def desenhar(caminho, saida, legenda=None):
    """Grava o PDF da folha e devolve o que foi desenhado."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    legenda = legenda or Legenda(titulo=Path(caminho).stem)
    m = carregar(caminho)
    celula = np.array([(FOLHA[0] - 2 * MARGEM) * 0.62, (FOLHA[1] - 2 * MARGEM) * 0.78]) - 40
    escala = _escala(m, celula)
    fig = plt.figure(figsize=(FOLHA[0] / 25.4, FOLHA[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FOLHA[0])
    ax.set_ylim(0, FOLHA[1])
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(plt.Rectangle((MARGEM, MARGEM), FOLHA[0] - 2 * MARGEM, FOLHA[1] - 2 * MARGEM, fill=False, lw=0.8))
    folha = _Folha(ax)
    x, y, z = m.extents * escala
    base = np.array([MARGEM + 30, MARGEM + 30])
    vistas = {"cima": _vista(folha, m, "cima", base, escala)}
    vistas["frente"] = _vista(folha, m, "frente", base + [0, y + 25], escala)
    vistas["lateral esquerda"] = _vista(folha, m, "lateral esquerda", base + [x + 30, y + 25], escala)
    furos = _furos(m)
    _cotar(folha, vistas, m, furos, escala)
    iso = np.array(_quadro(m, _perspectiva(), 600))
    iso[(iso == FUNDO).all(axis=-1)] = 255   # fundo branco no papel
    ax.imshow(iso, extent=(FOLHA[0] - MARGEM - 130, FOLHA[0] - MARGEM - 10, FOLHA[1] - MARGEM - 130, FOLHA[1] - MARGEM - 10))
    folha.texto(FOLHA[0] - MARGEM - 130, FOLHA[1] - MARGEM - 6, "PERSPECTIVA (sem escala)", 8, weight="bold")
    _legenda(folha, legenda, escala, m)
    fig.savefig(saida)
    plt.close(fig)
    return {"arquivo": str(saida), "escala": _rotulo(escala), "vistas": list(VISTAS) + ["perspectiva"],
            "medidas_mm": [round(float(v), 2) for v in m.extents], "furos": [{"x": a, "y": b, "diametro_mm": d} for a, b, d in furos],
            "limites": "Cotas gerais e diâmetros de furos verticais. Sem tolerâncias, rugosidade nem cotas de cada detalhe."}
