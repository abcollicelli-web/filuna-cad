"""Valida uma peça para impressão FDM na posição em que está no arquivo (Z para cima, apoiada em Z mínimo).

Mede malha, apoio na mesa, balanços, espessura de parede, estabilidade e se cabe na impressora, e dá uma nota de 0 a 100.
Não substitui o fatiador: tempo, gramas e suporte reais só saem dele.
"""
from dataclasses import dataclass

import numpy as np
import trimesh
from shapely.geometry import MultiPoint, Point

PAREDE_MINIMA = 0.8      # duas passadas de bico 0,4 mm
PAREDE_FRAGIL = 2.0      # abaixo disso uma parede solta quebra na mão
ANGULO_BALANCO = 45.0    # graus a partir da vertical que imprimem sem suporte
FOLGA_Z = 0.02
LOTE_RAIOS = 400         # raios por vez: sem o Embree o trimesh gasta memória na proporção de raios x triângulos


@dataclass
class Limites:
    mesa: tuple = (256.0, 256.0, 256.0)
    amostras: int = 4000
    semente: int = 7


def malha_do_step(caminho, tolerancia=0.02):
    """Triangula um STEP com o núcleo OCCT (precisa do build123d) e devolve a malha em mm."""
    import build123d as bd

    forma = bd.import_step(str(caminho))
    vertices, triangulos = forma.tessellate(tolerancia, 0.2)
    return trimesh.Trimesh([tuple(v) for v in vertices], triangulos, process=True)


def carregar(caminho):
    """Lê STL, 3MF, OBJ, GLB ou STEP como uma malha só, já com as posições das peças aplicadas."""
    if str(caminho).lower().endswith((".step", ".stp")):
        return malha_do_step(caminho)
    cena = trimesh.load(caminho, process=True)
    if isinstance(cena, trimesh.Scene):
        partes = cena.dump()
        if not len(partes):
            raise ValueError(f"{caminho} não tem malha")
        return trimesh.util.concatenate(partes)
    return cena


def medir_malha(m):
    return {
        "fechada": bool(m.is_watertight),
        "faces_para_fora": bool(m.is_winding_consistent),
        "volume_valido": bool(m.is_volume),
        "cascas": int(m.body_count),
        "triangulos": int(len(m.faces)),
        "triangulos_sem_area": int((m.area_faces < 1e-9).sum()),
        "volume_cm3": round(float(abs(m.volume)) / 1000, 3),
        "medidas_mm": [round(float(v), 2) for v in m.extents],
    }


def medir_mesa(m):
    """Área que encosta na mesa e quanto ela representa da sombra da peça."""
    z0 = m.bounds[0][2]
    embaixo = (m.face_normals[:, 2] < -0.999) & (m.triangles[:, :, 2].max(axis=1) < z0 + FOLGA_Z)
    area = float(m.area_faces[embaixo].sum())
    sombra = float(MultiPoint(m.vertices[:, :2]).convex_hull.area)
    return {"apoio_mm2": round(area, 1), "apoio_sobre_sombra": round(area / sombra, 3) if sombra else 0.0}, embaixo


def medir_balancos(m, embaixo):
    """Faces viradas para baixo, fora da mesa, mais deitadas que o ângulo que imprime no ar."""
    # Meio grau de tolerância: um chanfro desenhado a 45 graus exatos não pode cair para o lado errado por arredondamento.
    limite = -np.sin(np.radians(ANGULO_BALANCO + 0.5))
    ruins = (m.face_normals[:, 2] < limite) & ~embaixo
    area = float(m.area_faces[ruins].sum())
    pior = None
    if ruins.any():
        i = np.flatnonzero(ruins)[np.argmax(m.area_faces[ruins])]
        pior = [round(float(v), 2) for v in m.triangles_center[i]]
    return {"area_mm2": round(area, 1), "maior_face_em": pior}


def medir_paredes(m, lim):
    """Espessura medida por raios: de cada ponto da superfície para dentro, até sair do outro lado."""
    pontos, faces = trimesh.sample.sample_surface(m, lim.amostras, seed=lim.semente)
    normais = m.face_normals[faces]
    achados = [m.ray.intersects_location(pontos[i:i + LOTE_RAIOS] - normais[i:i + LOTE_RAIOS] * 1e-3, -normais[i:i + LOTE_RAIOS],
                                         multiple_hits=False) + (i,) for i in range(0, len(pontos), LOTE_RAIOS)]
    onde = np.concatenate([a[0] for a in achados])
    raio = np.concatenate([a[1] + a[3] for a in achados])
    bateu = np.concatenate([a[2] for a in achados])
    # Só conta como parede quando a face do outro lado é quase paralela: numa quina a espessura cai a zero sem ser defeito.
    parede = np.einsum("ij,ij->i", m.face_normals[bateu], normais[raio]) < -0.7
    onde, raio = onde[parede], raio[parede]
    if not len(raio):
        return {"medida": False}
    esp = np.linalg.norm(onde - pontos[raio], axis=1)
    i = int(np.argmin(esp))
    return {
        "medida": True,
        "minima_mm": round(float(esp[i]), 2),
        "minima_em": [round(float(v), 2) for v in pontos[raio][i]],
        "p05_mm": round(float(np.percentile(esp, 5)), 2),
        "mediana_mm": round(float(np.median(esp)), 2),
        "amostras": int(len(esp)),
    }


def medir_estabilidade(m, embaixo):
    """O centro de massa cai dentro da área de apoio? Margem em mm até a borda (negativa: tomba)."""
    if not embaixo.any() or not m.is_volume:
        return {"medida": False}
    base = MultiPoint(m.triangles[embaixo].reshape(-1, 3)[:, :2]).convex_hull
    cm = Point(m.center_mass[:2])
    margem = base.exterior.distance(cm) if base.geom_type == "Polygon" else 0.0
    dentro = base.contains(cm)
    return {"medida": True, "margem_mm": round(float(margem if dentro else -margem), 2),
            "altura_cm_mm": round(float(m.center_mass[2] - m.bounds[0][2]), 2)}


def cabe(m, mesa):
    x, y, z = m.extents
    return bool(z <= mesa[2] and ((x <= mesa[0] and y <= mesa[1]) or (y <= mesa[0] and x <= mesa[1])))


def achados(r):
    """Cada problema com gravidade (erro ou aviso), para o agente corrigir antes de imprimir."""
    a = []
    ml, p, e = r["malha"], r["paredes"], r["estabilidade"]
    if not ml["fechada"] or not ml["volume_valido"]:
        a.append(("erro", "malha", "A malha não é fechada: o fatiador pode abrir buracos ou sumir com partes."))
    if ml["cascas"] > 1:
        a.append(("aviso", "malha", f"A peça tem {ml['cascas']} cascas soltas: confirme que são peças separadas de propósito."))
    if not r["cabe_na_mesa"]:
        a.append(("erro", "mesa", "A peça não cabe na impressora informada."))
    if r["mesa"]["apoio_mm2"] < 20:
        a.append(("erro", "apoio", "Quase nada encosta na mesa: a peça descola. Vire a peça ou crie uma face plana."))
    elif r["mesa"]["apoio_sobre_sombra"] < 0.15:
        a.append(("aviso", "apoio", "Pouco apoio para o tamanho da peça: use aba (brim) ou mude a posição."))
    if r["balancos"]["area_mm2"] > 1:
        a.append(("aviso", "balanco", f"{r['balancos']['area_mm2']} mm² pedem suporte. Chanfre a 45 graus ou vire a peça."))
    if p.get("medida"):
        if p["minima_mm"] < PAREDE_MINIMA:
            a.append(("erro", "parede", f"Parede de {p['minima_mm']} mm em {p['minima_em']}: menos que duas passadas do bico."))
        elif p["minima_mm"] < PAREDE_FRAGIL:
            a.append(("aviso", "parede", f"Parede de {p['minima_mm']} mm em {p['minima_em']}: imprime, mas é frágil se ficar solta."))
    if e.get("medida") and e["margem_mm"] < 0:
        a.append(("erro", "estabilidade", "O centro de massa cai fora do apoio: a peça tomba durante a impressão."))
    return [{"gravidade": g, "tema": t, "texto": x} for g, t, x in a]


def nota(lista):
    """100 menos 25 por erro e 8 por aviso, sem passar de zero."""
    erros = sum(1 for i in lista if i["gravidade"] == "erro")
    avisos = len(lista) - erros
    return max(0, 100 - 25 * erros - 8 * avisos)


def validar(caminho, lim=None):
    lim = lim or Limites()
    m = carregar(caminho)
    mesa, embaixo = medir_mesa(m)
    r = {
        "arquivo": str(caminho),
        "malha": medir_malha(m),
        "mesa": mesa,
        "balancos": medir_balancos(m, embaixo),
        "paredes": medir_paredes(m, lim),
        "estabilidade": medir_estabilidade(m, embaixo),
        "cabe_na_mesa": cabe(m, lim.mesa),
    }
    r["achados"] = achados(r)
    r["nota"] = nota(r["achados"])
    r["aprovada"] = not any(i["gravidade"] == "erro" for i in r["achados"])
    return r
