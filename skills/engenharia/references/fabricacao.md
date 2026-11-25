# Fabricação: usinagem, injeção e chapa

Os números de regra de desenho abaixo são regras práticas comuns de oficina e ferramentaria, não medidas pelo
Filuna. O fabricante de verdade pode pedir outros: pergunte antes de fechar o desenho.

## Como a análise mede

Pontos espalhados por igual na superfície (6.000 por padrão). Para cada ponto e cada direção, um raio sai da
face no sentido da ferramenta: se escapa da peça sem bater, a ferramenta chega ali. Faces quase paralelas ao
eixo contam como alcançadas pela lateral da fresa. A área é a soma dos pontos, então detalhe menor que o
espaço entre eles pode escapar.

## Usinagem CNC de 3 eixos

| Saída | O que é | O que fazer |
|---|---|---|
| `fixacoes` | Menor conjunto de lados de onde a fresa alcança tudo o que é alcançável | Cada fixação a mais custa tempo e alinhamento; 1 ou 2 é o bom |
| `area_sem_alcance_mm2` | Superfície que nenhum dos 6 lados alcança (rebaixo escondido, vazio interno) | Abra o rebaixo para um lado, divida a peça ou use 5 eixos |
| `cantos_internos_vivos_mm` | Comprimento de canto interno reto ao longo do eixo da fresa, por fixação | Fresa é redonda: dê raio maior que o da fresa (regra prática: 1/3 da profundidade) |
| `material_removido` | Parte do bloco bruto que vira cavaco | Acima de 80%, compare com outro processo ou bloco mais justo |

Regras de desenho que a conta não mede: bolsão com profundidade até 4 vezes a largura; parede de alumínio de
pelo menos 0,8 mm e de plástico 1,5 mm; furo com diâmetro de broca padrão; rosca com profundidade até 3 vezes
o diâmetro.

## Injeção plástica

| Saída | O que é | O que fazer |
|---|---|---|
| `eixo_de_extracao` | Eixo (X, Y ou Z) em que o molde abre com menos área presa | Desenhe pensando nele desde o início |
| `area_presa_mm2` | Área que fica presa nas duas metades do molde (rebaixo) | Gaveta no molde custa caro: prefira furo passante ou encaixe que abra no eixo |
| `area_sem_saida_mm2` | Parede paralela ao eixo, sem inclinação | Dê 1 grau de saída, 2 a 3 em textura |
| `paredes` | Espessura mínima, típica e 5% mais finas | Parede de 1 a 4 mm e o mais uniforme possível; nervura com 60% da parede |

Espessura desigual (a típica mais de 2 vezes a fina) faz a parte grossa encolher mais: afunda e empena.

## Chapa metálica

| Saída | O que é |
|---|---|
| `espessura_mm` e `espessura_uniforme` | Chapa tem uma espessura só; variação acima de 15% reprova |
| `area_planificada_cm2` | Volume dividido pela espessura: a área da chapa antes de dobrar |
| `peso_g` | Em aço, alumínio e inox |

Regras de desenho: raio interno de dobra pelo menos igual à espessura; furo a pelo menos 2 espessuras da
dobra; aba com pelo menos 4 espessuras de altura. A análise não acha dobras nem desenvolve a peça: a área
planificada é estimativa.
