"""Linha de comando: python -m filuna_cad validar|orientar|vistas|comparar|raio-x|cupom ..."""
import argparse
import json
import sys

from . import comparar, cupom, orientar, validar, vistas


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
    return ap


COMANDOS = {
    "validar": lambda a: validar.validar(a.arquivo, validar.Limites(mesa=a.mesa, amostras=a.amostras)),
    "orientar": lambda a: orientar.orientar(a.arquivo),
    "vistas": lambda a: vistas.folha(a.arquivo, a.saida),
    "comparar": lambda a: comparar.comparar_pecas(a.a, a.b),
    "raio-x": lambda a: comparar.raio_x(a.peca, a.imagem, a.vista, a.saida),
    "cupom": lambda a: cupom.gerar(a.pasta, a.diametro),
}
RESUMOS = {"validar": _resumo, "orientar": _posicoes}


def main(argv=None):
    args = _argumentos().parse_args(argv)
    r = COMANDOS[args.comando](args)
    resumir = None if getattr(args, "json", False) else RESUMOS.get(args.comando)
    sys.stdout.write((resumir(r) if resumir else json.dumps(r, ensure_ascii=False, indent=1)) + "\n")
    return 0 if r.get("aprovada", True) else 1


if __name__ == "__main__":
    sys.exit(main())
