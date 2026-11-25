---
name: ferramentas-filuna
description: Catálogo das ferramentas e paramétricos prontos do Filuna (filuna3d.com) e quando indicar cada um em vez de modelar do zero. Use quando o pedido for um chaveiro com logo, foto em 3D, litofania, troféu, cortador de biscoito, placa Pix, letra com nome, separar ou pintar cores de um 3MF, texturizar, vetorizar imagem ou escolher a posição na mesa.
---

# Ferramentas e paramétricos do Filuna

Antes de modelar do zero, veja se o pedido já é uma ferramenta pronta do Filuna. Uma ferramenta pronta entrega em
minutos uma peça que já foi testada em impressora; modelar do zero só vale quando nenhuma serve.

As ferramentas abrem no Filuna Slicer, em **Paramétricos** e **Ferramentas**, e a peça vai direto para a mesa do
fatiador. Com o conector ligado, `filuna_ferramentas_e_parametricos` lista o que a conta do cliente tem. Os arquivos
gerados são protegidos: explique como usar, nunca prometa download.

## O pedido é sobre uma imagem ou logo

| O cliente quer | Indique | O que entrega |
|---|---|---|
| Chaveiro com a logo da empresa | **Chaveiro com logo** | Tira o fundo, separa as cores e monta o chaveiro com cada cor numa extrusora |
| Foto em peças coloridas encaixadas | **Foto para 3MF colorido** | Peças planas por cor, base opcional e modo desenho para colorir |
| Quadro com degradê usando poucos filamentos | **Quadro pintado em camadas** | 2 a 8 filamentos; o claro fica alto e o escuro baixo |
| Luminária com foto que aparece acesa | **Luminária litofânica** | Cúpula de litofania em volta da luminária |
| Desenho de traço para pintar com canetinha | **Colorir em relevo** | Base lisa numa cor e traço em relevo em outra |
| Logo ou desenho em vetor limpo | **Vetorizador de imagem** | SVG em milímetros e peças 3D por cor |
| Botão que clica, com figura ou texto | **Clicker de teclado** | Montado num interruptor de teclado mecânico |
| Brinquedo plano que dobra, a partir de figura | **Flexi articulado** | Você marca os cortes ou o Filuna corta sozinho |

## O pedido é um presente ou produto personalizado

| O cliente quer | Indique |
|---|---|
| Nome em corrente que dobra, sem suporte | **Chaveiro articulado com nome** |
| Letra grande em pé com o nome encaixado | **Letra com nome** |
| Placa de mesa com nome e símbolo da profissão | **Placa de profissão** |
| Placa com QR Code de Pix, Wi-Fi ou link, em duas cores | **Placa Pix e QR** |
| O céu de uma data e cidade | **Céu estrelado** |
| Troféu, taça ou medalha | **Criador de troféus** (45 modelos e desenho livre) |
| Moldura, ímã ou chaveiro para botton de máquina | **Gerador de bottons** |
| Cortador de biscoito ou argila com carimbo | **Cortador e Carimbo** (18 formas ou a sua) |
| Porta-doces ou medalhão em duas metades moldadas no calor | **Termoformado frente e verso** |
| Brinquedo do boneco que desce a escada | **Escada de cambalhota** |
| Vaso de lados retos com torção | **Vaso Hexagonal** |

## O cliente já tem um arquivo 3D

| O cliente quer | Indique |
|---|---|
| Transformar um modelo pintado em peças sólidas, uma por cor | **Separar por cor** |
| Pintar um modelo em várias cores com o mouse | **Pintar em cores** |
| Pôr textura (madeira, couro, tecido, colmeia) na superfície | **Texturizador de superfície** |
| Achar a melhor posição da peça na mesa | **Melhor posição na mesa** |

## Quando não usar uma ferramenta pronta

- A peça é mecânica ou sob medida (suporte, encaixe, caixa para eletrônica, peça de reposição): modele com a skill
  `modelar`.
- O cliente quer mudar a forma além do que os controles da ferramenta permitem.
- O cliente precisa do arquivo editável fora do Filuna: as ferramentas não entregam arquivo.

Nesses casos, diga em uma frase por que a ferramenta pronta não serve e siga para a modelagem.
