"""Linha de comando: python -m filuna_cad <comando> ... (python -m filuna_cad --help lista todos)."""
import argparse
import json
import sys
from pathlib import Path

from . import comparar, conferir, cupom, desenho, fabricar, orientar, pcb, robo, simular, validar, ver, vistas


def _mesa(texto):
    partes = tuple(float(v) for v in texto.lower().split("x"))
    if len(partes) != 3:
        raise argparse.ArgumentTypeError("use LARGURAxPROFUNDIDADExALTURA, por exemplo 256x256x256")
    return partes


def _resumo(r):
    linhas = [f"{'APROVADA' if r['aprovada'] else 'REPROVADA'}  nota {r['nota']}/100  {r['arquivo']}"]
    ml, p = r["malha"], r["paredes"]
    linhas.append(f"  malha: {'fechada' if ml['fechada'] else 'ABERTA'}, {ml['triangulos']} triângulos, "
                  f"{ml['volume_cm3']} cm³, {ml['medidas_mm']} mm")
    linhas.append(f"  mesa: apoio {r['mesa']['apoio_mm2']} mm², balanço {r['balancos']['area_mm2']} mm²")
    if p.get("medida"):
        linhas.append(f"  parede: mínima {p['minima_mm']} mm, 5% abaixo de {p['p05_mm']} mm")
    linhas += [f"  [{i['gravidade']}] {i['texto']}" for i in r["achados"]]
    return "\n".join(linhas)


def _posicoes(r):
    linhas = [f"Melhor posição: {r['melhor']}"]
    for p in r["posicoes"]:
        linhas.append(f"  {p['posicao']:<38} apoio {p['apoio_mm2']:>9} mm²  balanço {p['balanco_mm2']:>9} mm²  "
                      f"altura {p['altura_mm']:>6} mm{'  TOMBA' if p['tomba'] else ''}")
    return "\n".join(linhas)


def _argumentos():
    ap = argparse.ArgumentParser(prog="filuna_cad", description="Validadores de modelagem e impressão 3D do Filuna")
    sub = ap.add_subparsers(dest="comando", required=True)
    v = sub.add_parser("validar", help="confere se a peça imprime bem")
    v.add_argument("arquivo")
    v.add_argument("--mesa", type=_mesa, default=(256.0, 256.0, 256.0))
    v.add_argument("--amostras", type=int, default=4000)
    v.add_argument("--json", action="store_true")
    o = sub.add_parser("orientar", help="compara as seis posições na mesa")
    o.add_argument("arquivo")
    o.add_argument("--json", action="store_true")
    f = sub.add_parser("vistas", help="grava uma folha com perspectiva, frente, lado, cima e corte")
    f.add_argument("arquivo")
    f.add_argument("saida")
    c = sub.add_parser("comparar", help="mede se duas peças são a mesma forma")
    c.add_argument("a")
    c.add_argument("b")
    x = sub.add_parser("raio-x", help="compara a silhueta da peça com uma imagem de referência")
    x.add_argument("peca")
    x.add_argument("imagem")
    x.add_argument("--vista", choices=sorted(comparar.EIXOS), default="frente")
    x.add_argument("--saida")
    k = sub.add_parser("cupom", help="gera o teste de folga para a sua impressora")
    k.add_argument("pasta")
    k.add_argument("--diametro", type=float, default=8.0)
    _argumentos_engenharia(sub)
    return ap


def _forca(texto):
    partes = tuple(float(v) for v in texto.split(","))
    if len(partes) != 3:
        raise argparse.ArgumentTypeError("use FX,FY,FZ em newtons, por exemplo 0,0,-100")
    return partes


def _argumentos_engenharia(sub):
    c = sub.add_parser("conferir", help="conferência formal do arquivo: STEP, STL, 3MF, OBJ, GLB ou DXF")
    c.add_argument("arquivo")
    f = sub.add_parser("fabricar", help="análise de usinagem CNC, injeção plástica ou chapa metálica")
    f.add_argument("processo", choices=["cnc", "injecao", "chapa"])
    f.add_argument("arquivo")
    s = sub.add_parser("simular", help="simulação estrutural com o CalculiX: deformação e tensão")
    s.add_argument("arquivo")
    s.add_argument("--fixar", choices=sorted(simular.FACES), default="zmin")
    s.add_argument("--forca-em", choices=sorted(simular.FACES), default="zmax")
    s.add_argument("--forca", type=_forca, default=(0.0, 0.0, -100.0), help="FX,FY,FZ em newtons")
    s.add_argument("--material", choices=sorted(simular.MATERIAIS), default="pla")
    s.add_argument("--tamanho", type=float, default=0.0, help="tamanho dos elementos em mm (0: automático)")
    d = sub.add_parser("desenho", help="folha de desenho técnico cotada em PDF (A3, 1º diedro)")
    d.add_argument("arquivo")
    d.add_argument("saida")
    d.add_argument("--titulo")
    d.add_argument("--material", default="-")
    d.add_argument("--autor", default="-")
    p = sub.add_parser("pcb", help="KiCad: drc da placa, erc do esquema ou STEP 3D da placa")
    p.add_argument("operacao", choices=["drc", "erc", "step"])
    p.add_argument("arquivo")
    p.add_argument("saida", nargs="?")
    r = sub.add_parser("robo", help="confere URDF, SRDF (com --urdf) ou MJCF do MuJoCo")
    r.add_argument("arquivo")
    r.add_argument("--urdf")
    for comando in (c, f, s, d, p, r):
        comando.add_argument("--texto", action="store_true", help="resumo para ler, em vez do JSON completo")
    v = sub.add_parser("ver", help="visualizador ao vivo: refaz e confere a peça a cada salvamento")
    v.add_argument("fonte")
    v.add_argument("--porta", type=int, default=8765)
    v.add_argument("--sem-abrir", action="store_true")


def _pcb(a):
    if a.operacao == "step":
        if not a.saida:
            raise SystemExit("pcb step precisa do arquivo de saída: python -m filuna_cad pcb step placa.kicad_pcb placa.step")
        return pcb.exportar_step(a.arquivo, a.saida)
    return pcb.drc(a.arquivo) if a.operacao == "drc" else pcb.erc(a.arquivo)


COMANDOS_ENGENHARIA = {
    "conferir": lambda a: conferir.conferir(a.arquivo),
    "fabricar": lambda a: fabricar.PROCESSOS[a.processo](a.arquivo),
    "simular": lambda a: simular.simular(a.arquivo, simular.Caso(a.fixar, a.forca_em, a.forca, a.material, a.tamanho)),
    "desenho": lambda a: desenho.desenhar(a.arquivo, a.saida, desenho.Legenda(a.titulo or Path(a.arquivo).stem, a.material, a.autor)),
    "pcb": _pcb,
    "robo": lambda a: robo.conferir(a.arquivo, a.urdf),
    "ver": lambda a: ver.ver(a.fonte, a.porta, abrir=not a.sem_abrir),
}

COMANDOS = {**COMANDOS_ENGENHARIA,
    "validar": lambda a: validar.validar(a.arquivo, validar.Limites(mesa=a.mesa, amostras=a.amostras)),
    "orientar": lambda a: orientar.orientar(a.arquivo),
    "vistas": lambda a: vistas.folha(a.arquivo, a.saida),
    "comparar": lambda a: comparar.comparar_pecas(a.a, a.b),
    "raio-x": lambda a: comparar.raio_x(a.peca, a.imagem, a.vista, a.saida),
    "cupom": lambda a: cupom.gerar(a.pasta, a.diametro),
}
RESUMOS = {"validar": _resumo, "orientar": _posicoes}
FORA_DO_TEXTO = {"arquivo", "achados", "nota", "aprovada", "limites", "paredes"}


def _vazio(v):
    return v is None or (isinstance(v, (str, list, dict)) and not v)


def _valor(v):
    if isinstance(v, dict):
        return ", ".join(f"{k} {x}" for k, x in v.items())
    if isinstance(v, list):
        return " x ".join(str(x) for x in v) if all(isinstance(x, (int, float)) for x in v) else ", ".join(map(str, v))
    return str(v)


def _texto(r):
    """Resumo para gente ler: situação, números e cada achado. O JSON completo sai sem --texto."""
    linhas = []
    if "nota" in r:
        linhas.append(f"{'APROVADA' if r['aprovada'] else 'REPROVADA'}  nota {r['nota']}/100  {r.get('arquivo', '')}")
    linhas += [f"  {k.replace('_', ' ')}: {_valor(v)}" for k, v in r.items() if k not in FORA_DO_TEXTO and not _vazio(v)]
    p = r.get("paredes")
    if isinstance(p, dict) and p.get("medida"):
        linhas.append(f"  parede: mínima {p['minima_mm']} mm, típica {p['mediana_mm']} mm")
    linhas += [f"  [{a['gravidade']}] {a['texto']}" for a in r.get("achados", [])]
    if r.get("limites"):
        linhas.append(f"  limites: {r['limites']}")
    return "\n".join(linhas)


def main(argv=None):
    args = _argumentos().parse_args(argv)
    r = COMANDOS[args.comando](args)
    resumir = _texto if getattr(args, "texto", False) else None if getattr(args, "json", False) else RESUMOS.get(args.comando)
    sys.stdout.write((resumir(r) if resumir else json.dumps(r, ensure_ascii=False, indent=1)) + "\n")
    return 0 if r.get("aprovada", True) else 1


if __name__ == "__main__":
    sys.exit(main())
