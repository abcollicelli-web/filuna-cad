# build123d (CAD exato)

Use quando a peça precisa de arredondamento ou chanfro em muitas arestas, de casca com espessura constante, ou
de um arquivo STEP para outra pessoa editar. O núcleo é o mesmo do FreeCAD e do CadQuery (OpenCascade).

```bash
pip install build123d
```

```python
import build123d as bd

corpo = bd.Box(60, 40, 20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
corpo -= bd.Pos(0, 0, 2) * bd.Box(55.2, 35.2, 20, align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN))
corpo = bd.fillet(corpo.edges().filter_by(bd.Axis.Z), 3)
bd.export_step(corpo, "caixa.step")
bd.export_stl(corpo, "caixa.stl", tolerance=0.02)
```

## Pense em faces e arestas, não em somar blocos

O erro mais comum de quem vem do OpenSCAD é fazer tudo por soma e corte. Aqui a peça tem faces e arestas com
nome: fure a partir de uma face, faça casca, arredonde uma aresta escolhida. Fica mais curto e quebra menos.

## Armadilhas

- **Escolha as arestas de novo depois de cada operação.** Uma lista de arestas guardada antes de um corte aponta
  para arestas que não existem mais: o arredondamento pula essas arestas ou devolve a peça de antes, sem avisar.
- **Um corte que tira tudo devolve um sólido vazio sem erro.** Confira `corpo.solids()` e o volume.
- **Faces coincidentes ou quase tangentes** podem dar um resultado errado que o próprio motor considera válido.
  Depois de cada união ou corte, compare a caixa e o volume com o esperado. Enterre uma saliência 1 a 2 mm no
  corpo para ela fundir de verdade.
- **`.located()` troca a posição inteira** (e apaga o giro anterior); `Pos(...) * peca` e `.moved()` somam.
- **`align=None`** usa a origem crua da forma: cilindro com a base em Z = 0, caixa pelo canto.
- **O sentido do polígono decide para que lado ele extruda.** Dê a direção se importar.
- **União perde cor e nome;** corte e interseção mantêm os do primeiro.
- **Volume de sólido com curva livre** erra perto de 0,4%: aceite 1% nas conferências.

## Arredondamento e chanfro que falham

Mensagem típica: `StdFail_NotDone` ou `BRep_API: command not done`. As causas, na ordem:

1. Raio maior que a menor aresta vizinha.
2. Dois arredondamentos que se encostam.
3. Casca mais grossa que o raio da curva onde ela passa.

O que fazer: reduza o raio; arredonde os grupos de arestas em separado, as curtas primeiro; arredonde por
último, depois de todos os cortes. Se uma cadeia de arestas tangentes derruba o motor, arredonde o perfil 2D
antes de extrudar.

Raio só de aparência pode se ajustar sozinho (`min(R, parede * 0.8)`). Medida que tem função nunca muda calada:
se não coube, diga o valor que ficou.

## Ordem de construção

Sólido base, depois o que soma e o que corta, depois os furos, e arredondamentos e chanfros por último.

## Montagens

- Cada parte nasce na própria origem e depois é posicionada.
- As posições de uma parte saem das medidas da outra: uma única lista de furos serve para as duas partes que
  se parafusam.
- Interferência é o volume da interseção (tem que ser perto de zero); folga é a distância entre as formas.
  Distância zero pode ser encostado ou atravessado: meça os dois.
- Peça que se mexe: confira nas duas pontas do curso e no meio, com pelo menos 1 mm de folga.

## Exportar

- STEP é o arquivo mestre; a malha de impressão sai dele.
- Malha para encaixe justo: tolerância fina (0,02 mm). Para peça decorativa, 0,1 mm basta e o arquivo fica leve.
- Um STEP que passa de 50 MB tem alguma superfície doente: procure a curva livre que explodiu.

## CadQuery

Mesmo núcleo, outra escrita. Vale o mesmo raciocínio, com três cuidados próprios: o ponto de origem de
`.workplane()` não é o centro da face (peça `centerOption="CenterOfBoundBox"`); o seletor `>Z` pega a face de
centro mais alto, não o ponto mais alto; e `.val()` devolve só o primeiro item, calado. Faça furos de uma vez
(`pushPoints(...).hole()`), não num laço.
