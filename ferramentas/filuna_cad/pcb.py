"""Placas KiCad pelo `kicad-cli`: regras da placa (DRC), regras do esquema (ERC), medidas da placa e STEP 3D
para desenhar a caixa em volta dela.
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .validar import nota

TEMPO = 180


def _cli():
    cli = shutil.which("kicad-cli")
    if not cli:
        raise RuntimeError("O kicad-cli não está instalado (KiCad 8 ou mais novo).")
    return cli


def _rodar(*args):
    ambiente = {**os.environ, "HOME": os.environ.get("HOME") or tempfile.gettempdir()}
    r = subprocess.run([_cli(), *args], capture_output=True, text=True, timeout=TEMPO, env=ambiente, check=False)
    if r.returncode not in (0, 5):     # 5: o kicad-cli achou violações, que é resultado e não falha
        raise RuntimeError(f"O kicad-cli falhou: {(r.stderr or r.stdout).strip()[:300]}")
    return r


def _violacoes(relatorio, chaves):
    itens = []
    for chave in chaves:
        for grupo in relatorio.get(chave, []):
            for v in grupo.get("violations", [grupo]) if chave == "sheets" else [grupo]:
                itens.append(v)
    return itens


def _achados(itens, tema):
    a = []
    for v in itens:
        gravidade = "erro" if v.get("severity") == "error" else "aviso"
        onde = v.get("items", [{}])[0].get("description", "")
        a.append({"gravidade": gravidade, "tema": tema, "texto": f"{v.get('description', v.get('type'))}. {onde}".strip()})
    return a


def _medidas(caminho):
    """Tamanho da placa pelas linhas do recorte (Edge.Cuts), lidas do próprio arquivo."""
    import sexpdata

    arvore = sexpdata.loads(Path(caminho).read_text(encoding="utf-8"))
    xs, ys, camadas = [], [], 0

    def visitar(no):
        nonlocal camadas
        if not isinstance(no, list) or not no:
            return
        cabeca = str(no[0])
        if cabeca == "layers" and camadas == 0:
            camadas = sum(1 for c in no[1:] if isinstance(c, list) and len(c) > 1 and str(c[1]).endswith(".Cu"))
        if cabeca.startswith("gr_") and any(isinstance(c, list) and str(c[0]) == "layer" and str(c[1]) == "Edge.Cuts" for c in no):
            for c in no:
                if isinstance(c, list) and str(c[0]) in {"start", "end", "center", "mid", "xy"}:
                    xs.append(float(c[1]))
                    ys.append(float(c[2]))
        for c in no:
            visitar(c)

    visitar(arvore)
    medidas = [round(max(xs) - min(xs), 2), round(max(ys) - min(ys), 2)] if xs else None
    return medidas, camadas


def drc(caminho):
    with tempfile.TemporaryDirectory() as pasta:
        saida = Path(pasta) / "drc.json"
        _rodar("pcb", "drc", "--format", "json", "--severity-all", "--units", "mm", "-o", str(saida), str(caminho))
        rel = json.loads(saida.read_text())
    itens = _violacoes(rel, ["violations", "unconnected_items"])
    a = _achados(itens, "drc")
    medidas, camadas = _medidas(caminho)
    if medidas is None:
        a.append({"gravidade": "erro", "tema": "contorno", "texto": "A placa não tem contorno na camada Edge.Cuts."})
    return _fechar({"tipo": "placa", "medidas_mm": medidas, "camadas_de_cobre": camadas,
                    "violacoes": len(rel.get("violations", [])), "sem_ligacao": len(rel.get("unconnected_items", []))}, a, caminho)


def erc(caminho):
    with tempfile.TemporaryDirectory() as pasta:
        saida = Path(pasta) / "erc.json"
        _rodar("sch", "erc", "--format", "json", "--severity-all", "-o", str(saida), str(caminho))
        rel = json.loads(saida.read_text())
    itens = _violacoes(rel, ["sheets"])
    return _fechar({"tipo": "esquema", "violacoes": len(itens)}, _achados(itens, "erc"), caminho)


def exportar_step(caminho, saida):
    """STEP 3D da placa com os componentes que têm modelo: base para desenhar a caixa."""
    _rodar("pcb", "export", "step", "--subst-models", "--force", "-o", str(saida), str(caminho))
    return {"arquivo": str(saida), "placa": str(caminho)}


def _fechar(r, a, caminho):
    r.update(arquivo=str(caminho), achados=a, nota=nota(a), aprovada=not any(i["gravidade"] == "erro" for i in a))
    return r
