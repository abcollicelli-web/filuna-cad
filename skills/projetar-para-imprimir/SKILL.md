---
name: projetar-para-imprimir
description: Regras de projeto para impressão 3D FDM com números - posição na mesa, parede mínima, balanço, ponte, furos, primeira camada, resistência pela direção das camadas e escolha de material. Use ao desenhar ou revisar qualquer peça que vai ser impressa, ao decidir como deitar a peça na mesa, ou quando perguntarem se uma peça imprime bem, se precisa de suporte ou qual material usar.
---

# Projetar para imprimir (FDM)

A impressora empilha fios de plástico de baixo para cima. Quase toda regra daqui sai disso: o fio precisa de algo
embaixo, a peça é mais fraca entre uma camada e outra, e a primeira camada decide se o resto dá certo.

## As cinco decisões, nesta ordem

1. **Posição na mesa.** A maior face plana para baixo (`python -m filuna_cad orientar` compara as seis). É a decisão que mais muda suporte, tempo e resistência,
   então ela vem antes do desenho dos detalhes.
2. **Direção da força.** A peça aguenta cerca de metade entre camadas do que aguenta ao longo delas. Gancho,
   trava e braço imprimem deitados, com a força correndo ao longo do fio.
3. **Nada no ar.** Inclinação de até 45 graus imprime sozinha. Teto reto vira chanfro, arco ou ponte curta.
4. **Paredes que existem.** Abaixo de duas passadas do bico a parede não sai; abaixo de 2 mm ela quebra na mão
   se estiver solta.
5. **Primeira camada.** Bastante área na mesa e chanfro na borda de baixo.

Os números de cada uma estão em [Regras FDM](references/regras-fdm.md). A escolha de material está em
[Materiais](references/materiais.md).

## Como revisar uma peça

1. Rode a validação (skill `validar`): ela mede malha, apoio, balanço, parede e estabilidade.
2. Olhe o que ela não mede: direção das camadas em relação à força, furos horizontais, texto, folgas de encaixe,
   pontes, cantos vivos onde a peça é carregada.
3. Para cada problema, proponha a mudança de desenho antes de propor suporte. Suporte custa plástico, tempo e
   deixa marca; uma mudança de 45 graus no desenho costuma resolver de graça.
4. Diga a posição de impressão e os ajustes do fatiador que a peça pede (paredes, preenchimento, aba, suporte).

## O que o desenho resolve sem suporte

| Problema | Solução no desenho |
|---|---|
| Teto reto no ar | Chanfro de 45 graus, arco, ou ponte curta entre dois apoios |
| Furo horizontal grande | Formato de gota ou teto reto no alto do furo |
| Saliência lateral | Apoiar numa rampa de 45 graus até o corpo |
| Peça alta e fina que balança | Alargar a base ou deitar a peça |
| Borda de baixo que espalha | Chanfro de 0,5 mm (nunca arredondamento: ele é um balanço) |
| Canto que levanta da mesa | Canto arredondado visto de cima, e aba no fatiador |
| Parede fina solta | Engrossar, ligar a outra parede com nervura, ou encurtar |

## O que dizer e o que não dizer

- Limites de balanço e ponte variam com a impressora, o material e a ventilação. Os números daqui são
  conservadores; uma máquina bem ajustada faz mais. Diga que é ponto de partida.
- Suporte, tempo e gramas de verdade só saem do fatiador.
- Resistência só se prova imprimindo e forçando a peça. Conta de resistência é estimativa.
