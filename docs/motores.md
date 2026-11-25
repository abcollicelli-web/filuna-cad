# Instalar os motores

As habilidades funcionam com qualquer um dos motores abaixo. Instale os que for usar; o validador precisa só da
parte de Python de malha.

| Motor | Instalar | Conferir |
|---|---|---|
| Raios rápidos (recomendado para malhas grandes) | `pip install embreex` | `python -c "from trimesh import ray; print(ray.has_embree)"` |
| Python de malha | `pip install shapely manifold3d trimesh mapbox-earcut rtree scipy lxml networkx pillow` | `python -c "import manifold3d, trimesh, shapely"` |
| Imagem para contorno | `pip install numpy scikit-image opencv-python-headless fonttools svgpathtools` | |
| build123d | `pip install build123d` | `python -c "import build123d"` |
| OpenSCAD | Versão de desenvolvimento em [openscad.org/downloads](https://openscad.org/downloads.html) | `openscad --version` (2025 ou mais novo) |
| Biblioteca BOSL2 do OpenSCAD | `git clone https://github.com/BelfrySCAD/BOSL2` na pasta de bibliotecas, ou aponte `OPENSCADPATH` para ela | `include <BOSL2/std.scad>` num arquivo de teste |
| FreeCAD | [freecad.org/downloads](https://www.freecad.org/downloads.php) | `freecadcmd --version` |
| JavaScript | `npm install three manifold-3d earcut @napi-rs/canvas opentype.js fflate` | |
| Blender | [blender.org/download](https://www.blender.org/download/) | `blender --version` |
| OrcaSlicer | [github.com/OrcaSlicer/OrcaSlicer/releases](https://github.com/OrcaSlicer/OrcaSlicer/releases) | |
| Engenharia (Python) | `pip install "filuna-cad[engenharia]"` a partir deste repositório: gmsh, ezdxf, matplotlib, mujoco, sexpdata, build123d | `python -c "import gmsh, ezdxf, mujoco"` |
| CalculiX | `apt install calculix-ccx` (Linux) ou o pacote do [calculix.de](http://www.calculix.de) | `ccx -v` |
| KiCad 8 ou mais novo | `apt install kicad` ou [kicad.org/download](https://www.kicad.org/download/) | `kicad-cli version` |

Observações:

- O OpenSCAD estável de 2021 não tem o motor Manifold: use a versão de desenvolvimento.
- Em servidor sem tela, rode o OpenSCAD com `QT_QPA_PLATFORM=offscreen`.
- O CadQuery pode não instalar nas versões mais novas do Python; o build123d usa o mesmo núcleo e instala.

## Teste que prova que os motores funcionam

Cada motor gera a mesma peça, uma caixa de 30 × 20 × 10 mm com um furo de 10 mm, e o volume tem que dar
5.215 mm³ (30 × 20 × 10 menos π × 5² × 10). Na instalação que usamos para escrever este repositório, os motores
deram de 5.214,6 a 5.214,9 mm³.

```python
import manifold3d as m
peca = m.Manifold.cube([30, 20, 10]) - m.Manifold.cylinder(12, 5, 5, 128).translate([15, 10, -1])
print(round(peca.volume(), 1))
```

```scad
difference() { cube([30, 20, 10]); translate([15, 10, -1]) cylinder(r = 5, h = 12, $fn = 128); }
```

```python
import build123d as bd
print(round((bd.Box(30, 20, 10) - bd.Cylinder(5, 10)).volume, 1))
```

Se dois motores dão o mesmo volume para a mesma peça, o erro que você está caçando não é do motor.
