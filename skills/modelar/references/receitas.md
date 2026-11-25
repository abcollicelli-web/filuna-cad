# Receitas por situação

Números para impressão FDM com bico de 0,4 mm e camada de 0,2 mm. São pontos de partida: a folga certa depende da
impressora e do material, e só um teste impresso confirma. Onde os guias divergem, a faixa aparece inteira.
Toda folga aqui é **por lado**, salvo aviso.

## Folgas de encaixe

| O encaixe | Folga por lado | Observação |
|---|---|---|
| Entra sob pressão e fica | 0 a 0,1 mm | Não confie só no número: use nervuras de esmagamento ou parafuso de aperto |
| Justo, entra com a mão | 0,15 a 0,20 mm | Tampa que não cai sozinha |
| Desliza | 0,20 a 0,30 mm | Gaveta, trilho; trilho longo pede 0,25 ou mais |
| Folgado | 0,30 a 0,40 mm | Tampa solta, peça que gira livre |
| Impresso já montado (articulado) | 0,3 a 0,6 mm | Abaixo disso funde; há guias que só garantem a partir de 0,76 mm |

- PETG: some 0,1 mm nas folgas de deslizar.
- Encaixe sob pressão em plástico afrouxa em semanas. Para segurar de verdade: três ou mais nervuras finas que
  esmagam, um rasgo com parafuso de aperto, ou uma trava.
- Antes de imprimir a peça inteira, imprima um pedaço só com o encaixe.
- Se o fatiador já compensa furo e contorno, não some a folga duas vezes.

## Caixa com tampa

- Parede de 2,4 mm (três passadas de 0,8). Mínimo de 1,2 mm.
- Tampa por dentro: medida interna da caixa menos duas folgas justas. Aba de 1,6 a 3 mm, com a ponta chanfrada.
- São dois sólidos. Um só significa que a tampa fundiu na caixa.
- Componentes primeiro: posicione placa, conectores e furos, depois faça a casca em volta.
- Deixe abertura para tirar o suporte de dentro, se houver.

## Trava de encaixe (gancho flexível)

- Comprimento do braço: pelo menos 5 vezes a espessura na raiz.
- Raiz arredondada com raio de metade da espessura. Canto vivo na raiz é onde quebra.
- Deflexão de 0,5 a 1 mm; rampa de entrada de 30 graus.
- Face que destrava: 45 a 70 graus. Face de 90 graus não solta mais.
- **Imprima o braço deitado**, com as camadas ao longo dele. Braço em pé quebra na primeira vez.
- PLA aguenta pouca dobra (perto de 1%); PETG, o dobro. Trava que abre e fecha todo dia: PETG.

## Furos para parafuso

| Parafuso | Furo passante | Rebaixo da cabeça | Furo para inserto a quente |
|---|---|---|---|
| M2 | 2,4 | | 3,2 |
| M2,5 | 2,9 | | 3,6 a 4,0 |
| M3 | 3,4 | 6,5 × 3,4 de fundo | 4,0 a 4,4 |
| M4 | 4,5 | 8,0 × 4,4 de fundo | 5,6 a 5,7 |
| M5 | 5,5 | | 6,4 a 6,5 |
| M6 | 6,6 | | |

- Furo vertical sai 0,1 a 0,2 mm menor: os valores acima já contam com folga, não some de novo se o fatiador
  compensa.
- Furo horizontal: até 10 mm sai redondo; acima, use formato de gota ou teto reto.
- Inserto a quente: fundo do furo 1 mm maior que o inserto. A medida muda de fabricante para fabricante: peça o
  código do produto.
- Parafuso autoatarraxante de 3 mm direto no plástico: furo de 2,5 mm, 6 mm de profundidade útil.
- Torre do parafuso: diâmetro de pelo menos 2,5 vezes o furo, ligada à parede por nervuras.
- Distância do furo até a borda: duas vezes o diâmetro.
- Porca embutida: alojamento 0,2 mm maior.

## Roscas impressas

- Abaixo de M6 não se imprime rosca: use inserto ou parafuso autoatarraxante.
- Rosca impressa funciona com passo grosso (2 a 3 mm para diâmetros de 8 a 12 mm), perfil sem ponta e 0,2 a
  0,3 mm de folga por lado.
- A folga se faz afastando o perfil no raio, nunca mudando a escala: escala muda o passo e a rosca não entra.
- Imprima um pedaço curto das duas partes antes da peça inteira.

## Dobradiça e peça articulada impressa montada

- Pino de 3 mm ou mais; folga em volta do pino de 0,3 mm (faixa de 0,15 a 0,6); folga entre os elos de 0,4 mm.
- Cada elo é um sólido separado: conte os sólidos.
- Confira a interseção com a peça aberta, a 45 graus, a 90 graus e fechada.
- A primeira camada espalha e solda os elos: chanfre a base de cada um.
- Dobradiça de lâmina fina (0,3 a 0,5 mm): só em polipropileno ou PETG. Em PLA, quebra.

## Texto e relevo

- Letra em relevo ou rebaixo: 0,6 a 1 mm, sempre um número inteiro de camadas.
- Altura da letra: 5 mm ou mais. Traço da letra: pelo menos duas larguras de bico (0,8 mm).
- Fonte grossa e sem serifa lê melhor. Texto na face de cima ou na lateral; na face da mesa só espelhado e raso.
- Texto em outra cor: rebaixo de 0,4 a 0,6 mm preenchido por um sólido da outra cor, com a mesma fronteira.

## Peça em várias cores

- Um sólido por cor, encostados sem se atravessar, num 3MF.
- O custo vem do número de trocas por camada, não do número de cores. Um detalhe pequeno que atravessa muitas
  camadas custa mais que uma área grande em poucas camadas.
- Para gastar menos: ponha as cores nas primeiras ou nas últimas camadas (peça deitada), use rebaixo raso em vez
  de cor atravessando a peça, ou imprima as cores separadas e encaixe.

## Suporte de objeto (celular, fone, ferramenta)

- A peça apoia o objeto numa fenda ou num degrau e o encosta numa aresta ou face: calcule o ângulo pela linha
  entre os dois pontos de contato.
- Fenda 1 mm mais larga que o objeto com capa.
- Parede entre a fenda e a borda: pelo menos 2 mm, porque é ela que leva o tranco de pôr e tirar o objeto.
- Confira que o peso do objeto cai dentro da base nos ângulos de uso.
- Arredonde a aresta onde o objeto encosta.

## Ímãs e rolamentos

- Ímã colado: diâmetro e profundidade com 0,1 a 0,2 mm a mais.
- Rolamento sob pressão: diâmetro externo com 0 a 0,1 mm a mais; para entrar com a mão, 0,2 mm.

## Peça maior que a mesa

Divida com encaixe rabo de andorinha (ângulo de 8 a 14 graus, 0,15 mm de folga) ou com pino e rasgo: um furo
redondo e um rasgo alinham sem travar. Faça uma chave assimétrica para as partes só montarem do jeito certo.

## Engrenagens

Folga entre dentes de 0,1 mm; distância entre eixos calculada pelo módulo e pelo número de dentes. Para uso
contínuo, náilon; PLA gasta. Imprima deitada.
