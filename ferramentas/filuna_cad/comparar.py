"""Compara duas peças (são a mesma forma?) e uma peça com uma imagem de referência (raio-x de silhueta)."""
import manifold3d as m3d
import numpy as np
from PIL import Image, ImageDraw

from .validar import carregar

EIXOS = {"frente": (0, 2), "lado": (1, 2), "cima": (0, 1)}


def _solido(m):
    return m3d.Manifold(m3d.Mesh(np.asarray(m.vertices, dtype=np.float32), np.asarray(m.faces, dtype=np.uint32)))


def comparar_pecas(caminho_a, caminho_b):
    """Sobreposição de volume (1,0 = idênticas) e diferença de medidas. As duas malhas precisam ser fechadas."""
    a, b = carregar(caminho_a), carregar(caminho_b)
    sa, sb = _solido(a), _solido(b)
    dentro, juntas = (sa ^ sb).volume(), (sa + sb).volume()
    return {
        "sobreposicao": round(dentro / juntas, 6) if juntas else 0.0,
        "volume_a_cm3": round(sa.volume() / 1000, 3),
        "volume_b_cm3": round(sb.volume() / 1000, 3),
        "diferenca_medidas_mm": [round(float(v), 3) for v in np.abs(a.extents - b.extents)],
    }


def silhueta(m, vista="frente", lado=512):
    """Sombra da peça vista de um eixo, como máscara quadrada: a peça ocupa a maior dimensão inteira."""
    i, j = EIXOS[vista]
    p = m.vertices[:, [i, j]]
    mn, tam = p.min(axis=0), np.ptp(p, axis=0)
    esc = (lado - 1) / tam.max()
    px = (p - mn) * esc + (lado - 1 - tam * esc) / 2
    px[:, 1] = lado - 1 - px[:, 1]
    img = Image.new("1", (lado, lado), 0)
    pincel = ImageDraw.Draw(img)
    for f in m.faces:
        pincel.polygon([tuple(px[k]) for k in f], fill=1)
    return np.asarray(img, dtype=bool)


def mascara_da_imagem(caminho, lado=512, tolerancia=30):
    """Recorta o objeto de uma foto de fundo liso (cor do canto) ou transparente, no mesmo enquadramento da silhueta."""
    img = Image.open(caminho).convert("RGBA")
    px = np.asarray(img).astype(int)
    if (px[..., 3] < 250).any():
        obj = px[..., 3] > 128
    else:
        obj = np.abs(px[..., :3] - px[0, 0, :3]).sum(axis=2) > tolerancia
    ys, xs = np.nonzero(obj)
    if not len(ys):
        raise ValueError("Não achei o objeto na imagem: o fundo precisa ser liso ou transparente.")
    corte = obj[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    esc = (lado - 1) / max(corte.shape)
    novo = (max(1, round(corte.shape[1] * esc)), max(1, round(corte.shape[0] * esc)))
    red = np.asarray(Image.fromarray(corte).resize(novo, Image.NEAREST))
    tela = np.zeros((lado, lado), bool)
    y0, x0 = (lado - red.shape[0]) // 2, (lado - red.shape[1]) // 2
    tela[y0:y0 + red.shape[0], x0:x0 + red.shape[1]] = red
    return tela


def raio_x(caminho_peca, caminho_imagem, vista="frente", saida=None):
    """Semelhança da silhueta (0 a 1) entre a peça e a referência. Com `saida`, grava a sobreposição colorida:
    branco = igual, vermelho = só na referência (falta na peça), azul = só na peça (sobra)."""
    a = silhueta(carregar(caminho_peca), vista)
    b = mascara_da_imagem(caminho_imagem)
    uniao = (a | b).sum()
    if saida:
        cor = np.zeros(a.shape + (3,), np.uint8)
        cor[a & b] = (255, 255, 255)
        cor[b & ~a] = (220, 40, 40)
        cor[a & ~b] = (40, 90, 220)
        Image.fromarray(cor).save(saida)
    return {"vista": vista, "semelhanca": round(float((a & b).sum() / uniao), 4) if uniao else 0.0,
            "falta_na_peca": round(float((b & ~a).sum() / b.sum()), 4), "sobra_na_peca": round(float((a & ~b).sum() / a.sum()), 4)}
