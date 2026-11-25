"""Conferência de descrições de robô: URDF (elos e juntas), SRDF (grupos do MoveIt) e MJCF (MuJoCo).

URDF: árvore com uma raiz só, nomes únicos, juntas ligando elos que existem, eixo e limites, massa e inércia
fisicamente possíveis, malhas que existem. SRDF: tudo o que cita existe no URDF. MJCF: o próprio MuJoCo compila
e roda alguns passos de simulação sem explodir.
"""
from pathlib import Path

import numpy as np
from lxml import etree

from .validar import nota

TIPOS_DE_JUNTA = {"revolute", "continuous", "prismatic", "fixed", "floating", "planar"}


def _numeros(texto, n=3):
    valores = [float(v) for v in (texto or "").split()]
    return valores if len(valores) == n else None


def _inercia(elo, a):
    nome = elo.get("name")
    inercial = elo.find("inertial")
    if inercial is None:
        return
    massa = inercial.find("mass")
    if massa is None or float(massa.get("value", 0)) <= 0:
        a.append(("erro", "massa", f"Elo {nome}: massa ausente ou não positiva."))
    i = inercial.find("inertia")
    if i is None:
        a.append(("erro", "inercia", f"Elo {nome}: tem massa mas não tem inércia."))
        return
    v = {k: float(i.get(k, 0)) for k in ("ixx", "iyy", "izz", "ixy", "ixz", "iyz")}
    matriz = np.array([[v["ixx"], v["ixy"], v["ixz"]], [v["ixy"], v["iyy"], v["iyz"]], [v["ixz"], v["iyz"], v["izz"]]])
    principais = np.linalg.eigvalsh(matriz)
    if principais.min() <= 0:
        a.append(("erro", "inercia", f"Elo {nome}: inércia não é positiva definida; a simulação explode."))
    elif principais.max() > principais.sum() - principais.max() + 1e-12:
        a.append(("erro", "inercia", f"Elo {nome}: inércia impossível (um momento maior que a soma dos outros dois)."))


def _malhas(raiz, pasta, a):
    for m in raiz.iter("mesh"):
        nome = m.get("filename", "")
        if nome.startswith("package://"):
            continue
        caminho = Path(nome.removeprefix("file://"))
        if not (caminho if caminho.is_absolute() else pasta / caminho).exists():
            a.append(("erro", "malha", f"Malha {nome} não existe."))


def _juntas(juntas, elos, a):
    filhos = {}
    for j in juntas:
        nome, tipo = j.get("name"), j.get("type")
        pai, filho = j.find("parent"), j.find("child")
        if tipo not in TIPOS_DE_JUNTA:
            a.append(("erro", "junta", f"Junta {nome}: tipo {tipo!r} não existe."))
        if pai is None or filho is None or pai.get("link") not in elos or filho.get("link") not in elos:
            a.append(("erro", "junta", f"Junta {nome}: liga elo que não existe."))
            continue
        filhos.setdefault(filho.get("link"), []).append(nome)
        eixo = _numeros(j.find("axis").get("xyz")) if j.find("axis") is not None else [1, 0, 0]
        if tipo in {"revolute", "continuous", "prismatic"} and (eixo is None or np.linalg.norm(eixo) < 1e-9):
            a.append(("erro", "eixo", f"Junta {nome}: eixo nulo ou mal escrito."))
        limite = j.find("limit")
        if tipo in {"revolute", "prismatic"}:
            if limite is None:
                a.append(("erro", "limite", f"Junta {nome}: {tipo} precisa de limite."))
            elif float(limite.get("lower", 0)) > float(limite.get("upper", 0)):
                a.append(("erro", "limite", f"Junta {nome}: limite inferior maior que o superior."))
    return filhos


def conferir_urdf(caminho):
    raiz = etree.parse(str(caminho)).getroot()
    elos = [e.get("name") for e in raiz.findall("link")]
    juntas = raiz.findall("joint")
    a = []
    for repetido in {n for n in elos if elos.count(n) > 1}:
        a.append(("erro", "nome", f"Elo {repetido} aparece mais de uma vez."))
    filhos = _juntas(juntas, set(elos), a)
    for elo, js in filhos.items():
        if len(js) > 1:
            a.append(("erro", "arvore", f"Elo {elo} é filho de {len(js)} juntas: URDF é árvore, um pai por elo."))
    raizes = [e for e in elos if e not in filhos]
    if len(raizes) != 1:
        a.append(("erro", "arvore", f"A árvore precisa de uma raiz só e tem {len(raizes)}: {', '.join(raizes[:5])}."))
    for e in raiz.findall("link"):
        _inercia(e, a)
    _malhas(raiz, Path(caminho).parent, a)
    moveis = sum(1 for j in juntas if j.get("type") not in {"fixed", None})
    return {"formato": "URDF", "robo": raiz.get("name"), "elos": len(elos), "juntas": len(juntas),
            "juntas_moveis": moveis, "raiz": raizes[0] if len(raizes) == 1 else None}, a


def conferir_srdf(caminho, urdf):
    if not urdf:
        raise ValueError("Para conferir um SRDF passe também o URDF do robô (--urdf).")
    robo = etree.parse(str(urdf)).getroot()
    elos = {e.get("name") for e in robo.findall("link")}
    juntas = {j.get("name") for j in robo.findall("joint")}
    raiz = etree.parse(str(caminho)).getroot()
    grupos = {g.get("name") for g in raiz.findall("group")}
    a = []
    for g in raiz.findall("group"):
        for e in g.findall("link"):
            if e.get("name") not in elos:
                a.append(("erro", "grupo", f"Grupo {g.get('name')}: elo {e.get('name')} não existe no URDF."))
        for j in g.findall("joint"):
            if j.get("name") not in juntas:
                a.append(("erro", "grupo", f"Grupo {g.get('name')}: junta {j.get('name')} não existe no URDF."))
        for c in g.findall("chain"):
            if c.get("base_link") not in elos or c.get("tip_link") not in elos:
                a.append(("erro", "grupo", f"Grupo {g.get('name')}: corrente com ponta que não existe."))
        for s in g.findall("group"):
            if s.get("name") not in grupos:
                a.append(("erro", "grupo", f"Grupo {g.get('name')}: subgrupo {s.get('name')} não existe."))
    for d in raiz.findall("disable_collisions"):
        if d.get("link1") not in elos or d.get("link2") not in elos:
            a.append(("aviso", "colisao", f"Par sem colisão {d.get('link1')}/{d.get('link2')} cita elo que não existe."))
    for p in raiz.findall("group_state"):
        if p.get("group") not in grupos:
            a.append(("erro", "pose", f"Pose {p.get('name')} é de um grupo que não existe."))
    return {"formato": "SRDF", "grupos": len(grupos), "poses": len(raiz.findall("group_state")),
            "pares_sem_colisao": len(raiz.findall("disable_collisions"))}, a


def conferir_mjcf(caminho, passos=500):
    import mujoco

    a = []
    try:
        modelo = mujoco.MjModel.from_xml_path(str(caminho))
    except ValueError as e:
        return {"formato": "MJCF", "compila": False}, [("erro", "mujoco", f"O MuJoCo não compila: {e}")]
    dados = mujoco.MjData(modelo)
    for _ in range(passos):
        mujoco.mj_step(modelo, dados)
    estavel = bool(np.isfinite(dados.qpos).all() and np.isfinite(dados.qvel).all())
    avisos = [mujoco.mjtWarning(i).name for i, w in enumerate(dados.warning) if w.number]
    if not estavel:
        a.append(("erro", "simulacao", "A simulação explodiu (NaN): confira massas, inércias e passo de tempo."))
    for w in avisos:
        a.append(("aviso", "simulacao", f"O MuJoCo avisou {w} durante {passos} passos."))
    return {"formato": "MJCF", "compila": True, "corpos": int(modelo.nbody), "juntas": int(modelo.njnt),
            "atuadores": int(modelo.nu), "massa_total_kg": round(float(modelo.body_mass.sum()), 3),
            "passos_simulados": passos, "estavel": estavel}, a


def conferir(caminho, urdf=None):
    ext = Path(caminho).suffix.lower()
    if ext == ".urdf":
        r, a = conferir_urdf(caminho)
    elif ext == ".srdf":
        r, a = conferir_srdf(caminho, urdf)
    elif ext in {".xml", ".mjcf"}:
        r, a = conferir_mjcf(caminho)
    else:
        raise ValueError("Aceitos: .urdf, .srdf (com --urdf), .xml ou .mjcf do MuJoCo.")
    r["arquivo"] = str(caminho)
    r["achados"] = [{"gravidade": g, "tema": t, "texto": x} for g, t, x in a]
    r["nota"] = nota(r["achados"])
    r["aprovada"] = not any(i["gravidade"] == "erro" for i in r["achados"])
    return r
