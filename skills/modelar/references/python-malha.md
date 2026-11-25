# Python de malha: shapely, Manifold e trimesh

É o jeito dos geradores do Filuna: o perfil nasce em 2D, onde toda conta é exata, e só então vira sólido.
Serve para letras, números, silhuetas, placas, peças por cor e para mexer em STL que já existe.

```bash
pip install shapely manifold3d trimesh mapbox-earcut rtree scipy lxml networkx pillow
```

## O caminho

```python
import manifold3d as m3d
import numpy as np
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

# 1. Perfil em 2D: soma e corte de polígonos, com conta exata
perfil = unary_union([box(0, 0, 60, 8), box(20, 0, 30, 50)]).difference(box(40, 2, 51, 30))

# 2. Sólido: extrusão pelo Manifold, que só devolve malha fechada
contornos = [np.asarray(perfil.exterior.coords)[:-1]] + [np.asarray(f.coords)[:-1] for f in perfil.interiors]
solido = m3d.Manifold.extrude(m3d.CrossSection(contornos, m3d.FillRule.EvenOdd), 40)
assert solido.status() == m3d.Error.NoError

# 3. Malha para exportar
m = solido.to_mesh()
malha = trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts))
malha.export("peca.stl")
```

## Para que serve cada biblioteca

| Biblioteca | Use para |
|---|---|
| **shapely** | Perfil 2D: unir, cortar, engordar ou afinar (`buffer`), arredondar canto, medir área e distância |
| **manifold3d** | Extrudar, girar, unir, cortar e furar em 3D sem abrir a malha; medir volume |
| **trimesh** | Ler e gravar STL, 3MF e OBJ; medir; separar cascas; cortar seções; lançar raios |
| **mapbox-earcut** | Transformar polígono com furos em triângulos |
| **numpy, scipy, scikit-image, opencv, pillow** | Imagem para contorno: tirar fundo, separar cor, achar borda |
| **fonttools, svgpathtools** | Letras de uma fonte e caminhos de SVG como polígonos |

## Regras

- **Faça o máximo em 2D.** Arredondar canto de perfil é `perfil.buffer(-r).buffer(r)` (cantos para fora) ou o
  inverso (cantos para dentro). Em 3D, malha não tem aresta para arredondar.
- **`buffer(0)` conserta polígono inválido**, mas confira a área antes e depois: se mudou muito, o desenho
  estava errado.
- **Perfil com mais de uma parte** (`MultiPolygon`) vira mais de um sólido: decida se é isso que você quer.
- **Sentido dos triângulos:** quando montar malha na mão, confira `malha.is_winding_consistent` e
  `malha.volume > 0`. Volume negativo é malha do avesso.
- **Operação em 3D sempre pelo Manifold**, não pelas operações de malha comuns: ele recusa entrada aberta em vez
  de devolver lixo.
- **Depois de cada operação, confira** `is_watertight`, `volume` e `extents`. Um corte que não tirou nada ou uma
  união que deixou duas cascas não avisa.

## Mudar um STL que já existe

```python
peca = trimesh.load("original.stl", force="mesh")
base = m3d.Manifold(m3d.Mesh(np.asarray(peca.vertices, np.float32), np.asarray(peca.faces, np.uint32)))
furo = m3d.Manifold.cylinder(20, 2.2, 2.2, 64).translate([10, 10, -1])
novo = base - furo
```

- Se a malha original for aberta, o Manifold recusa. Conserte primeiro (`trimesh.repair.fill_holes`,
  `fix_normals`) e, se não fechar, avise: remendar por cima esconde o defeito.
- Não redesenhe a peça: importe, e some ou corte só o que muda.
- Se existir o arquivo de CAD (STEP), mude nele, não na malha.

## Várias cores num 3MF

Uma malha por cor, cada uma como objeto próprio do 3MF. As peças de cores diferentes se encostam sem se
atravessar: gere uma cortando a outra (`a - b`) para a fronteira ser exatamente a mesma.

## Mesma coisa em JavaScript

`manifold-3d` (o mesmo Manifold, em WebAssembly), `three` e `earcut` fazem esse caminho no navegador e no Node.
`@napi-rs/canvas` dá o Canvas 2D fora do navegador. É o conjunto que os paramétricos do Filuna usam.
