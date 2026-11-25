"""Simulação estrutural linear (estática) com o CalculiX: quanto a peça deforma e onde a tensão passa do limite.

Malha de tetraedros de 10 nós feita pelo gmsh a partir do STEP (melhor) ou do STL. Uma face é presa e uma força total
em newtons é espalhada sobre outra. Unidades: mm, N, MPa.

Limites honestos: material linear e maciço. Peça impressa é mais fraca entre camadas e com pouco preenchimento;
por isso o fator de segurança pedido para peça impressa é 3, não 1,5. Tensão num canto vivo ou bem onde a força
encosta é exagerada pela malha: olhe também o valor de 99,5%.
"""
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .validar import carregar, nota


@dataclass(frozen=True)
class Material:
    nome: str
    modulo_mpa: float
    poisson: float
    limite_mpa: float
    impresso: bool


# Valores típicos de ficha técnica do material maciço (impresso a 100%), arredondados para baixo.
MATERIAIS = {
    "pla": Material("PLA impresso", 3500, 0.35, 40, True),
    "petg": Material("PETG impresso", 2000, 0.38, 35, True),
    "abs": Material("ABS impresso", 2000, 0.35, 30, True),
    "asa": Material("ASA impresso", 2000, 0.35, 30, True),
    "nylon": Material("Nylon (PA) impresso", 1500, 0.39, 40, True),
    "aco": Material("Aço 1020", 205000, 0.29, 250, False),
    "aluminio": Material("Alumínio 6061-T6", 69000, 0.33, 240, False),
}
FACES = {"xmin": (0, 0), "xmax": (0, 1), "ymin": (1, 0), "ymax": (1, 1), "zmin": (2, 0), "zmax": (2, 1)}
TEMPO = 300
NUMERO = r"[-+]?\d+(?:\.\d*)?(?:[eE][-+]?\d+)?"


@dataclass
class Caso:
    fixar: str = "zmin"
    carregar_em: str = "zmax"
    forca_n: tuple = (0.0, 0.0, -100.0)
    material: str = "pla"
    tamanho_mm: float = 0.0          # 0: um vigésimo da maior medida


def _malhar(caminho, pasta, tamanho):
    """Gera os tetraedros com o gmsh e grava `malha.inp` (formato que o CalculiX lê)."""
    import gmsh

    gmsh.initialize(["-nt", "2"])
    gmsh.option.setNumber("General.Terminal", 0)
    try:
        if str(caminho).lower().endswith((".step", ".stp")):
            gmsh.model.occ.importShapes(str(caminho))
            gmsh.model.occ.synchronize()
        else:
            stl = Path(pasta) / "peca.stl"
            carregar(caminho).export(stl, file_type="stl_ascii")   # o gmsh recusa STL binário com cabeçalho zerado
            gmsh.merge(str(stl))
            gmsh.model.mesh.classifySurfaces(np.radians(40), True, True, np.pi)
            gmsh.model.mesh.createGeometry()
            cascas = [s for _, s in gmsh.model.getEntities(2)]
            gmsh.model.geo.addVolume([gmsh.model.geo.addSurfaceLoop(cascas)])
            gmsh.model.geo.synchronize()
        volumes = [v for _, v in gmsh.model.getEntities(3)]
        if not volumes:
            raise ValueError("A peça não forma um volume fechado: não dá para simular.")
        gmsh.model.addPhysicalGroup(3, volumes, name="PECA")
        gmsh.option.setNumber("Mesh.MeshSizeMax", tamanho)
        gmsh.option.setNumber("Mesh.MeshSizeMin", tamanho / 4)
        gmsh.option.setNumber("Mesh.ElementOrder", 2)
        gmsh.option.setNumber("Mesh.SaveAll", 0)
        gmsh.model.mesh.generate(3)
        etiquetas, coords, _ = gmsh.model.mesh.getNodes()
        gmsh.write(str(Path(pasta) / "malha.inp"))
        return {int(t): c for t, c in zip(etiquetas, coords.reshape(-1, 3))}
    finally:
        gmsh.finalize()


def _nos_da_face(nos, face, tolerancia):
    """Números dos nós que estão na face pedida da caixa da peça (por exemplo zmin, a base)."""
    eixo, lado = FACES[face]
    valores = {t: c[eixo] for t, c in nos.items()}
    alvo = max(valores.values()) if lado else min(valores.values())
    return np.array(sorted(t for t, v in valores.items() if abs(v - alvo) <= tolerancia))


def _lista(ids):
    return "\n".join(", ".join(str(i) for i in ids[k:k + 12]) for k in range(0, len(ids), 12))


def _entrada(caso, mat, nos, presos, carregados):
    forca = np.asarray(caso.forca_n, float) / len(carregados)
    cargas = [f"CARGA, {i + 1}, {v:.6g}" for i, v in enumerate(forca) if v]
    return "\n".join([
        "*INCLUDE, INPUT=malha.inp",
        "*NSET, NSET=TODOS", _lista(sorted(nos)),
        "*NSET, NSET=PRESA", _lista(presos),
        "*NSET, NSET=CARGA", _lista(carregados),
        "*MATERIAL, NAME=MAT", "*ELASTIC", f"{mat.modulo_mpa}, {mat.poisson}",
        "*SOLID SECTION, ELSET=PECA, MATERIAL=MAT",
        "*STEP", "*STATIC",
        "*BOUNDARY", "PRESA, 1, 3",
        "*CLOAD", *cargas,
        "*NODE PRINT, NSET=TODOS", "U",
        "*EL PRINT, ELSET=PECA", "S",
        "*END STEP", ""])


def _ler_resultado(dat):
    """Deslocamentos por nó e tensões por ponto de integração, do arquivo .dat do CalculiX."""
    texto = Path(dat).read_text(errors="replace")
    blocos = dict(re.findall(r"\n\s*(displacements|stresses) \([^\n]*\n(.*?)(?=\n\s*[a-z]+ \(|\Z)", texto, re.S))
    linha_u = re.compile(rf"^\s*(\d+)\s+({NUMERO})\s+({NUMERO})\s+({NUMERO})\s*$", re.M)
    linha_s = re.compile(rf"^\s*(\d+)\s+\d+" + rf"\s+({NUMERO})" * 6 + r"\s*$", re.M)
    if not {"displacements", "stresses"} <= blocos.keys():
        raise RuntimeError("O CalculiX não gravou deslocamentos e tensões no resultado.")
    linhas_u = linha_u.findall(blocos["displacements"])
    u = {int(g[0]): np.array([float(v) for v in g[1:]]) for g in linhas_u}
    s = np.array([[float(v) for v in g[1:]] for g in linha_s.findall(blocos["stresses"])])
    sxx, syy, szz, sxy, sxz, syz = s.T
    mises = np.sqrt(0.5 * ((sxx - syy) ** 2 + (syy - szz) ** 2 + (szz - sxx) ** 2) + 3 * (sxy ** 2 + sxz ** 2 + syz ** 2))
    return u, mises


def simular(caminho, caso=None):
    caso = caso or Caso()
    mat = MATERIAIS[caso.material]
    ccx = shutil.which("ccx") or shutil.which("ccx_2.21")
    if not ccx:
        raise RuntimeError("CalculiX (ccx) não está instalado: apt install calculix-ccx")
    with tempfile.TemporaryDirectory(prefix="filuna-simular-") as pasta:
        extensao = np.ptp(carregar(caminho).bounds, axis=0)
        tamanho = caso.tamanho_mm or float(extensao.max()) / 20
        nos = _malhar(caminho, pasta, tamanho)
        tolerancia = max(0.3, 0.01 * float(extensao.max()))
        presos, carregados = (_nos_da_face(nos, f, tolerancia) for f in (caso.fixar, caso.carregar_em))
        Path(pasta, "caso.inp").write_text(_entrada(caso, mat, nos, presos, carregados))
        ambiente = {**os.environ, "OMP_NUM_THREADS": "2"}
        r = subprocess.run([ccx, "-i", "caso"], cwd=pasta, capture_output=True, text=True, timeout=TEMPO, env=ambiente, check=False)
        dat = Path(pasta, "caso.dat")
        if not dat.exists() or "*ERROR" in r.stdout:
            erro = next((linha for linha in r.stdout.splitlines() if "ERROR" in linha), "sem mensagem")
            raise RuntimeError(f"O CalculiX não resolveu o caso: {erro.strip()}")
        u, mises = _ler_resultado(dat)
    return _relatorio(caminho, caso, mat, (nos, presos, carregados), u, mises)


def _relatorio(caminho, caso, mat, malha, u, mises):
    nos, presos, carregados = malha
    maior = max(u, key=lambda t: float(np.linalg.norm(u[t])))
    pico, p995 = float(mises.max()), float(np.percentile(mises, 99.5))
    pedido = 3.0 if mat.impresso else 1.5
    r = {"arquivo": str(caminho), "material": mat.nome, "modulo_mpa": mat.modulo_mpa, "limite_mpa": mat.limite_mpa,
         "presa_em": caso.fixar, "forca_em": caso.carregar_em, "forca_n": list(caso.forca_n),
         "nos": int(len(nos)), "nos_presos": int(len(presos)), "nos_com_forca": int(len(carregados)),
         "deslocamento_max_mm": round(float(np.linalg.norm(u[maior])), 4),
         "deslocamento_max_em": [round(float(v), 2) for v in nos[maior]],
         "tensao_max_mpa": round(pico, 2), "tensao_995_mpa": round(p995, 2),
         "fator_de_seguranca": round(mat.limite_mpa / max(pico, 1e-9), 2),
         "fator_de_seguranca_995": round(mat.limite_mpa / max(p995, 1e-9), 2), "fator_pedido": pedido}
    a = []
    if r["fator_de_seguranca_995"] < 1:
        a.append(("erro", "tensao", f"A tensão passa do limite do material ({p995:.1f} > {mat.limite_mpa} MPa): a peça quebra ou deforma de vez."))
    elif r["fator_de_seguranca_995"] < pedido:
        a.append(("aviso", "tensao", f"Fator de segurança {r['fator_de_seguranca_995']} abaixo de {pedido}: reforce a região mais tensionada."))
    if r["fator_de_seguranca"] < 1 <= r["fator_de_seguranca_995"]:
        a.append(("aviso", "pico", "O pico passa do limite só em poucos pontos: costuma ser canto vivo ou o ponto da força. Arredonde o canto."))
    if mat.impresso:
        a.append(("aviso", "camadas", "Peça impressa é mais fraca entre camadas: deite a peça para a força não puxar as camadas."))
    r["achados"] = [{"gravidade": g, "tema": t, "texto": x} for g, t, x in a]
    r["nota"] = nota([i for i in r["achados"] if i["tema"] != "camadas"])
    r["aprovada"] = not any(i["gravidade"] == "erro" for i in r["achados"])
    r["limites"] = ("Estática linear, material maciço e isotrópico, força espalhada por igual na face. Não prevê fadiga, "
                    "flambagem, impacto nem a resistência real de cada impressão.")
    return r
