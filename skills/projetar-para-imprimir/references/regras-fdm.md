# Regras FDM com números

Para bico de 0,4 mm e camada de 0,2 mm. Onde os guias divergem, a tabela mostra o valor seguro e a faixa que aparece. O valor seguro funciona em qualquer impressora; o resto depende de teste.

## Paredes

| Regra | Seguro | Faixa |
|---|---|---|
| Parede em pé, mínimo que imprime | 0,8 mm (duas passadas) | 0,8 a 1,2 |
| Parede de peça que se usa | 1,2 mm | 1,2 a 2,4 |
| Parede solta de um lado (aba, borda de fenda) | 2 mm | |
| Piso ou teto deitado | 2 camadas (0,4 mm) | menos de uma camada não imprime |
| Menor detalhe | 2 larguras de bico (0,8 mm) | |
| Menor vão entre duas partes | 0,5 mm | |

- Espessura em múltiplo da largura do fio (0,4 / 0,8 / 1,2 / 1,6) imprime mais limpa.
- Aresta em ponta com menos de 45 graus de material sai arredondada: corte a ponta na parede mínima.
- Peça que leva força: 3 paredes, 4 camadas em cima e 4 embaixo. Gancho e suporte: 4 a 5 paredes.
- Uma parede a mais rende mais resistência do que 15 pontos a mais de preenchimento.

## Balanço

O ângulo aqui é medido **a partir da vertical**: 0 é parede em pé, 90 é teto reto. No OrcaSlicer o ajuste de
suporte mede a partir da horizontal, então "45 da vertical" lá é 45 também, mas "60 da vertical" é 30.

| Ângulo da vertical | O que esperar |
|---|---|
| até 45 graus | Imprime sem suporte em qualquer máquina |
| 45 a 60 graus | Costuma sair, com a face de baixo mais feia |
| 60 a 70 graus | Só com boa ventilação e camada fina; teste |
| acima de 70 graus | Suporte, ou mude o desenho |

Camada mais fina salva balanço: a 60 graus, camada de 0,20 mm deixa 23% do fio apoiado; camada de 0,12 mm,
54%.

## Ponte (teto reto entre dois apoios)

| Vão | O que esperar |
|---|---|
| até 5 mm | Sai sempre |
| 5 a 20 mm | Sai com ventilação normal |
| 20 a 50 mm | Sai com cuidado e a face de baixo cede um pouco |
| acima de 50 mm | Teste antes, ou ponha um apoio |

Verificadores automáticos param em 5 mm por segurança; máquinas bem ajustadas passam de 50 mm.

## Furos e pinos

- Menor furo: 1 mm, na vertical quando der.
- Menor pino: 2 mm para aguentar; 1 mm imprime, mas quebra.
- Furo vertical sai 0,1 a 0,2 mm menor que o desenho. Desenhe 0,2 mm maior, ou deixe o fatiador compensar
  (nunca os dois).
- Furo horizontal redondo até 10 mm; acima, gota ou teto reto.
- Canto interno onde passa força: raio de pelo menos metade da parede, mínimo de 1 mm.

## Primeira camada e mesa

- A primeira camada espalha 0,1 a 0,3 mm para os lados ("pé de elefante"). Chanfro de 0,5 mm a 45 graus na
  borda de baixo esconde. Arredondamento na borda de baixo é um balanço: não use.
- Compensação no fatiador: 0,1 a 0,2 mm por lado.
- Apoio pequeno para o tamanho da peça pede aba de 5 a 10 mm.
- Peça grande e chata em ABS ou ASA levanta os cantos: arredonde os cantos vistos de cima.
- Altura dos detalhes em múltiplo da camada: um degrau de 0,5 mm com camada de 0,2 sai com 0,4 ou 0,6.

## Resistência

- Entre camadas a peça tem de 50 a 90% da resistência ao longo delas, conforme o material. Conte com metade.
- Força e dobra no plano das camadas. Braço, gancho e trava deitados.
- Nervura com 0,6 vez a espessura da parede reforça sem marcar o outro lado.
- Preenchimento: 10 a 15% para enfeite, 15 a 25% para uso comum, 30 a 50% para carga. Acima de 60%, mais
  paredes rendem mais.

## Precisão

- Conte com erro de 0,1 a 0,2 mm no plano da mesa.
- Os erros se somam: espalhamento da base, compensação, canto arredondado pelo bico, encolhimento.
- Medida justa: imprima um pedaço de teste, meça com paquímetro e corrija o parâmetro.
