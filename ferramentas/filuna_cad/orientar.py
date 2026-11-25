"""Compara as seis posições da peça na mesa (cada face para baixo) e ordena da melhor para a pior de imprimir."""
import numpy as np
import trimesh

from .validar import carregar, medir_balancos, medir_estabilidade, medir_mesa

# Nome da posição e o giro que põe aquela face para baixo.
POSICOES = {
    "como está (Z- na mesa)": (0, [1, 0, 0]),
    "de cabeça para baixo (Z+ na mesa)": (180, [1, 0, 0]),
    "frente na mesa (Y- na mesa)": (-90, [1, 0, 0]),
    "fundo na mesa (Y+ na mesa)": (90, [1, 0, 0]),
    "lado esquerdo na mesa (X- na mesa)": (90, [0, 1, 0]),
    "lado direito na mesa (X+ na mesa)": (-90, [0, 1, 0]),
}


def _medir(m):
    mesa, embaixo = medir_mesa(m)
    balanco = medir_balancos(m, embaixo)["area_mm2"]
    firme = medir_estabilidade(m, embaixo)
    return {
        "apoio_mm2": mesa["apoio_mm2"],
        "balanco_mm2": balanco,
        "altura_mm": round(float(m.extents[2]), 1),
        "tomba": bool(firme.get("medida") and firme["margem_mm"] < 0),
    }


def _pontos(r, area_total):
    """Menos é melhor: balanço pesa mais, depois falta de apoio, depois altura. Posição que tomba vai para o fim."""
    falta_apoio = 1 - min(1.0, r["apoio_mm2"] / (0.15 * area_total)) if area_total else 1
    return (r["balanco_mm2"] / area_total * 100 if area_total else 0) + 20 * falta_apoio + r["altura_mm"] / 50 + (1000 if r["tomba"] else 0)


def orientar(caminho):
    """Lista as seis posições, da melhor para a pior, com o giro que leva a peça a cada uma."""
    base = carregar(caminho)
    lista = []
    for nome, (graus, eixo) in POSICOES.items():
        m = base.copy()
        m.apply_transform(trimesh.transformations.rotation_matrix(np.radians(graus), eixo))
        r = _medir(m)
        r.update(posicao=nome, giro={"graus": graus, "eixo": "XYZ"[int(np.argmax(np.abs(eixo)))]})
        r["pontos"] = round(_pontos(r, float(base.area)), 2)
        lista.append(r)
    lista.sort(key=lambda r: r["pontos"])
    return {"arquivo": str(caminho), "melhor": lista[0]["posicao"], "posicoes": lista}
