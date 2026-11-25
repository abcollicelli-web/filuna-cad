---
name: validar
description: Confere com números se uma peça 3D (STL, 3MF ou OBJ) imprime bem - malha fechada, apoio na mesa, balanço, espessura de parede, estabilidade e se cabe na impressora - acha a melhor posição na mesa, grava uma folha de vistas com corte, e mede se duas peças são iguais ou se a peça bate com uma imagem de referência (raio-x). Use depois de modelar ou mudar qualquer peça, antes de fatiar, ou quando pedirem para validar, conferir, dar nota, escolher a posição de impressão ou comparar modelos.
---

# Validar uma peça

A validação responde com medida o que o olho não responde: a malha fecha, a peça apoia, a parede existe. Rode
depois de cada mudança de geometria e antes de fatiar.

## Preparar

```bash
pip install "git+https://github.com/abcollicelli-web/filuna-cad#subdirectory=ferramentas"
```

## Validar para impressão

```bash
python -m filuna_cad validar peca.stl --mesa 256x256x256
python -m filuna_cad validar peca.3mf --json
```

A peça é conferida **na posição em que está no arquivo**, com Z para cima e apoiada no ponto mais baixo. Para
outra posição, gire a peça no modelo e valide de novo.

```text
APROVADA  nota 92/100  suporte.stl
  malha: fechada, 136 triângulos, 520.972 cm³, [160.0, 110.0, 80.0] mm
  mesa: apoio 6512.2 mm², balanço 0.0 mm²
  parede: mínima 1.18 mm, 5% abaixo de 8.38 mm
  [aviso] Parede de 1.18 mm em [94.0, 43.92, 46.01]: imprime, mas é frágil se ficar solta.
```

| Medida | Erro (reprova) | Aviso |
|---|---|---|
| Malha | Aberta ou sem volume válido | Mais de uma casca |
| Mesa | Não cabe na impressora informada | |
| Apoio | Menos de 20 mm² na mesa | Apoio menor que 15% da sombra da peça |
| Balanço | | Faces mais deitadas que 45 graus, fora da mesa |
| Parede | Menor que 0,8 mm | Menor que 2 mm |
| Estabilidade | Centro de massa fora do apoio | |

A nota é 100 menos 25 por erro e 8 por aviso. O comando devolve código 1 quando há erro, para servir em
automação. Com `--json` sai tudo, inclusive a posição de cada achado.

## Como ler

- **Parede mínima com posição:** vá ao ponto indicado e veja se a parede está solta ou ligada dos dois lados.
  Ligada, 1,2 mm aguenta; solta, engrosse para 2 mm.
- **"5% abaixo de":** se a mínima é pequena e esse valor é grande, o problema é um ponto só.
- **Mais de uma casca:** certo em peça articulada ou multicor, errado em peça única.
- **Balanço:** é a área que pede suporte na posição atual. Antes de aceitar suporte, tente outra posição.

## O que a validação não prova

- **Não fatia.** Tempo, gramas e suporte reais só saem do fatiador (skill `fatiar-e-imprimir`).
- **A parede é medida por amostragem** (4.000 raios por padrão). Um ponto fino menor que o espaço entre os raios
  pode escapar: aumente `--amostras` em peça com detalhe pequeno.
- **Quina não conta como parede fina.** Numa aresta em ponta a espessura cai a zero sem ser defeito, então só
  entram paredes de faces quase paralelas. Aresta em ponta de menos de 45 graus fica por sua conta.
- **Não mede** ponte, furo horizontal, folga de encaixe, legibilidade de texto nem resistência.
- **Aprovada quer dizer que não achou erro no que mede.** Não quer dizer que a peça funciona.

## Qual é a melhor posição na mesa?

```bash
python -m filuna_cad orientar peca.stl
```

Compara as seis posições (cada face para baixo) por balanço, apoio e altura, e avisa a que tomba:

```text
Melhor posição: como está (Z- na mesa)
  como está (Z- na mesa)                 apoio    6510.6 mm²  balanço       0.0 mm²  altura   80.0 mm
  fundo na mesa (Y+ na mesa)             apoio   11200.0 mm²  balanço    5920.0 mm²  altura  110.0 mm
  lado esquerdo na mesa (X- na mesa)     apoio    1280.0 mm²  balanço   11831.4 mm²  altura  160.0 mm  TOMBA
```

Com `--json` vem o giro que leva a peça a cada posição. A conta não sabe de onde vem a força nem qual face
precisa ficar bonita: a melhor posição para imprimir pode não ser a melhor para a peça aguentar. Decida com a
skill `projetar-para-imprimir`.

## Ver a peça sem abrir programa

```bash
python -m filuna_cad vistas peca.stl folha.png
```

Grava uma folha com perspectiva, frente, lado, cima e um corte na meia altura, com as medidas de cada vista.
O corte mostra paredes e vazios que as vistas de fora escondem. Olhe a folha depois de cada mudança de
geometria: "gerou sem erro" não é "ficou certo".

## As duas peças são a mesma?

```bash
python -m filuna_cad comparar a.stl b.stl
```

Devolve a sobreposição de volume: 1,0 é a mesma forma na mesma posição. Serve para provar que uma peça refeita
em outro motor ficou igual, e para saber quanto uma versão mudou em relação à anterior. As duas malhas precisam
ser fechadas.

## A peça bate com a referência?

```bash
python -m filuna_cad raio-x peca.stl referencia.png --vista frente --saida raio_x.png
```

Devolve a semelhança da silhueta de 0 a 1 e uma imagem onde vermelho é o que falta na peça e azul é o que
sobra. Os detalhes e os limites estão na referência "A partir de imagem" da skill `modelar`.

## Conferir que a validação funciona

Uma conferência só merece confiança depois de falhar numa peça com defeito plantado. Os testes do repositório
fazem isso: malha com face arrancada, parede de 0,5 mm, balanço em T, peça maior que a mesa.

```bash
cd ferramentas && python -m pytest -q
```
