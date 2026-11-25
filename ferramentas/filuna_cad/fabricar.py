"""Análise de fabricação além da impressão: usinagem CNC de 3 eixos, injeção plástica e chapa metálica.

Tudo é medido na malha (STL, 3MF, OBJ, GLB ou STEP), por amostras da superfície e raios. Mostra o que o processo
não alcança e onde o desenho precisa mudar. Não faz orçamento, não escolhe ferramenta e não gera caminho de corte.
"""
import numpy as np
import trimesh

from .validar import LOTE_RAIOS, Limites, carregar, medir_paredes, nota

EIXOS = {"+Z": (0, 0, 1), "-Z": (0, 0, -1), "+X": (1, 0, 0), "-X": (-1, 0, 0), "+Y": (0, 1, 0), "-Y": (0, -1, 0)}
LATERAL = 0.05             # faces quase paralelas ao eixo: a lateral da fresa alcança
SOBRA_BLOCO = 2.0          # mm de sobra em cada lado do bloco bruto
CANTO_VIVO = np.radians(45)
SEM_SAIDA = np.sin(np.radians(0.5))
SAIDA_BOA = np.sin(np.radians(1.0))
PAREDE_INJECAO = (0.8, 4.0)
DENSIDADES = {"aço": 7.85, "alumínio": 2.70, "inox": 8.00}


def _amostras(m, quantas, semente=7):
    pontos, faces = trimesh.sample.sample_surface_even(m, quantas, seed=semente)
    return pontos, m.face_normals[faces], m.area / max(len(pontos), 1)


def _livre(m, pontos, normais, sentido):
    """Para cada ponto, o raio que sai dele no sentido dado escapa da peça sem bater?"""
    d = np.tile(np.asarray(sentido, float), (len(pontos), 1))
    # Sai um pouco para fora da face: numa parede paralela ao raio ele correria rente e bateria nela mesma.
    inicio = pontos + normais * 1e-2 + d * 1e-3
    bate = [m.ray.intersects_any(inicio[i:i + LOTE_RAIOS], d[i:i + LOTE_RAIOS]) for i in range(0, len(pontos), LOTE_RAIOS)]
    return ~np.concatenate(bate) if bate else np.zeros(0, bool)


def _alcance(m, pontos, normais, sentido):
    """Pontos que uma ferramenta vindo de `sentido` toca: face virada para ela (ou de lado) e caminho livre."""
    voltada = normais @ np.asarray(sentido, float) > -LATERAL
    ok = np.zeros(len(pontos), bool)
    ok[voltada] = _livre(m, pontos[voltada], normais[voltada], sentido)
    return ok


def _cobrir(alcances):
    """Menor conjunto de fixações que alcança tudo o que é alcançável (escolha gulosa)."""
    falta = np.logical_or.reduce(list(alcances.values()))
    escolhidas = []
    while falta.any():
        melhor = max(alcances, key=lambda k: int((alcances[k] & falta).sum()))
        if not (alcances[melhor] & falta).any():
            break
        escolhidas.append(melhor)
        falta &= ~alcances[melhor]
    return escolhidas


def _cantos_vivos(m, eixo):
    """Arestas côncavas e vivas ao longo do eixo: fresa redonda não faz canto interno reto."""
    concavas = ~m.face_adjacency_convex & (m.face_adjacency_angles > CANTO_VIVO)
    arestas = m.vertices[m.face_adjacency_edges[concavas]]
    vetor = arestas[:, 1] - arestas[:, 0]
    comprimento = np.linalg.norm(vetor, axis=1)
    ao_longo = np.abs(vetor @ np.asarray(eixo, float)) > 0.95 * np.maximum(comprimento, 1e-9)
    return float(comprimento[ao_longo].sum())


def usinagem(caminho, amostras=6000):
    m = carregar(caminho)
    pontos, normais, area_ponto = _amostras(m, amostras)
    alcances = {k: _alcance(m, pontos, normais, d) for k, d in EIXOS.items()}
    fixacoes = _cobrir(alcances)
    sem_alcance = ~np.logical_or.reduce(list(alcances.values()))
    bloco = m.extents + 2 * SOBRA_BLOCO
    cantos = {k: round(_cantos_vivos(m, EIXOS[k]), 1) for k in fixacoes}
    r = {"processo": "usinagem CNC 3 eixos", "medidas_mm": [round(float(v), 2) for v in m.extents],
         "bloco_bruto_mm": [round(float(v), 1) for v in bloco],
         "material_removido": round(1 - abs(m.volume) / float(np.prod(bloco)), 3),
         "fixacoes": fixacoes, "alcance_por_lado": {k: round(float(v.mean()), 3) for k, v in alcances.items()},
         "area_sem_alcance_mm2": round(float(sem_alcance.sum() * area_ponto), 1),
         "cantos_internos_vivos_mm": cantos}
    a = []
    if r["area_sem_alcance_mm2"] > 1:
        a.append(("erro", "alcance", f"{r['area_sem_alcance_mm2']} mm² não são alcançados de nenhum dos 6 lados: "
                                     "rebaixo escondido. Abra o rebaixo para um lado ou use 5 eixos."))
    if len(fixacoes) > 2:
        a.append(("aviso", "fixacoes", f"{len(fixacoes)} fixações ({', '.join(fixacoes)}): cada uma custa tempo e precisão."))
    for k, mm in cantos.items():
        if mm > 0.5:
            a.append(("aviso", "canto", f"{mm} mm de canto interno vivo na fixação {k}: arredonde com raio maior que o da fresa."))
    if r["material_removido"] > 0.8:
        a.append(("aviso", "bloco", f"{round(r['material_removido'] * 100)}% do bloco vira cavaco: veja se outro processo sai mais barato."))
    return _fechar(r, a, caminho)


def _eixo_de_extracao(m, pontos, normais):
    """Eixo do molde com menos área presa (rebaixo) quando as duas metades se separam."""
    melhor = None
    for nome, d in (("Z", (0, 0, 1)), ("X", (1, 0, 0)), ("Y", (0, 1, 0))):
        d = np.asarray(d, float)
        sai = _alcance(m, pontos, normais, d) | _alcance(m, pontos, normais, -d)
        presa = float((~sai).mean())
        if melhor is None or presa < melhor[1]:
            melhor = (nome, presa, d)
    return melhor


def injecao(caminho, amostras=6000):
    m = carregar(caminho)
    pontos, normais, area_ponto = _amostras(m, amostras)
    eixo, presa, d = _eixo_de_extracao(m, pontos, normais)
    inclinacao = np.abs(normais @ d)
    paredes = medir_paredes(m, Limites(amostras=amostras))
    r = {"processo": "injeção plástica", "eixo_de_extracao": eixo, "area_presa_mm2": round(presa * len(pontos) * area_ponto, 1),
         "area_sem_saida_mm2": round(float((inclinacao < SEM_SAIDA).sum() * area_ponto), 1),
         "area_saida_menor_1grau_mm2": round(float(((inclinacao >= SEM_SAIDA) & (inclinacao < SAIDA_BOA)).sum() * area_ponto), 1),
         "paredes": paredes}
    a = []
    if r["area_presa_mm2"] > 1:
        a.append(("erro", "rebaixo", f"{r['area_presa_mm2']} mm² ficam presos no molde no eixo {eixo}: precisa de gaveta ou mudar o desenho."))
    if r["area_sem_saida_mm2"] > 1:
        a.append(("aviso", "saida", f"{r['area_sem_saida_mm2']} mm² de parede reta no sentido do molde: dê pelo menos 1 grau de saída."))
    if paredes.get("medida"):
        fina, grossa = PAREDE_INJECAO
        if paredes["minima_mm"] < fina:
            a.append(("erro", "parede", f"Parede de {paredes['minima_mm']} mm: o plástico não preenche bem abaixo de {fina} mm."))
        if paredes["p05_mm"] and paredes["mediana_mm"] / paredes["p05_mm"] > 2:
            a.append(("aviso", "parede", "Espessura muito desigual: a parte grossa encolhe mais e afunda ou empena."))
        if paredes["mediana_mm"] > grossa:
            a.append(("aviso", "parede", f"Parede típica de {paredes['mediana_mm']} mm: acima de {grossa} mm afunda; esvazie com nervuras."))
    return _fechar(r, a, caminho)


def chapa(caminho, amostras=4000):
    m = carregar(caminho)
    p = medir_paredes(m, Limites(amostras=amostras))
    r = {"processo": "chapa metálica", "paredes": p}
    a = []
    if not p.get("medida"):
        a.append(("erro", "espessura", "Não deu para medir a espessura: a malha precisa ser fechada."))
        return _fechar(r, a, caminho)
    espessura = p["mediana_mm"]
    uniforme = p["p05_mm"] >= 0.85 * espessura
    area_chapa = abs(m.volume) / espessura   # chapa de espessura única: volume = área planificada x espessura
    r.update(espessura_mm=espessura, espessura_uniforme=bool(uniforme), area_planificada_cm2=round(area_chapa / 100, 1),
             peso_g={k: round(abs(m.volume) / 1000 * v, 1) for k, v in DENSIDADES.items()})
    if not uniforme:
        a.append(("erro", "espessura", f"A espessura varia (5% abaixo de {p['p05_mm']} mm, típica {espessura} mm): "
                                       "chapa tem espessura única; separe em peças ou use outro processo."))
    if espessura < 0.5 or espessura > 6:
        a.append(("aviso", "espessura", f"Chapa de {espessura} mm é rara para dobra: o comum é de 0,5 a 6 mm."))
    return _fechar(r, a, caminho)


def _fechar(r, a, caminho):
    r["arquivo"] = str(caminho)
    r["achados"] = [{"gravidade": g, "tema": t, "texto": x} for g, t, x in a]
    r["nota"] = nota(r["achados"])
    r["aprovada"] = not any(i["gravidade"] == "erro" for i in r["achados"])
    r["limites"] = "Medido na malha por amostras. Não faz orçamento, não escolhe ferramenta, não gera caminho de corte."
    return r


PROCESSOS = {"cnc": usinagem, "injecao": injecao, "chapa": chapa}
