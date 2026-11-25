# Ajustes do fatiador e multicor

Para bico de 0,4 mm. O perfil oficial da impressora já acerta quase tudo: mude só o que a peça pede, e diga por
quê.

## O que mudar e quando

| Ajuste | Padrão | Mude quando |
|---|---|---|
| Altura da camada | 0,20 mm | 0,12 para detalhe fino e balanço difícil; 0,28 para rascunho. Limite: 65% do bico para peça forte |
| Paredes | 2 | 3 para peça de uso; 4 a 5 para gancho e suporte |
| Camadas de cima e de baixo | 3 a 4 | 4 e 4 para peça que leva força |
| Preenchimento | 15% | 10 a 15 enfeite, 15 a 25 uso, 30 a 50 carga; acima disso, mais paredes |
| Padrão do preenchimento | grade | cúbico ou giroide para carga em várias direções; concêntrico para TPU |
| Suporte | desligado | árvore para forma orgânica (marca menos); normal para balanço reto de peça mecânica |
| Aba | desligada | 5 a 10 mm quando o apoio é pequeno ou o material levanta |
| Costura | alinhada | atrás, para esconder |
| Primeira camada | 15 a 25 mm/s | mais lenta e 5 a 10 °C mais quente se não gruda |

- Subir a altura da camada é o jeito limpo de ganhar tempo.
- Parede externa a 60 ou 70% da velocidade da interna melhora o acabamento sem custar muito tempo.
- Tempo mínimo por camada perto de 8 segundos em peça pequena; se a peça é fina e alta, imprima várias de uma
  vez para cada camada esfriar.
- Ao trocar o bico, refaça a conta de paredes: espessura dividida pela largura do fio.
- Trocar de impressora no fatiador troca o processo e o filamento junto, e escolher um perfil pode apagar
  ajustes não salvos. Ordem: filamento, depois processo, depois fatiar.

## Várias cores

**O que custa é o número de trocas, não o número de cores.** A cada troca a impressora purga o filamento
anterior. Um detalhe pequeno que atravessa cem camadas dá cem trocas; uma área grande em três camadas dá três.

- A purga é direcional: de preto para branco gasta muito mais do que de branco para preto. A matriz de purga tem
  uma entrada para cada par, N × N para N filamentos.
- A purga real é o valor da matriz vezes o multiplicador de purga.
- Mudar cor ou filamento recalcula a matriz: ajuste-a por último.
- Para gastar menos: purgar no preenchimento, baixar o multiplicador, estreitar a torre. Não purgue dentro de
  objetos: eles saem com a cor que estiver carregada.
- A torre de purga ocupa mesa: numa mesa de 256 mm sobram perto de 200 mm úteis.
- Sem troca automática de filamento, cada troca é uma parada manual.
- Materiais de temperaturas diferentes juntos (PETG com suporte de PLA) pedem autorização explícita no programa.

### No desenho

| Em vez de | Faça |
|---|---|
| Cor atravessando a peça inteira | Rebaixo raso de 0,4 a 0,6 mm preenchido com a outra cor |
| Peça em pé com detalhe colorido | Peça deitada, com as cores nas primeiras camadas |
| Seis cores numa peça só | Peças separadas por cor, encaixadas ou coladas |

### No arquivo

- Um objeto por cor dentro do mesmo 3MF, cada um ligado a um filamento.
- Um 3MF é um arquivo zip. O projeto guarda modelos e ajustes; o fatiado guarda também o G-code de cada mesa.
  Trocar o nome de um 3MF de malha para `.gcode.3mf` não o torna imprimível.
- A impressora casa o filamento pelo nome exato do tipo: "ASA" e "ASA-Aero" não são o mesmo.

## Conferir no G-code

No fim do arquivo ficam os ajustes usados. Confirme impressora, diâmetro do bico, tipo de filamento e as
temperaturas de bico e mesa antes de mandar imprimir.

Para saber qual filamento foi de fato usado: gramas divididos por (metros × 2,405 mm²) dá a densidade. Perto de
1,24 é PLA; 1,27, PETG; 1,05, ABS ou ASA.
