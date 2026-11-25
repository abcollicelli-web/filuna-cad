---
name: modelar
description: Modela uma peça 3D para impressão FDM a partir de texto, medidas ou imagem de referência, escolhendo o motor certo (OpenSCAD, Manifold e trimesh em Python, build123d, three.js ou Blender), escrevendo o modelo por código e conferindo com números antes de entregar. Use quando pedirem para criar, desenhar, modelar, ajustar ou refazer uma peça, suporte, caixa, encaixe, chaveiro, placa ou qualquer objeto para imprimir.
---

# Modelar uma peça para imprimir

Uma peça só está pronta quando três coisas são verdade: ela faz o que a pessoa pediu, ela imprime, e você mediu
as duas coisas em vez de supor. Quem recebe a peça vai gastar horas e filamento nela.

## Comece pelo pedido

| O pedido | Comece por | Referência |
|---|---|---|
| Já existe pronto no Filuna (chaveiro com logo, litofania, troféu, placa Pix...) | A ferramenta pronta | skill `ferramentas-filuna` |
| Peça mecânica, suporte, caixa, encaixe | Código paramétrico | [Escolher o motor](references/escolher-motor.md) |
| Encaixe, tampa, parafuso, dobradiça, rosca, texto | A receita com os números | [Receitas por situação](references/receitas.md) |
| Copiar uma foto ou desenho | Decompor a imagem e confirmar com a pessoa | [A partir de imagem](references/a-partir-de-imagem.md) |
| Forma orgânica, escultura, textura | Blender | [Blender](references/blender.md) |
| Mudar um STL que já existe | Importar a malha e cortar ou somar em volta | [Python de malha](references/python-malha.md) |

## Antes de escrever código

1. **Pergunte só o que muda o resultado**, de uma vez, no máximo cinco perguntas: o que a peça segura ou encaixa
   e as medidas disso, tamanho máximo, de onde vem a força, qual impressora e material, se pode ser em mais de
   uma parte. O que a pessoa não souber, assuma, e diga o que assumiu.
2. **Medida de peça comprada vem da pessoa ou da ficha técnica, nunca da memória.** Parafuso, ímã, rolamento,
   celular, placa eletrônica: peça a medida ou o código do produto.
3. **Não enfeite o pedido.** Um suporte é um suporte: não acrescente furos, simetrias e detalhes que ninguém pediu.
4. **Monte a tabela de medidas antes do código.** Cada eixo fecha uma conta: largura total = soma das partes.
   Se a conta não fecha no papel, não fecha na peça.
5. **Decida a posição de impressão agora**, não no fim: a maior face plana na mesa, a força correndo ao longo das
   camadas, nenhum teto reto no ar. As regras estão na skill `projetar-para-imprimir`.

## Escreva o modelo

- **Um bloco de parâmetros no topo**, com números literais e unidade no comentário. Tudo o mais é derivado deles:
  nenhum número digitado duas vezes.
- **Parâmetros independentes.** De largura externa, largura interna e parede, a pessoa escolhe duas; a terceira é
  conta. Parede e parafuso não crescem junto com o tamanho da peça.
- **Do grosso para o fino:** volume principal, depois o que dá função (furos, fendas, encaixes), depois detalhes,
  e arredondamentos por último.
- **Cortes atravessam, uniões se enterram.** Quem corta passa pelo menos 0,1 mm de cada lado; quem se junta entra
  pelo menos 0,1 mm no outro. Face encostando em face gera malha aberta.
- **Uma parte impressa = um sólido.** Conte os sólidos: um a menos significa que duas partes fundiram, um a mais
  significa que sobrou um pedaço solto.
- **Uma mudança por vez.** Guarde a última versão que passou; nunca sobrescreva a versão que a pessoa já viu.

## Confira, nesta ordem

Número primeiro, imagem depois. A imagem engana: uma peça achatada parece certa de cima.

1. **O motor terminou sem erro e sem aviso**, e o arquivo existe e não está vazio. O OpenSCAD pode sair com
   código zero mesmo com erro: leia a saída.
2. **Medidas e volume** batem com a tabela.
3. **Validação de impressão** (skill `validar`): malha fechada, apoio, balanço, parede mínima, estabilidade.
4. **Corte no meio** da peça, para ver o interior e as espessuras.
5. **Imagens:** a folha de vistas (`python -m filuna_cad vistas`) dá perspectiva, frente, lado, cima e corte.
   Olhe também por trás.
6. **Encaixes:** meça a folga em cada par e, se a peça se mexe, nas duas pontas do curso e no meio. A folga
   certa da impressora sai do cupom de folga (skill `calibrar`), não de tabela.

Cada conferência que não pôde ser feita fica dita como "não conferi", nunca como aprovada.

## Quando algo não sai

- Três tentativas no mesmo detalhe significam que o caminho está errado: mude a forma de construir.
- Arredondamento que falha é limite do motor: reduza o raio e diga o valor que ficou.
- Nunca empilhe um remendo em cima de um erro, nunca apague o detalhe para o erro sumir, nunca mude a escala ou
  a impressora para a validação passar.

## Entregue

Diga em poucas linhas: o que a peça é e as medidas principais, a posição de impressão, o que foi conferido com
o resultado, o que **não** foi conferido, o que foi assumido, e a sugestão de camada, paredes, preenchimento e
suporte. Nada impresso ainda é nada testado: resistência e encaixe só se provam na impressora.
