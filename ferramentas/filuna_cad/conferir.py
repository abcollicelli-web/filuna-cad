"""Conferência formal de um arquivo de CAD pelo formato: STEP, STL, 3MF, OBJ, GLB ou DXF.

Diz se o arquivo é o que diz ser antes de alguém usar: sólido válido no STEP, malha fechada no STL e no 3MF,
malhas e materiais no GLB, contornos fechados e unidade no DXF. Não julga se a peça imprime ou fabrica bem:
para isso há `validar` e `fabricar`.
"""
from pathlib import Path

import trimesh

from .validar import medir_malha, nota

UNIDADES_DXF = {0: "sem unidade", 1: "polegada", 2: "pé", 4: "mm", 5: "cm", 6: "m"}


def _achado(gravidade, tema, texto):
    return {"gravidade": gravidade, "tema": tema, "texto": texto}


def conferir_step(caminho):
    import build123d as bd

    forma = bd.import_step(str(caminho))
    solidos = forma.solids()
    # Casca fechada: toda aresta é dividida por exatamente duas faces.
    cascas_abertas = sum(1 for c in forma.shells() if not c.is_manifold)
    r = {"formato": "STEP", "valido": bool(forma.is_valid), "solidos": len(solidos), "cascas_abertas": cascas_abertas,
         "faces": len(forma.faces()), "volume_cm3": round(sum(s.volume for s in solidos) / 1000, 3),
         "medidas_mm": [round(v, 2) for v in forma.bounding_box().size]}
    a = []
    if not r["valido"]:
        a.append(_achado("erro", "step", "O núcleo de CAD diz que a forma é inválida: faces ou arestas quebradas."))
    if not solidos:
        a.append(_achado("erro", "step", "Não há sólido no arquivo, só superfícies: não dá volume nem malha fechada."))
    if cascas_abertas:
        a.append(_achado("erro", "step", f"{cascas_abertas} casca(s) aberta(s): falta face para fechar o volume."))
    return r, a


def conferir_malha(caminho, formato):
    cena = trimesh.load(caminho, force="scene", process=True)
    malhas = list(cena.dump())
    if not malhas:
        return {"formato": formato, "malhas": 0}, [_achado("erro", "malha", "O arquivo não tem nenhuma malha.")]
    unida = trimesh.util.concatenate(malhas)
    r = {"formato": formato, "malhas": len(malhas), **medir_malha(unida)}
    a = []
    abertas = sum(1 for m in malhas if not m.is_watertight)
    if abertas:
        a.append(_achado("erro", "malha", f"{abertas} de {len(malhas)} malha(s) não fecham: o fatiador pode sumir com partes."))
    if not r["faces_para_fora"]:
        a.append(_achado("aviso", "malha", "Há triângulos virados ao contrário: o lado de dentro e o de fora se confundem."))
    if r["triangulos_sem_area"]:
        a.append(_achado("aviso", "malha", f"{r['triangulos_sem_area']} triângulos sem área: limpe a malha antes de exportar."))
    if formato == "GLB":
        r["materiais"] = len({id(getattr(m.visual, "material", None)) for m in malhas})
        if max(r["medidas_mm"]) < 5:
            a.append(_achado("aviso", "unidade", "A peça mede menos de 5 em tudo: o GLB costuma vir em metros; confira a escala."))
    return r, a


def _pontas_soltas(msp):
    """Pontas de linha e arco que não encostam em outra: contorno aberto não corta nem extruda."""
    from collections import Counter

    pontas = Counter()
    for e in msp.query("LINE ARC"):
        ini, fim = (e.dxf.start, e.dxf.end) if e.dxftype() == "LINE" else (e.start_point, e.end_point)
        for p in (ini, fim):
            pontas[(round(p.x, 3), round(p.y, 3))] += 1
    return sum(1 for n in pontas.values() if n == 1)


def conferir_dxf(caminho):
    import ezdxf
    from ezdxf import bbox

    doc = ezdxf.readfile(str(caminho))
    msp = doc.modelspace()
    tipos = {}
    for e in msp:
        tipos[e.dxftype()] = tipos.get(e.dxftype(), 0) + 1
    polis = list(msp.query("LWPOLYLINE POLYLINE"))
    abertas = sum(1 for p in polis if not p.closed)
    caixa = bbox.extents(msp)
    unidade = UNIDADES_DXF.get(doc.header.get("$INSUNITS", 0), "outra")
    r = {"formato": "DXF", "versao": doc.dxfversion, "unidade": unidade, "entidades": tipos,
         "polilinhas_abertas": abertas, "pontas_soltas": _pontas_soltas(msp),
         "medidas": [round(v, 3) for v in caixa.size][:2] if caixa.has_data else None}
    a = []
    if not caixa.has_data:
        a.append(_achado("erro", "dxf", "O desenho está vazio."))
    if unidade != "mm":
        a.append(_achado("aviso", "unidade", f"Unidade do desenho: {unidade}. Corte a laser e CNC esperam mm; confira a escala."))
    if abertas or r["pontas_soltas"]:
        a.append(_achado("aviso", "contorno", f"{abertas} polilinha(s) aberta(s) e {r['pontas_soltas']} ponta(s) solta(s): "
                                               "contorno aberto não corta nem vira extrusão."))
    if "SPLINE" in tipos:
        a.append(_achado("aviso", "dxf", "Há splines: algumas máquinas de corte não leem; converta em arcos ou polilinhas."))
    return r, a


FORMATOS = {".step": conferir_step, ".stp": conferir_step, ".dxf": conferir_dxf,
            ".stl": lambda c: conferir_malha(c, "STL"), ".3mf": lambda c: conferir_malha(c, "3MF"),
            ".obj": lambda c: conferir_malha(c, "OBJ"), ".glb": lambda c: conferir_malha(c, "GLB")}


def conferir(caminho):
    """Confere o arquivo pelo formato da extensão e devolve medidas, achados e nota."""
    extensao = Path(caminho).suffix.lower()
    if extensao not in FORMATOS:
        raise ValueError(f"Formato {extensao} não é conferido. Aceitos: {', '.join(sorted(FORMATOS))}")
    r, a = FORMATOS[extensao](caminho)
    r.update(arquivo=str(caminho), achados=a, nota=nota(a), aprovada=not any(i["gravidade"] == "erro" for i in a))
    return r
