# OpenSCAD

Use uma versão de 2025 em diante (as de desenvolvimento servem): o motor Manifold é muito mais rápido e é o que
os comandos abaixo pedem. A versão 2021 não tem.

## Rodar

```bash
openscad --backend=manifold -o peca.stl peca.scad          # malha
openscad --backend=manifold -o peca.3mf peca.scad          # 3MF (guarda unidade)
openscad --backend=manifold --render --imgsize=1200,900 --projection=ortho \
         --autocenter --viewall -o vista.png peca.scad      # imagem
```

- Em servidor sem tela: `QT_QPA_PLATFORM=offscreen` na frente do comando.
- Câmera: `--camera=tx,ty,tz,rx,ry,rz,dist`. Perspectiva `0,0,0,55,0,25,0`; cima `0,0,0,0,0,0,0`; frente
  `0,0,0,90,0,0,0`; lado `0,0,0,90,0,90,0`.
- Use sempre `--render`: a pré-visualização rápida mostra faces piscando onde há corte rente.
- `--viewall` esconde o tamanho real. Para comparar tamanhos, fixe a distância da câmera.
- **O código de saída não é confiável.** Um `assert` que falha ou um módulo que não existe podem sair com zero.
  Leia a saída procurando `ERROR:` e `WARNING:` e confirme que o arquivo existe e tem conteúdo.
- Corte para ver por dentro: `projection(cut=true) translate([0,0,-z]) peca();`
- Parâmetro pela linha de comando: `-D 'largura=80'`.

## Armadilhas da linguagem

- **Sem unidade:** trate tudo como milímetro e escreva isso no topo do arquivo.
- **Variável não muda.** A última atribuição no bloco vale para o bloco inteiro, e atribuir dentro de `if` ou
  `for` não sai de lá. Use `x = condicao ? a : b` e funções.
- **`difference()`:** o primeiro filho é o corpo, os outros cortam. Corpo errado na frente dá peça vazia.
- **Corte rente não corta.** Quem corta precisa passar: altura `h + 0.2` começando em `-0.1`. Quem se junta
  precisa entrar no outro: sólidos que só se encostam geram malha aberta.
- **Círculo é polígono por dentro:** furo sai menor que o pedido. Suba `$fn` no furo ou multiplique o raio por
  `1/cos(180/$fn)`.
- **`$fn` alto no arquivo inteiro deixa tudo lento.** Use 64 enquanto ajusta e 128 na exportação, e baixo nos
  furos pequenos.
- **2D e 3D não se misturam** numa mesma operação: extrude antes.
- **`hull()` e `minkowski()` são lentos.** Caixa arredondada sai mais rápido com `offset()` no perfil 2D antes de
  extrudar, ou com `cuboid(rounding=)` da BOSL2.
- **`cube()` nasce no canto, `cuboid()` da BOSL2 nasce centrado.** Escolha um jeito por arquivo.
- **`include` traz variáveis e roda o código; `use` traz só módulos e funções.**
- OpenSCAD não exporta STEP.

## Estrutura do arquivo

```scad
// Unidade: mm. Imprime com a face do perfil na mesa.
LARGURA = 80;     // [40:200]
PAREDE  = 2.4;    // [1.2:0.4:4]
FOLGA   = 0.2;    // por lado

altura_util = LARGURA * 0.6;          // derivado: nunca redigitado

module corpo() { ... }
module fenda(x) { ... }

difference() { corpo(); fenda(20); }
```

- Parâmetros no topo, com número literal: é o que vira controle deslizante no painel do OpenSCAD.
  `// [min:max]`, `// [min:passo:max]` ou `// [a, b, c]` logo depois do valor definem o controle; expressão não
  aparece no painel.
- Um módulo por parte; a montagem fica separada.
- `echo()` das medidas derivadas e `assert()` nas combinações impossíveis, com mensagem que a pessoa entende.
- Faça o perfil em 2D (`square`, `polygon`, `offset`) e use `linear_extrude`: é mais fácil de conferir do que
  somar caixas em 3D.

## Várias cores

Cada cor é um objeto no nível mais alto do arquivo. Exporte 3MF com `--enable lazy-union` para os objetos não
serem unidos; uma chamada de módulo une os filhos, então os objetos precisam estar soltos no topo.

## Biblioteca BOSL2

`include <BOSL2/std.scad>` dá roscas (`threaded_rod`), engrenagens, dobradiças, encaixe rabo de andorinha
(`dovetail`), caixa arredondada (`cuboid`), cilindro (`cyl`) e posicionamento por âncora. A folga dela (`$slop`)
é por lado e começa em zero: o valor certo, entre 0,10 e 0,20 mm, sai de um teste na sua impressora.
Confira se a biblioteca está instalada antes de usar.
