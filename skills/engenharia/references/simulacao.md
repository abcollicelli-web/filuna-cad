# Simulação estrutural com o CalculiX

## Como funciona

1. O gmsh enche a peça de tetraedros de 10 nós (do STEP direto, ou do STL reconstruindo as faces).
2. A face escolhida em `--fixar` fica presa nos três eixos.
3. A força total de `--forca` (newtons, FX,FY,FZ) é dividida por igual entre os nós da face de `--forca-em`.
4. O CalculiX resolve a estática linear e devolve deslocamento e tensão de von Mises.

As faces são as da caixa da peça: `xmin`, `xmax`, `ymin`, `ymax`, `zmin` (a base), `zmax` (o topo).

## Prova de que a conta está certa

Viga de aço de 100 × 10 × 10 mm presa numa ponta, 10 N para baixo na outra. A conta de livro dá flecha de
0,0195 mm e tensão de 6 MPa na raiz. O comando dá 0,0191 a 0,0196 mm e 5,4 a 6,6 MPa, conforme o tamanho dos
elementos. Esse caso é um dos testes do repositório.

## Como ler

| Saída | Significado |
|---|---|
| `deslocamento_max_mm` e onde | Quanto a peça entorta no pior ponto |
| `tensao_max_mpa` | O maior valor; num canto vivo ou bem onde a força encosta a malha exagera |
| `tensao_995_mpa` | O valor que 99,5% da peça não passa: use este para decidir |
| `fator_de_seguranca_995` | Limite do material dividido pela tensão 99,5% |

Fator pedido: 3 para peça impressa (fraca entre camadas e com preenchimento parcial) e 1,5 para metal. Se o
pico passa do limite e o 99,5% não, quase sempre é canto vivo: arredonde e simule de novo.

## Materiais

| Nome | Módulo (MPa) | Limite usado (MPa) |
|---|---|---|
| `pla` | 3500 | 40 |
| `petg` | 2000 | 35 |
| `abs`, `asa` | 2000 | 30 |
| `nylon` | 1500 | 40 |
| `aco` (1020) | 205000 | 250 |
| `aluminio` (6061-T6) | 69000 | 240 |

Os plásticos são valores de ficha técnica de peça maciça, arredondados para baixo. Peça impressa com 20% de
preenchimento é bem mais fraca: simule a parede e o preenchimento como sólido só para comparar versões, e
confirme imprimindo e testando.

## Erros comuns

- **Prender e carregar a mesma face:** a peça não se mexe e a tensão sai zero.
- **Força em newtons, não em quilos:** 1 kg pesa cerca de 9,8 N.
- **Elementos grandes demais** em peça fina: passe `--tamanho` com metade da parede mais fina.
